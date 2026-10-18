import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

candidates = [
    ("CFMI Rock 101.1 Vancouver", "https://corus.leanstream.co/CFMIFM"),
    ("CFNY 102.1 The Edge Toronto", "https://corus.leanstream.co/CFNYFM"),
    ("CILQ Q107 107.1 Toronto", "https://corus.leanstream.co/CILQFM"),
    ("CHOM 97.7 Montreal", "https://rogers.leanstream.co/rogers/chomfm.stream/icy?environment=tunein&args=tunein_01"),
    ("CHEZ 106.1 Ottawa", "https://rogers.leanstream.co/rogers/ott1061.stream/icy?environment=tunein&args=tunein_01"),
    ("CJAX Jack 96.9 Vancouver", "https://rogers.leanstream.co/rogers/van969.stream/icy?environment=tunein&args=tunein_01"),
    ("CKKS Sonic 107.5 Chilliwack/Van", "https://rogers.leanstream.co/rogers/van1049.stream/icy?environment=tunein&args=tunein_01"),
    ("CJAQ Jack 96.9 Calgary", "https://rogers.leanstream.co/rogers/cal969.stream/icy?environment=tunein&args=tunein_01"),
]

for name, url in candidates:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=4, context=ctx) as r:
            print(f"[VERIFIED 200] {name} | {r.headers.get('Content-Type')} | {url}")
    except Exception as e:
        print(f"[FAIL] {name} -> {e}")
