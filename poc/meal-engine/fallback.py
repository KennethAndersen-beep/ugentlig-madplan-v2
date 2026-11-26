"""Local prototype for atomic replacement of a single validated JSON snapshot."""
import json, os, tempfile
from pathlib import Path

def publish(path, candidate, validate):
    path=Path(path)
    validate(candidate)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.candidate-')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(candidate,f,ensure_ascii=False,allow_nan=False)
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
