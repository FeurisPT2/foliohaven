import sys
import subprocess
import time
import urllib.request
import json
sys.path.append(r"c:\Users\epicg\Downloads\icecream_ebook_reader_replica\tests")
from e2e_suite import MinimalWebSocketClient

cmd = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "--headless=new",
    "--remote-debugging-port=9222",
    "--disable-gpu",
    "--no-sandbox",
    "--allow-file-access-from-files",
    r"file:///c:/Users/epicg/Downloads/icecream_ebook_reader_replica/app/index.html"
]
proc = subprocess.Popen(cmd)
time.sleep(1.5)
try:
    with urllib.request.urlopen("http://localhost:9222/json") as resp:
        tabs = json.loads(resp.read().decode())
        print("All tabs:")
        for t in tabs:
            print(f"  Type: {t.get('type')}, URL: {t.get('url')}")
        page_tabs = [t for t in tabs if t.get("type") == "page" and "app/index.html" in t.get("url", "")]
        tab = page_tabs[0] if page_tabs else tabs[0]
        ws_url = tab["webSocketDebuggerUrl"]
        path = ws_url.split("localhost:9222")[1]
        ws = MinimalWebSocketClient("localhost", 9222, path)
        print("window.db string:", ws.eval_js("String(window.db)"))
        print("window.app string:", ws.eval_js("String(window.app)"))
        print("window.engine string:", ws.eval_js("String(window.engine)"))
        # Check any errors
        errors = ws.eval_js("""
            (function() {
                return {
                    scripts: Array.from(document.querySelectorAll('script')).map(s => s.src),
                    hasContainer: !!document.getElementById('app-container')
                };
            })()
        """)
        print("DOM scripts & container:", errors)
finally:
    proc.terminate()
