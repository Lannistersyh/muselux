"""Video-grounded style observations and editorial links to the existing catalog."""
from pathlib import Path
from html import escape
from urllib.parse import urlsplit
import json,re
import brand_catalog
from bag_yearbook import price_text,date_label

ROOT=Path(__file__).resolve().parents[1]
e=lambda value:escape(str(value),quote=True)


def load(data,root=ROOT):
    config=json.loads((root/'tools/womens_styles.json').read_text())
    catalog={x['id']:x for x in brand_catalog.products(data)}
    brands={b['id']:b for b in data['brands']}
    styles=config['styles'];seen=set()
    if not 3<=len(styles)<=5:raise ValueError('Style atlas needs three to five observed styles')
    for style in styles:
        key=style['id']
        if key in seen or not re.fullmatch(r'[a-z][a-z0-9-]*',key):raise ValueError('Duplicate or unsafe style ID')
        seen.add(key)
        if len(style['observations'])<3:raise ValueError('Style needs three timed observations')
        if not 3<=len(style['products'])<=5:raise ValueError('Style needs three to five catalog suggestions')
        if len({x['id'] for x in style['products']})!=len(style['products']):raise ValueError('Duplicate style suggestion')
        for observation in style['observations']:
            if not 0<=observation['time']<config['sourceVideo']['durationSeconds']:raise ValueError('Observation outside source video')
        for suggestion in style['products']:
            product=catalog[suggestion['id']]
            if not product.get('image') or product.get('priceUSD') is None:raise ValueError('Style suggestion needs a pictured priced variant')
        if len(style['brandMatches'])<3:raise ValueError('Style needs three sourced brand matches')
        for match in style['brandMatches']:
            if match['brand'] not in brands:raise ValueError('Style brand absent from catalog')
            if urlsplit(match['source']).scheme!='https':raise ValueError('Style brand source must be HTTPS')
        frame=style['frame']
        if not 0<=frame['timestampSeconds']<config['sourceVideo']['durationSeconds']:raise ValueError('Frame outside source video')
        if not (root/frame['path']).is_file():raise ValueError('Missing style frame')
        if frame.get('originalPath') and not (root/frame['originalPath']).is_file():raise ValueError('Missing original style screenshot')
        for variant in frame.get('variants',[]):
            if not (root/variant['path']).is_file():raise ValueError('Missing responsive style frame')
    photography=config.get('photography',{})
    photos=photography.get('photos',[])
    if len({p['id'] for p in photos})!=len(photos):raise ValueError('Duplicate photography ID')
    if len({p['sourceSha256'] for p in photos})!=len(photos):raise ValueError('Duplicate photography source image')
    for photo in photos:
        if photo['style'] not in seen:raise ValueError('Unknown photography style')
        if photo['licenseStatus']!='platform-license-permits-website-use':raise ValueError('Photography needs a verified website-use license')
        if min(photo['sourceWidth'],photo['sourceHeight'])<2000:raise ValueError('Photography source resolution is too small')
        if not photo['photographer'] or any(urlsplit(photo[k]).scheme!='https' for k in ('source','imageSource','licenseURL')):raise ValueError('Photography needs author, source and license')
        for variant in photo['variants']:
            path=variant['path']
            if not path.startswith('assets/img/style-photography/') or '..' in Path(path).parts or not (root/path).is_file():raise ValueError('Missing or unsafe photography asset')
    for creator in photography.get('creators',[]):
        if creator['licenseStatus']!='copyright-reserved-link-only' or urlsplit(creator['source']).scheme!='https':raise ValueError('Creator work must link to its original source')
        if not set(creator['styles'])<=seen:raise ValueError('Unknown creator style')
    return {'config':config,'catalog':catalog,'brands':brands}


def timestamp(seconds):
    return f'{int(seconds)//60:02}:{int(seconds)%60:02}'


