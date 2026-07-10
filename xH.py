import requests, json, binascii, random, warnings
import urllib3
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from cryptography.hazmat.primitives.ciphers import Cipher as Cp, algorithms as Al, modes as Md
from cryptography.hazmat.backends import default_backend as Bk
from google.protobuf.internal.decoder import _DecodeVarint32

warnings.filterwarnings("ignore")
urllib3.disable_warnings()

K  = b"Yg&tc%DEuh6%Zc^8"
IV = b"6oyZDr22E3ychjM%"

# নতুন পেলেলড (OB54 1.126.1)
dT = bytes.fromhex(
    "1a13323032352d31312d32362030313a35313a3238220966726565206669726528013a07312e3132362e314232416e64726f6964204f532039202f204150492d3238202850492f72656c2e636a772e32303232303531382e313134313333294a0848616e6468656c64520c4d544e2f537061636574656c5a045749464960800a68d00572033234307a2d7838362d3634205353453320535345342e3120535345342e32204156582041565832207c2032343030207c20348001e61e8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e329a012b476f6f676c657c36323566373136662d393161372d343935622d396631362d303866653964336336353333a2010e3137362e32382e3133392e313835aa01026172b201203433303632343537393364653836646134323561353263616164663231656564ba010134c2010848616e6468656c64ca010d4f6e65506c7573204135303130ea014063363961653230386661643732373338623637346232383437623530613361316466613235643161313966616537343566633736616334613065343134633934f00101ca020c4d544e2f537061636574656cd2020457494649ca03203161633462383065636630343738613434323033626638666163363132306635e003b5ee02e8039a8002f003af13f80384078004a78f028804b5ee029004a78f029804b5ee02b00404c80401d2043d2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f6c69622f61726de00401ea045f65363261623933353464386662356662303831646233333861636233333439317c2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f626173652e61706bf00406f804018a050233329a050a32303139313139303236a80503b205094f70656e474c455332b805ff01c00504e005be7eea05093372645f7061727479f205704b717348543857393347646347335a6f7a454e6646775648746d377171316552554e6149444e67526f626f7a4942744c4f695943633459367a767670634943787a514632734f453463627974774c7334785a62526e70524d706d5752514b6d654f35766373386e51594268777148374bf805e7e4068806019006019a060134a2060134b2062213521146500e590349510e460900115843395f005b510f685b560a6107576d0f0366"
)

def padB(d): n=16-(len(d)%16); return d+bytes([n]*n)
def upd(d): p=d[-1]; return d[:-p] if 1<=p<=16 else d

def enc(b):
    c=Cp(Al.AES(K),Md.CBC(IV),backend=Bk()); e=c.encryptor()
    return e.update(padB(b))+e.finalize()

def dec(b):
    c=Cp(Al.AES(K),Md.CBC(IV),backend=Bk()); d=c.decryptor()
    return upd(d.update(b)+d.finalize())

def pbD(data):
    i,out=0,{}
    while i<len(data):
        try: key,i=_DecodeVarint32(data,i)
        except: break
        fn,wt=key>>3,key&0x7
        if wt==0:
            v,i=_DecodeVarint32(data,i); out[str(fn)]={"t":"int","v":v}
        elif wt==2:
            ln,i=_DecodeVarint32(data,i); v=data[i:i+ln]; i+=ln
            try: out[str(fn)]={"t":"str","v":v.decode()}
            except: out[str(fn)]={"t":"hex","v":v.hex()}
        elif wt==1: out[str(fn)]={"t":"64b","v":data[i:i+8].hex()}; i+=8
        elif wt==5: out[str(fn)]={"t":"32b","v":data[i:i+4].hex()}; i+=4
        else: break
    return out

def eID(x):
    x=int(x); e=[]
    while x:
        e.append((x&0x7F)|(0x80 if x>0x7F else 0)); x>>=7
    return bytes(e).hex()

def ua():
    return random.choice([
        "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
        "GarenaMSDK/4.0.18P6(SM-A125F ;Android 11;en;IN;)",
        "GarenaMSDK/4.1.0P3(Redmi 9A ;Android 10;en;ID;)"
    ])

def gTok(u,p):
    r=requests.post(
        "https://100067.connect.garena.com/oauth/guest/token/grant",
        headers={"Host":"100067.connect.garena.com","User-Agent":ua(),"Content-Type":"application/x-www-form-urlencoded","Accept-Encoding":"gzip, deflate, br","Connection":"close"},
        data={"uid":u,"password":p,"response_type":"token","client_type":"2","client_secret":"2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3","client_id":"100067"},
        verify=False,timeout=15
    )
    if r.status_code!=200: raise Exception(f"garena {r.status_code}")
    d=r.json(); return d["access_token"],d["open_id"]

def bLd(at,oid):
    x=dT[:]
    # ডেট টাইম আপডেট
    x=x.replace(b"2025-11-26 01:51:28", str(datetime.now())[:19].encode())
    # অ্যাক্সেস টোকেন রিপ্লেস
    x=x.replace(b"c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94", at.encode())
    # ওপেন আইডি রিপ্লেস
    x=x.replace(b"4306245793de86da425a52caadf21eed", oid.encode())
    return enc(x)

def gJwt(u,p):
    at,oid=gTok(u,p)
    pay=bLd(at,oid)
    r=requests.post(
        "https://loginbp.ggpolarbear.com/MajorLogin",
        headers={"Expect":"100-continue","X-Unity-Version":"2018.4.11f1","X-GA":"v1 1","ReleaseVersion":"OB54","Host":"loginbp.common.ggbluefox.com","User-Agent":"Dalvik/2.1.0 (Linux; U; Android 13; A063)","Content-Type":"application/x-www-form-urlencoded","Accept-Encoding":"gzip"},
        data=pay,verify=False,timeout=20
    )
    if r.status_code!=200: raise Exception(f"MajorLogin {r.status_code}")
    d=pbD(r.content); tok=d.get("8",{}).get("v","")
    if not tok: raise Exception("no jwt")
    return tok.strip()

def hdr(tok):
    return {"Content-Type":"application/x-www-form-urlencoded","X-GA":"v1 1","ReleaseVersion":"OB54","Host":"clientbp.ggpolarbear.com","Accept-Encoding":"gzip, deflate, br","Accept-Language":"en-GB,en-US;q=0.9,en;q=0.8","User-Agent":"Free%20Fire/2019117061 CFNetwork/1399 Darwin/22.1.0","Connection":"keep-alive","Authorization":f"Bearer {tok}","X-Unity-Version":"2018.4.11f1","Accept":"*/*"}