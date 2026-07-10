import sys, os, hashlib, json, base64
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import urllib3
from flask import Flask, request, Response
from Crypto.Cipher import AES
from google.protobuf import json_format
from cachetools import TTLCache
from xH import gJwt
import AccountPersonalShow_pb2 as apsPb
import main_pb2 as mPb
import requests , time

urllib3.disable_warnings()
app = Flask(__name__)

cK = hashlib.md5(b"DeveloperHabib69").hexdigest()

mK = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
mIV = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')

jCache = TTLCache(maxsize=10, ttl=4 * 60 * 60)
iCache = TTLCache(maxsize=100, ttl=300)
bUid = "4307122789"
bPw  = "92C815BB3EFCB3211AC515B019AB120CDBE83B714DCB4EA84565156680946154"

def vCr(d): return hashlib.md5(d.get("Dev","").encode().replace(b"@",b"\x40")).hexdigest()==cK

def encPl(b):
    n=AES.block_size-(len(b)%AES.block_size)
    return AES.new(mK,AES.MODE_CBC,mIV).encrypt(b+bytes([n]*n))

def mkPl(uid):
    m=mPb.GetPlayerPersonalShow(); m.a=int(uid); m.b=7
    return encPl(m.SerializeToString())
    
OB_VERSION_CACHE = {"version": None, "timestamp": 0}

OB_VERSION_CACHE_TTL = 3600 
 
def get_ob_version():
    global OB_VERSION_CACHE
    now = time.time()
    if OB_VERSION_CACHE["version"] and (now - OB_VERSION_CACHE["timestamp"]) < OB_VERSION_CACHE_TTL:
        return OB_VERSION_CACHE["version"]

    try:
        url = "https://version.ggwhitehawk.com//live/ver.php?version=1.3.0&lang=ar&device=android&channel=android&appstore=googleplay&region=ME&whitelist_version=1.3.0&whitelist_sp_version=1.0.0&device_name=google%20G011A&device_CPU=ARMv7%20VFPv3%20NEON%20VMH&device_GPU=Adreno%20(TM)%20640&device_mem=1993"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        ob = data.get("latest_release_version")
        if ob:
            OB_VERSION_CACHE["version"] = ob
            OB_VERSION_CACHE["timestamp"] = now
            return ob
    except Exception as e:
        print(f"[ERROR] Failed to fetch OB version: {e}")

    return "ob"

def ua():
    return random.choice([
        "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
        "GarenaMSDK/4.0.18P6(SM-A125F ;Android 11;en;IN;)",
        "GarenaMSDK/4.1.0P3(Redmi 9A ;Android 10;en;ID;)"
    ])    

def getTok():
    k="jwt_ME"
    if k in jCache: return jCache[k]
    tok=gJwt(bUid,bPw)
    jCache[k]=tok
    return tok

def fetch(uid):
    tok=getTok()
    pl=mkPl(uid)
    h={
        "Host":"clientbp.ggblueshark.com",
        "X-Unity-Version":"2018.4.11f1","Accept":"*/*",
        "Authorization":f"Bearer {tok}","ReleaseVersion": get_ob_version(),
        "X-GA":"v1 1","Accept-Encoding":"gzip, deflate, br",
        "Content-Type":"application/octet-stream",
        "User-Agent":"Free%20Fire/2019118692 CFNetwork/3826.500.111.2.2 Darwin/24.4.0",
        "Connection":"keep-alive"
    }
    r=requests.post("https://clientbp.ggpolarbear.com/GetPlayerPersonalShow",data=pl,headers=h,verify=False,timeout=30)
    if r.status_code!=200: raise Exception(f"server {r.status_code}")
    proto=apsPb.AccountPersonalShowInfo()
    proto.ParseFromString(r.content)
    return json.loads(json_format.MessageToJson(proto))

@app.get("/info")
def ep():
    uid=request.args.get("uid","").strip()
    if not uid or not uid.isdigit():
        return Response(json.dumps({"ok":False,"error":"invalid uid","Dev":"DeveloperHabib69"},ensure_ascii=False),mimetype='application/json'),400
    ck=(request.path,uid)
    if ck in iCache:
        cached=iCache[ck]
        if not vCr(cached): return Response(json.dumps({"error":"Hey hey my credit","Dev":"DeveloperHabib69"},ensure_ascii=False),mimetype='application/json'),403
        return Response(json.dumps(cached,ensure_ascii=False),mimetype='application/json')
    try:
        data=fetch(uid)
        out={**data,"Dev":"DeveloperHabib69"}
        if not vCr(out): return Response(json.dumps({"error":"heyyy bro my credit","Dev":"DeveloperHabib69"},ensure_ascii=False),mimetype='application/json'),403
        iCache[ck]=out
        return Response(json.dumps(out,ensure_ascii=False),mimetype='application/json')
    except Exception as e:
        jCache.clear()
        return Response(json.dumps({"ok":False,"error":str(e),"Dev":"DeveloperHabib69"},ensure_ascii=False),mimetype='applicATion/json'),497

if __name__=="__main__": app.run(host="0.0.0.0",port=5000,debug=False)
