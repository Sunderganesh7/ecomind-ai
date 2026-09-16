import json
import urllib.request
import os

KB_DIR = os.path.join(os.path.dirname(__file__), "../knowledge_base/metadata")
SOURCES_PATH = os.path.join(KB_DIR, "sources.json")

def check_urls():
    with open(SOURCES_PATH, "r", encoding="utf-8") as f:
        sources = json.load(f)
    
    results = {}
    for s in sources:
        url = s["url"]
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                status = response.getcode()
                results[s["source_id"]] = (status == 200, status)
        except Exception as e:
            results[s["source_id"]] = (False, str(e))
            
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    check_urls()
