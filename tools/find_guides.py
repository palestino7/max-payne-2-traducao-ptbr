import urllib.request, re, sys

sys.stdout.reconfigure(encoding='utf-8')
url = 'https://steamcommunity.com/app/12150/guides/?searchText=Tradu%C3%A7%C3%A3o'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
        matches = re.findall(r'href="(https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+)"', html)
        print("Direct links:", list(set(matches))[:10])
except Exception as e:
    print('Error:', e)