def runtime(atlas):
    rows=[]
    for s in atlas['config']['styles']:
        names=[atlas['brands'][m['brand']]['name'] for m in s['brandMatches']]
        rows.append({'id':s['id'],'name':s['name'],'nameZh':s['nameZh'],'oneLiner':s['tagline'],
                     'image':s['frame']['path'],'categories':s['categories'],'brandNames':' '.join(names),
                     'keywords':s['keywords'],'styleGuide':True})
    return rows


def responsive_image(image,variants,prefix,alt,sizes,loading='lazy'):
    srcset=', '.join(prefix+e(v['path'])+' '+str(v['width'])+'w' for v in variants)
    responsive=f' srcset="{srcset}" sizes="{e(sizes)}"' if variants else ''
    priority=' fetchpriority="high"' if loading=='eager' else ''
    return f'<img src="{prefix}{e(image["path"])}"{responsive} width="{image["width"]}" height="{image["height"]}" alt="{e(alt)}" loading="{loading}" decoding="async"{priority}>'


def figure(style,prefix=''):
    frame=style['frame']
    image=responsive_image(frame,frame.get('variants',[]),prefix,'原视频'+timestamp(frame['timestampSeconds'])+'画面：'+style['nameZh']+'造型，引用用于下方穿搭评论','(max-width:768px) calc(100vw - 40px), 620px','eager')
    original=frame.get('originalPath',frame['path'])
    return f'''<figure class="style-source-frame"><a class="style-frame-image" href="{prefix}{e(original)}" target="_blank" rel="noopener" aria-label="查看{e(style['nameZh'])}原始高清截图">{image}</a><figcaption><span>4K画面引用 · {timestamp(frame['timestampSeconds'])}</span><a href="{e(frame['source'])}" target="_blank" rel="noopener">{e(frame['credit'])} ↗</a><a class="style-original-link" href="{prefix}{e(original)}" target="_blank" rel="noopener">查看原始截图 · {frame['width']}×{frame['height']} ↗</a></figcaption></figure>'''


def card(style,prefix=''):
    frame=style['frame']
    image=responsive_image(frame,frame.get('variants',[]),prefix,style['nameZh']+'的原视频画面引用','(max-width:768px) calc(100vw - 40px), 410px')
    return f'''<article class="style-atlas-card"><a href="{prefix}style/{style['id']}.html">{image}<div><p class="eyebrow">{e(style['name'])}</p><h3>{e(style['nameZh'])} <span>↗</span></h3><p>{e(style['tagline'])}</p><span class="style-card-source">视频标签：{e(style['videoLabel'])} · 4K截图</span></div></a></article>'''


def photography_section(atlas,style=None,prefix=''):
    photography=atlas['config'].get('photography',{})
    photos=[p for p in photography.get('photos',[]) if style is None or p['style']==style['id']]
    if not photos:return ''
    names={s['id']:s['nameZh'] for s in atlas['config']['styles']}
    cards=[]
    for photo in photos:
        image=responsive_image(photo['image'],photo['variants'],prefix,photo['alt'],'(max-width:768px) calc(100vw - 40px), 600px' if style else '(max-width:768px) calc(100vw - 40px), 410px')
        more=f'<a class="text-link" href="{prefix}style/{photo["style"]}.html#photography">放进{e(names[photo["style"]])}看一看 ↗</a>' if style is None else ''
        cards.append(f'''<figure class="style-photo-study"><a class="style-photo-image" href="{prefix}{e(photo['image']['path'])}" target="_blank" rel="noopener" aria-label="放大摄影作品：{e(photo['title'])}">{image}</a><figcaption><p class="eyebrow rose-text">{e(photo['setting'])}</p><h3>{e(photo['title'])}</h3><p>{e(photo['captionZh'])}</p><p lang="en">{e(photo['captionEn'])}</p><div class="style-photo-credit"><a href="{e(photo['source'])}" target="_blank" rel="noopener">Photo: {e(photo['photographer'])} ↗</a><span>原图 {photo['sourceWidth']}×{photo['sourceHeight']}</span><a href="{e(photo['licenseURL'])}" target="_blank" rel="noopener">{e(photo['licenseName'])}</a></div>{more}</figcaption></figure>''')
    intro='两幅摄影，观察剪裁、配饰与背景怎样一起形成风格。照片按可见设计细节选入，衣物与首饰不作品牌鉴定。' if style else photography['intro']
    return f'''<section class="style-photography style-section" id="photography"><p class="eyebrow rose-text">STYLE IN FOCUS / A WIDER FRAME</p><h2>让穿搭，也成为一幅画</h2><p class="style-section-note">{e(intro)}</p><div class="style-photo-grid {'style-photo-grid-pair' if style else ''}">{''.join(cards)}</div></section>'''


