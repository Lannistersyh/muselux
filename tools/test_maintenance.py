"""Regression checks for recurring content updates; all mutations use temp folders."""
from pathlib import Path
from contextlib import redirect_stdout, ExitStack
from unittest.mock import patch
import copy, io, json, shutil, tempfile, unittest
import apply_style_edit as style
import apply_bag_yearbook as bags
import apply_jewel_yearbooks as jewels
import bag_yearbook, brand_catalog, generate

ROOT=Path(__file__).resolve().parents[1]


class MaintenanceTests(unittest.TestCase):
    def fixture(self):
        temporary=tempfile.TemporaryDirectory(prefix='muselux-regression-')
        self.addCleanup(temporary.cleanup)
        root=Path(temporary.name)
        (root/'tools/research').mkdir(parents=True)
        (root/'reports').mkdir()
        shutil.copyfile(ROOT/'tools/content.json',root/'tools/content.json')
        for name in style.SOURCES+list(bags.SOURCES)+list(jewels.SOURCES):
            shutil.copyfile(ROOT/'tools/research'/name,root/'tools/research'/name)
        data=json.loads((root/'tools/content.json').read_text())
        for product in brand_catalog.products(data):
            if product.get('image'):
                target=root/product['image'];target.parent.mkdir(parents=True,exist_ok=True);target.touch()
        return root

    def run_merge(self,module,root):
        with ExitStack() as stack:
            stack.enter_context(patch.object(module,'ROOT',root))
            if hasattr(module,'DATA'):stack.enter_context(patch.object(module,'DATA',root/'tools/content.json'))
            with redirect_stdout(io.StringIO()):module.main()

    def research(self,root,name,mutate):
        path=root/'tools/research'/name
        data=json.loads(path.read_text());mutate(data)
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

    def test_source_review_dates_survive_all_mergers(self):
        root=self.fixture();expected={}
        for name in style.SOURCES+list(bags.SOURCES)+list(jewels.SOURCES):
            data=json.loads((root/'tools/research'/name).read_text())
            products=data.get('products',[])+[x for key in ('years','necklaceYears','jewelryYears') for y in data.get(key,[]) for x in y['entries']]
            expected.update({x['id']:x['checkedAt'] for x in products})
        for module in (style,bags,jewels):self.run_merge(module,root)
        actual=json.loads((root/'tools/content.json').read_text())
        self.assertEqual({x['id']:x['checkedAt'] for x in brand_catalog.products(actual) if x.get('image')},expected)
        once=(root/'tools/content.json').read_bytes()
        for module in (style,bags,jewels):self.run_merge(module,root)
        self.assertEqual((root/'tools/content.json').read_bytes(),once)

    def test_fresh_core_date_and_fractional_usd(self):
        root=self.fixture()
        def change(data):data['products'][0].update(checkedAt='2026-10-23',priceUSD=1234.56)
        self.research(root,style.SOURCES[0],change)
        self.run_merge(style,root)
        product=next(x for x in json.loads((root/'tools/content.json').read_text())['items'] if x.get('priceUSD')==1234.56)
        self.assertIn('23 October 2026',product['priceContextEn'])
        self.assertEqual(generate.usd(product['priceUSD']),'US$1,234.56')
        self.assertIn('US$1,234.56',product['priceRange'])
        self.assertIn('23 October 2026',generate.price_note([product]))

    def test_replace_core_product_removes_old_brand_reference(self):
        root=self.fixture()
        path=root/'tools/research'/style.SOURCES[0]
        data=json.loads(path.read_text());old=data['products'][0]['id']
        data['products'][0]['id']='replacement-product';path.write_text(json.dumps(data))
        self.run_merge(style,root)
        merged=json.loads((root/'tools/content.json').read_text())
        self.assertNotIn(old,{x['id'] for x in merged['items']})
        self.assertFalse(any(old in b['classicItems'] for b in merged['brands']))
        self.assertTrue(any('replacement-product' in b['classicItems'] for b in merged['brands']))

    def test_classic_id_collision_is_rejected(self):
        root=self.fixture()
        self.research(root,style.SOURCES[0],lambda d:d['products'][0].update(id='birkin'))
        with self.assertRaisesRegex(AssertionError,'collision'):self.run_merge(style,root)

    def test_fifth_editorial_slot_preserves_existing_products(self):
        root=self.fixture()
        def fifth(data):
            watches=[x for x in data['products'] if x['category']=='watches'][:4]
            data['products']=[x for x in data['products'] if x['category']!='watches']+watches
            product=copy.deepcopy(next(x for x in data['products'] if x['category']=='watches'))
            product['id']='fifth-watch';data['products'].append(product)
        self.research(root,'watches-fragrance.json',fifth)
        self.run_merge(style,root)
        data=json.loads((root/'tools/content.json').read_text())
        self.assertEqual(sum(x.get('styleEdit',False) and x['category']=='watches' for x in data['items']),5)
        def sixth(data):
            product=copy.deepcopy(data['products'][-1]);product['id']='sixth-watch';data['products'].append(product)
        self.research(root,'watches-fragrance.json',sixth)
        with self.assertRaisesRegex(AssertionError,'three to five'):self.run_merge(style,root)

    def test_new_yearbook_cutoff_is_kept(self):
        root=self.fixture()
        def change(data):
            for y in data['years']:
                y['cutoff']='2026-10-23'
                for x in y['entries']:x['checkedAt']='2026-10-23'
        self.research(root,'bag-years-2026.json',change)
        self.run_merge(bags,root)
        data=json.loads((root/'tools/content.json').read_text())
        self.assertEqual(data['bagYears'][-1]['cutoff'],'2026-10-23')
        captured={}
        bag_yearbook.render(data,lambda path,title,desc,content,*args,**kw:captured.update({path:content}),{b['id']:b for b in data['brands']})
        self.assertIn('The 2026 edit covers evidence available by 23 October 2026.',captured['bags-by-year.html'])

    def test_future_evidence_and_price_are_rejected(self):
        for module in (bags,jewels):
            with self.subTest(module=module.__name__):
                year={'year':2026,'yearToDate':True,'cutoff':'2026-10-24','entries':[{'id':'test','checkedAt':'2026-10-23'}]}
                with self.assertRaises(AssertionError):module.evidence_cutoff(year)
                with self.assertRaises(AssertionError):module.validate_sources([{'publishedAt':'2026-10-24'}],module.iso_date('2026-10-23','test'),'test')
        with self.assertRaises(AssertionError):style.validate_price_dates({'id':'test','checkedAt':'2026-10-23','priceAsOf':'2026-10-24'})

    def test_retrospective_evidence_remains_valid(self):
        for module in (bags,jewels):
            year={'year':2024,'entries':[{'id':'test','checkedAt':'2026-10-19'}]}
            cutoff=module.evidence_cutoff(year)
            module.validate_sources([{'publishedAt':'2025-05-20'}],cutoff,'2024 retrospective')

    def test_visible_article_date_matches_metadata(self):
        article=generate.D['articles'][0];captured={}
        with patch.dict(article,{'date':'2026-10-23'}),patch.object(generate,'page',lambda path,title,desc,content,*args,**kw:captured.update({path:content})):
            fragment=generate.card(article)
            generate.detailpages()
        marker='<time datetime="2026-10-23">2026.10.23</time>'
        self.assertIn(marker,fragment)
        self.assertIn(marker,captured['mag/'+article['id']+'.html'])

    def test_structured_data_cannot_break_out_of_script(self):
        value={'name':'A </script><script>alert(1)</script> bag'}
        encoded=generate.json_script(value)
        self.assertNotIn('<',encoded)
        self.assertEqual(json.loads(encoded),value)

    def test_only_retired_generated_pages_are_removed(self):
        temporary=tempfile.TemporaryDirectory(prefix='muselux-retirement-');self.addCleanup(temporary.cleanup)
        root=Path(temporary.name);(root/'item').mkdir()
        old=root/'item/old.html';keep=root/'item/current.html';custom=root/'custom.html'
        for path in (old,keep,custom):path.write_text('content')
        generate.retire_pages(['item/old.html','item/current.html'],['item/current.html'],root)
        self.assertFalse(old.exists());self.assertTrue(keep.exists());self.assertTrue(custom.exists())
        with self.assertRaises(ValueError):generate.retire_pages(['../outside.html'],[],root)
        self.assertTrue(custom.exists())


if __name__=='__main__':unittest.main()
