import urllib.request, re, sys

sys.stdout.reconfigure(encoding='utf-8')
guides = [
    '2391895389', '1673588008', '474101971', '3482751985',
    '305909505', '2258930484', '2616843336', '3775755232',
    '3542269893', '2399840060'
]

for gid in guides:
    url = f'https://steamcommunity.com/sharedfiles/filedetails/?id={gid}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            html = r.read().decode('utf-8', errors='ignore')
            title = re.search(r'<div class="workshopItemTitle">([^<]+)</div>', html)
            t = title.group(1).strip() if title else 'No title'
            print(f'{gid}: {t}')
            # Look for mega / mediafire / drive
            links = re.findall(r'https?://(?:mega\.nz|www\.mediafire\.com|drive\.google\.com)[^\s"\'<>]+', html)
            if links:
                print('   Links:', links)
    except Exception as e:
        print(f'{gid} Error: {e}')
