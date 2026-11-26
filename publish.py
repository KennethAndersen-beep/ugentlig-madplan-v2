import json, pathlib, os, tempfile, sys
root=pathlib.Path(__file__).resolve().parent
src=root/'incoming/test.json'; dst=root/'public/test.json'
def publish():
    d=json.loads(src.read_text())
    if type(d) is not dict or set(d)!={'version','message'} or type(d['version']) is not int or d['version']<1 or not isinstance(d['message'],str) or not d['message'].strip(): raise ValueError('Invalid test payload')
    dst.parent.mkdir(exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=dst.parent,delete=False,mode='w',encoding='utf-8') as f:
        json.dump(d,f,ensure_ascii=False); name=f.name
    os.replace(name,dst)
    print('PASS: validated and staged version',d['version'])
if __name__=='__main__':
    try: publish()
    except Exception as e: print('FAIL:',e,file=sys.stderr); sys.exit(1)
