"""One repeatable pre-publication gate; Python stdlib and Node.js, no packages."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,re

ROOT=Path(__file__).resolve().parents[1]

def run(command):
    result=subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
    if result.returncode:
        print(result.stdout);print(result.stderr,file=sys.stderr)
        raise SystemExit(result.returncode)
    return result.stdout+result.stderr

def snapshot():
    paths=json.loads((ROOT/'reports/page-manifest.json').read_text())
    paths+=['assets/js/data.js','sitemap.xml','reports/page-manifest.json']
    return {path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in paths}

def main():
    node=shutil.which('node')
    if not node:raise SystemExit('Node.js is required for code verification; website browsing still needs no runtime.')
    run([sys.executable,'-m','compileall','-q','tools'])
    for name in ('data.js','render.js','main.js'):run([node,'--check','assets/js/'+name])
    test_result=run([sys.executable,'tools/test_maintenance.py'])
    test_count=int(re.search(r'Ran (\d+) tests?',test_result).group(1))
    run([sys.executable,'tools/generate.py'])
    first=snapshot()
    run([sys.executable,'tools/generate.py'])
    if first!=snapshot():raise SystemExit('Static generation is not reproducible')
    run([sys.executable,'tools/validate.py'])
    run([node,'tools/test_frontend.cjs'])
    run(['git','diff','--check'])
    static=json.loads((ROOT/'reports/static-validation.json').read_text())
    frontend=json.loads((ROOT/'reports/frontend-code-validation.json').read_text())
    sources=sorted((ROOT/'tools').glob('*.py'))+list((ROOT/'assets/js').glob('*.js'))+[ROOT/'tools/test_frontend.cjs']
    report={'passed':True,'reproducibleBuild':True,'pages':static['pages'],'brands':static['brands'],
            'searchableItems':static['searchableItemPages'],'pythonRegressionTests':test_count,
            'frontendAssertions':frontend['assertions'],
            'method':'Python regression tests, actual JavaScript in Node VM with DOM stubs, syntax, exact manifest/runtime/asset checks; no browser layout test',
            'sourceHashes':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}}
    (ROOT/'reports/code-check-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='sourceHashes'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
