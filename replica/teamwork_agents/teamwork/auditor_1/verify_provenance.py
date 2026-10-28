import os
import re

exe_path = r"C:\Program Files (x86)\Icecream Ebook Reader\icebookreader.exe"
svc_path = r"C:\Program Files (x86)\Icecream Ebook Reader\icebooksvc.exe"
settings_path = r"C:\Users\epicg\AppData\Local\Icecream\Icecream Ebook Reader\settings.ini"
db_path = r"C:\Users\epicg\.Icecream Ebook Reader\data\ebooklib.sqlite3"

print("=== 1. CHECKING BINARY STRINGS PROVENANCE (icebookreader.exe) ===")
with open(exe_path, "rb") as f:
    exe_data = f.read()

terms_to_find = [
    b"BookReader",
    b"wstransport.h",
    b"WSTransport",
    b"ebooklib.sqlite3",
    b"NotePopup",
    b"Debenu",
    b"books",
    b"book_metadata",
    b"book_folder_binder",
    b"DayStyle",
    b"NightStyle",
    b"SepiaStyle",
    b"lastStyleId",
    b"column_count"
]

for t in terms_to_find:
    cnt = exe_data.count(t)
    print(f"icebookreader.exe contains '{t.decode('utf-8')}': count={cnt}")
    assert cnt > 0, f"Missing term {t} in icebookreader.exe"

print("\n=== 2. CHECKING HELPER SERVICE PROVENANCE (icebooksvc.exe) ===")
with open(svc_path, "rb") as f:
    svc_data = f.read()

svc_terms = [b"reportPaginationDone", b"remotehandler.cpp", b"RemoteHandler", b"QLocalSocket"]
for t in svc_terms:
    cnt = svc_data.count(t)
    print(f"icebooksvc.exe contains '{t.decode('utf-8')}': count={cnt}")
    assert cnt > 0, f"Missing term {t} in icebooksvc.exe"

print("\n=== 3. CHECKING SETTINGS.INI PROVENANCE ===")
with open(settings_path, "r", encoding="utf-8", errors="ignore") as f:
    ini_content = f.read()

ini_terms = ["lastStyleId", "library_view_mode", "ttsLocaleVoiceMap", "column_count", "MainWindow_Geometry"]
for t in ini_terms:
    assert t in ini_content, f"Missing INI key {t}"
    print(f"settings.ini contains '{t}': YES")

print("\n=== 4. CHECKING LOG FILES PROVENANCE ===")
log_dir = r"C:\Users\epicg\.Icecream Ebook Reader\log"
logs = [os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.startswith("icebookreader_") and f.endswith(".txt")]
found_resize = False
for lp in logs:
    with open(lp, "r", encoding="utf-8", errors="ignore") as f:
        l_text = f.read()
        if "RESIZE MODE" in l_text:
            found_resize = True
            print(f"Found 'RESIZE MODE' in {os.path.basename(lp)}")
            for line in l_text.splitlines():
                if "RESIZE MODE" in line:
                    print(f"  Snippet: {line.strip()}")
            break

print(f"Log trace confirmed 'RESIZE MODE': {found_resize}")
assert found_resize, "RESIZE MODE not found in logs"

print("\n=== 5. CHECKING TRANSLATION STRINGS PROVENANCE ===")
qm_path = r"C:\Program Files (x86)\Icecream Ebook Reader\translations\ebookreader_en.qm"
with open(qm_path, "rb") as f:
    qm_data = f.read()

qm_terms = [b"Table of contents", b"Bookmarks", b"Clear all bookmarks", b"Export notes to HTML", b"Add note"]
for t in qm_terms:
    cnt = qm_data.count(t)
    print(f"ebookreader_en.qm contains '{t.decode('utf-8')}': count={cnt}")
    assert cnt > 0, f"Missing translation string {t}"

print("\nALL 5 PROVENANCE GROUND TRUTH CHECKS VERIFIED EMPIRICALLY WITH 100% MATCH!")