def creator_section(atlas,style=None):
    creators=[c for c in atlas['config'].get('photography',{}).get('creators',[]) if style is None or style['id'] in c['styles']]
    if not creators:return ''
    cards=[]
    for creator in creators:
        date=('原文 '+creator['publishedAt']+' · ') if creator.get('publishedAt') else ''
        cards.append(f'''<article class="style-creator-card"><p class="eyebrow">{e(creator['role'])}</p><h3>{e(creator['name'])}</h3><h4>{e(creator['title'])}</h4><p>{e(creator['captionZh'])}</p><a class="text-link" href="{e(creator['source'])}" target="_blank" rel="noopener">到作者原站看完整作品 ↗</a><span>{e(date)}原作图片 {creator['sourceImageWidth']}×{creator['sourceImageHeight']}</span></article>''')
    return f'''<section class="style-section style-creator-index"><p class="eyebrow rose-text">CREATORS / PHOTOGRAPHERS / PLACES</p><h2>跟着创作者，继续看</h2><p class="style-section-note">从穿搭作者的完整造型，到摄影师如何选择空间。以下入口直达原站作品。</p><div class="style-creator-grid">{''.join(cards)}</div></section>'''


def teaser(atlas,prefix=''):
    styles=atlas['config']['styles']
    return f'''<section class="style-atlas-teaser"><header><p class="eyebrow rose-text">THE STYLE ATLAS / FROM LOOK TO DETAIL</p><h2>女性风格指南</h2><p>从一段穿搭视频出发，拆开轮廓与细节，再找到适合的品牌和单品。</p><a class="text-link" href="{prefix}womens-style.html">浏览三种风格与搭配 ↗</a></header><div class="style-atlas-grid">{''.join(card(s,prefix) for s in styles)}</div></section>'''


def price_context(product):
    if product.get('annualEdit'):
        return product['priceLabelEn']+' · Record reviewed '+date_label(product['checkedAt'])
    return product['priceContextEn']


def suggestion_card(atlas,suggestion,prefix='../'):
    product=atlas['catalog'][suggestion['id']];brand=atlas['brands'][product['brand']]
    return f'''<article class="style-suggestion"><a class="style-suggestion-photo" href="{prefix}item/{product['id']}.html"><img src="{prefix}{e(product['image'])}" width="{product['imageWidth']}" height="{product['imageHeight']}" alt="{e(brand['name']+' '+product['name'])}，本站搭配推荐而非已确认视频同款" loading="lazy"></a><div><a class="eyebrow rose-text" href="{prefix}brand/{brand['id']}.html">{e(brand['name'])} ↗</a><h3 lang="en"><a href="{prefix}item/{product['id']}.html">{e(product['name'])}</a></h3><p>{e(suggestion['reason'])}</p><p class="style-suggestion-price" lang="en">{price_text(product)}</p><p class="style-suggestion-context" lang="en">{e(price_context(product))}</p><a class="text-link" href="{prefix}item/{product['id']}.html">型号、材质与多图详情 ↗</a></div></article>'''


