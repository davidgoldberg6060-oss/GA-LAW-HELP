import os, hashlib, uuid, shutil
from pathlib import Path
from typing import BinaryIO
from .private_case_policy import private_storage_prefix

ROOT=Path(os.getenv('EVIDENCE_DIR','./evidence_store'))
ROOT.mkdir(parents=True,exist_ok=True)
BACKEND=os.getenv('STORAGE_BACKEND','local').lower()
BUCKET=os.getenv('S3_BUCKET','')
PREFIX=os.getenv('S3_PREFIX','evidence').strip('/')
MAX_EVIDENCE_BYTES=int(os.getenv('MAX_EVIDENCE_BYTES',str(10*1024*1024*1024)))
MAX_CHUNK_BYTES=int(os.getenv('MAX_CHUNK_BYTES',str(16*1024*1024)))

def _s3():
    import boto3
    from botocore.config import Config
    return boto3.client('s3', endpoint_url=os.getenv('S3_ENDPOINT_URL') or None,
        region_name=os.getenv('AWS_REGION') or None,
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID') or None,
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY') or None,
        config=Config(signature_version='s3v4',s3={'addressing_style':'path'}))

def session_dir(user_id:int, case_id:int, upload_id:str)->Path:
    p=ROOT/'uploads'/private_storage_prefix(user_id,case_id)/upload_id
    p.mkdir(parents=True,exist_ok=True); return p

def save_chunk(user_id,case_id,upload_id,index,data:bytes):
    if len(data) > MAX_CHUNK_BYTES: raise ValueError('chunk exceeds MAX_CHUNK_BYTES')
    p=session_dir(user_id,case_id,upload_id)/f'{index:08d}.part'
    if p.exists(): return p.stat().st_size
    tmp=p.with_suffix('.tmp'); tmp.write_bytes(data); os.replace(tmp,p); return len(data)

def _cloud_key(key:str)->str: return f'{PREFIX}/{key}' if PREFIX else key

def put_file(local_path:Path,key:str):
    if BACKEND=='s3':
        if not BUCKET: raise RuntimeError('S3_BUCKET is required for STORAGE_BACKEND=s3')
        # Objects are private and are read only through authenticated API routes.
        # Do not add public-read ACLs or expose storage URLs to clients.
        _s3().upload_file(str(local_path),BUCKET,_cloud_key(key))
        local_path.unlink(missing_ok=True)
    return key

def store_stream(stream:BinaryIO,key:str):
    dest=ROOT/'staging'/key; dest.parent.mkdir(parents=True,exist_ok=True)
    h=hashlib.sha256(); size=0
    with open(dest,'xb') as out:
        while True:
            b=stream.read(8*1024*1024)
            if not b: break
            size+=len(b)
            if size > MAX_EVIDENCE_BYTES:
                out.close(); dest.unlink(missing_ok=True); raise ValueError('evidence exceeds MAX_EVIDENCE_BYTES')
            h.update(b); out.write(b)
    put_file(dest,key)
    return h.hexdigest(),size

def open_stored(key:str):
    if BACKEND=='s3':
        return _s3().get_object(Bucket=BUCKET,Key=_cloud_key(key))['Body']
    return open(ROOT/'staging'/key,'rb')

def hash_stored(key:str):
    h=hashlib.sha256(); size=0
    if BACKEND=='s3':
        body=_s3().get_object(Bucket=BUCKET,Key=_cloud_key(key))['Body']
        while True:
            b=body.read(8*1024*1024)
            if not b: break
            h.update(b); size+=len(b)
    else:
        path=ROOT/'staging'/key
        with open(path,'rb') as src:
            while True:
                b=src.read(8*1024*1024)
                if not b: break
                h.update(b); size+=len(b)
    return h.hexdigest(),size

def finalize_chunks(user_id,case_id,upload_id,filename,total_chunks,expected_bytes=None):
    src=session_dir(user_id,case_id,upload_id)
    safe=os.path.basename(filename or 'evidence')
    key=f'{private_storage_prefix(user_id,case_id)}/{uuid.uuid4().hex}_{safe}'
    dest=ROOT/'staging'/key; dest.parent.mkdir(parents=True,exist_ok=True)
    h=hashlib.sha256(); size=0
    with open(dest,'xb') as out:
        for i in range(total_chunks):
            part=src/f'{i:08d}.part'
            if not part.exists(): raise FileNotFoundError(f'missing chunk {i}')
            with open(part,'rb') as f:
                while True:
                    b=f.read(8*1024*1024)
                    if not b: break
                    h.update(b); out.write(b); size+=len(b)
    if size > MAX_EVIDENCE_BYTES:
        dest.unlink(missing_ok=True); raise ValueError('evidence exceeds MAX_EVIDENCE_BYTES')
    if expected_bytes is not None and size != expected_bytes:
        dest.unlink(missing_ok=True); raise ValueError('assembled size does not match declared total_bytes')
    shutil.rmtree(src,ignore_errors=True); put_file(dest,key)
    return key,h.hexdigest(),size