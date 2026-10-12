#!/usr/bin/env python3
"""옛 주소 ggah1911.github.io/wowbocho/<경로> 마다 넘겨주기 페이지를 만든다.

- 새 사이트 sitemap.xml 의 주소마다 wowbocho/<경로>/index.html 을 만든다(HTTP 200).
  404.html 로만 넘기면 GitHub Pages 가 404 상태로 응답해서 구글이 canonical 을 따르지 않는다.
- 각 페이지는 canonical·meta refresh 를 그 경로의 새 주소로 둔다(구글은 0초 meta refresh 를 영구 이동으로 본다).
- noindex 는 넣지 않는다: noindex 가 있으면 구글이 이 페이지를 버리기만 하고 새 주소로 순위를 넘기지 않는다.
- 브라우저 저장값(wg:*) 옮기기 스크립트는 그대로 둔다.
사용: python3 tools/gen.py  (새 사이트 sitemap 을 받아 다시 만든다)
"""
import os, re, shutil, urllib.request
NEW = "https://wowbocho.pages.dev"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JS = """(function(){var p=location.pathname.replace(/^\\/wowbocho(?=\\/|$)/,"")||"/",d={},n=0;
try{for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i),v=localStorage.getItem(k);if(k&&k.indexOf("wg:")===0&&v!=null&&v.length<20000){d[k]=v;n++;}}}catch(e){}
var h=n?"#wgimport="+encodeURIComponent(JSON.stringify({d:d,h:location.hash})):location.hash;
location.replace("https://wowbocho.pages.dev"+p+location.search+h);})();"""

def page(target):
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<title>와우보초 주소가 바뀌었습니다</title>
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0;url={target}">
<script>
// 와우보초는 2026-10-06 https://wowbocho.pages.dev/ 로 옮겼다. 옛 주소 ggah1911.github.io/wowbocho/… 를 같은 경로로 넘겨준다
// 옛 주소의 브라우저 저장값(wg:*)은 이 도메인에만 있으므로 #wgimport= 에 실어 보내고, 새 사이트 app.js 가 받아 저장한다
{JS}
</script>
</head><body style="font-family:sans-serif;background:#111;color:#ddd;padding:40px">
<p>와우보초 주소가 바뀌었습니다: <a href="{target}" style="color:#6af">{target}</a></p>
</body></html>
"""

xml = urllib.request.urlopen(urllib.request.Request(NEW + "/sitemap.xml", headers={"User-Agent": "Mozilla/5.0"})).read().decode()
locs = re.findall(r"<loc>(.*?)</loc>", xml)
assert len(locs) > 100, len(locs)
out = os.path.join(ROOT, "wowbocho")
shutil.rmtree(out, ignore_errors=True)
for loc in locs:
    path = loc[len(NEW):]
    assert path.startswith("/") and path.endswith("/"), loc
    d = os.path.join(out, path.strip("/"))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(page(loc))
# 사용자 사이트 맨 앞과 모르는 경로(404.html)는 새 사이트 홈을 대표 주소로 둔다
for f in ("index.html", "404.html"):
    open(os.path.join(ROOT, f), "w").write(page(NEW + "/"))
print(len(locs), "pages")