def product_links(atlas,product_id,prefix='../'):
    styles=[s for s in atlas['config']['styles'] if any(x['id']==product_id for x in s['products'])]
    if not styles:return ''
    return '<section class="container style-related"><p class="eyebrow rose-text">IN AN OUTFIT</p><h2>把这件单品放进穿搭</h2><p>本站编辑搭配建议，未认定为视频同款。价格与型号以本页实际来源日期为准。</p><div>'+''.join(f'<a class="text-link" href="{prefix}style/{s["id"]}.html">{e(s["nameZh"])} · {e(s["name"])} ↗</a>' for s in styles)+'</div></section>'


def brand_links(atlas,brand_id,prefix='../'):
    styles=[]
    for s in atlas['config']['styles']:
        ids={m['brand'] for m in s['brandMatches']}|{atlas['catalog'][x['id']]['brand'] for x in s['products']}
        if brand_id in ids:styles.append(s)
    if not styles:return ''
    return '<section class="style-related"><p class="eyebrow rose-text">THE STYLE ATLAS</p><h2>从造型，继续认识这个品牌</h2><p>按具体设计细节匹配，品牌可以出现在多种风格中。</p><div>'+''.join(f'<a class="text-link" href="{prefix}style/{s["id"]}.html">{e(s["nameZh"])} ↗</a>' for s in styles)+'</div></section>'


def source_note(atlas,prefix=''):
    source=atlas['config']['sourceVideo']
    return f'''<aside class="style-source-note"><p class="eyebrow">THE ORIGINAL REFERENCE</p><h2>这一组造型从哪里来</h2><p>参考视频：{e(source['creator'])}《{e(source['title'])}》，发布于{e(source['publishedAt'][:10])}，约64秒。本栏目保留视频的三种风格称呼，造型拆解与搭配理由为MuseLux原创编辑内容。</p><p>引用画面保留作者水印，仅用于对应造型评论；完整作品请到作者原页观看。视频截图保留2880×2160原始画面，点击图片可查看PNG；摄影作品的作者与许可标在各图旁。推荐款式按本站既有型号与资料日期展示，没有据画面认定服饰材质或鉴定视频同款。</p><a class="text-link" href="{e(source['source'])}" target="_blank" rel="noopener">观看作者原视频 ↗</a></aside>'''


def render(atlas,page):
    styles=atlas['config']['styles']
    cards=''.join(card(s) for s in styles)
    shortcuts=''.join(f'<a href="style/{s["id"]}.html">{e(s["nameZh"])} ↗</a>' for s in styles)+'<a href="#photography">摄影灵感 ↘</a>'
    content=f'''<div class="container style-atlas-page"><nav class="breadcrumbs" aria-label="面包屑"><a href="index.html">首页</a><span>/</span><span aria-current="page">女性风格</span></nav><header class="style-atlas-opening"><p class="eyebrow rose-text">THE STYLE ATLAS / VOL. 01</p><h1>从喜欢的造型，<br>找到穿搭的线索<span class="rose-dot">。</span></h1><p class="style-atlas-english" lang="en">Three looks. A closer reading.</p><p>读懂一套衣服，不必先记住所有品牌。先看轮廓、颜色与配饰比例，再用具体作品把风格放进自己的日常。</p><nav class="style-atlas-shortcuts" aria-label="选择女性穿搭风格">{shortcuts}</nav></header><section class="style-atlas-grid" aria-label="原视频三种主风格">{cards}</section>{photography_section(atlas)}{creator_section(atlas)}<section class="style-atlas-how"><p class="eyebrow">READ / CONNECT / WEAR</p><h2>先观察，再挑一件</h2><ol><li><strong>看造型</strong><p>每种风格都保留可回看的视频时间点，拆解画面里实际能看见的细节。</p></li><li><strong>找品牌</strong><p>用具体系列和官方作品的设计特征解释匹配理由，一个品牌可以进入不同风格。</p></li><li><strong>配单品</strong><p>每种风格给出三件本站已有款式。美元参考保留原日期，档案报价和快照各自标明。</p></li></ol></section>{source_note(atlas)}</div>'''
    page('womens-style.html','The Style Atlas','从Mob Wife、拿破仑风与千金风，阅读造型细节、品牌对应、真实单品与有日期的美元参考。',content,'styles')
    for style in styles:
        observations=''.join(f'<li><a href="{e(atlas["config"]["sourceVideo"]["source"]+"?t="+str(o["time"]))}" target="_blank" rel="noopener">{timestamp(o["time"])} ↗</a><p>{e(o["text"])}</p></li>' for o in style['observations'])
        matches=[]
        for match in style['brandMatches']:
            brand=atlas['brands'][match['brand']]
            matches.append(f'''<article class="style-brand-match"><a class="eyebrow rose-text" href="../brand/{brand['id']}.html">{e(brand['name'])} ↗</a><h3>{e(match['collection'])}</h3><p>{e(match['reason'])}</p><p class="style-brand-evidence">官方设计线索：{e(match['feature'])}</p><a class="text-link" href="{e(match['source'])}" target="_blank" rel="noopener">查看官方作品 ↗</a></article>''')
        other=''.join(card(s,'../') for s in styles if s['id']!=style['id'])
        extra=''.join(f'<a class="source-link" href="{e(x["source"])}" target="_blank" rel="noopener">{e(x["label"])} ↗</a>' for x in style.get('extraReading',[]))
        content=f'''<div class="container style-detail"><nav class="breadcrumbs" aria-label="面包屑"><a href="../index.html">首页</a><span>/</span><a href="../womens-style.html">女性风格</a><span>/</span><span aria-current="page">{e(style['nameZh'])}</span></nav><header class="style-detail-opening"><div><p class="eyebrow rose-text">THE STYLE ATLAS / {e(style['name'])}</p><h1>{e(style['nameZh'])}</h1><p>{e(style['tagline'])}</p><span class="style-video-label">视频标签：{e(style['videoLabel'])} · {e(style['rangeLabel'])}</span></div>{figure(style,'../')}</header><div class="style-reading"><article class="prose"><p>{e(style['introZh'])}</p><p lang="en">{e(style['introEn'])}</p><h2>把这套造型拆开看</h2><ol class="style-observations">{observations}</ol><h2>一个可以照着试的组合</h2><ul class="style-formula">{''.join('<li>'+e(x)+'</li>' for x in style['formula'])}</ul><p>{e(style['stylingZh'])}</p></article><aside class="style-reading-note"><p class="eyebrow">THE EDITORIAL CONNECTION</p><h2>把线索放回具体作品</h2><p>下面的品牌与单品由本站根据设计特征匹配，未认定为视频里穿戴的同款。</p><p>{e(style['avoidZh'])}</p><a class="text-link" href="#brand-matches">先看品牌对应 ↓</a><a class="text-link" href="#style-pieces">再看三件搭配 ↓</a></aside></div>{photography_section(atlas,style,'../')}{creator_section(atlas,style)}<section class="style-section" id="brand-matches"><p class="eyebrow rose-text">HOUSES / SHAPES / DETAILS</p><h2>哪些品牌作品，可以从这里读起</h2><div class="style-brand-grid">{''.join(matches)}</div>{extra}</section><section class="style-section" id="style-pieces"><p class="eyebrow rose-text">THREE PIECES TO CONSIDER</p><h2>把风格落到具体单品</h2><p class="style-section-note">本站搭配推荐，非已确认视频同款。下方美元参考沿用各商品实际来源日期；档案款保留历史报价口径。具体尺寸、材质与照片见详情页。</p><div class="style-suggestion-grid">{''.join(suggestion_card(atlas,p) for p in style['products'])}</div></section>{source_note(atlas,'../')}<section class="style-section"><p class="eyebrow">ANOTHER WAY TO DRESS</p><h2>换一种造型，再看一次</h2><div class="style-atlas-grid style-atlas-pair">{other}</div></section></div>'''
        page('style/'+style['id']+'.html',style['name'],style['tagline']+'阅读视频造型、品牌对应与具体单品搭配。',content,'style',style['id'],style=style)
