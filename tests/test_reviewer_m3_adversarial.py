"""
FolioHaven Milestone 3 UX & Adversarial Review Test Suite
Reviewer: reviewer_m3_2
Focus Areas:
- Feature 10: Collapsible Formats Stress Testing, Keyboard Navigation, ARIA sync, Fallback resilience
- Feature 11: Reader Toolbar Overflow Menu 4-Theme Styling & WCAG Contrast, Focus restoration, Interaction lifecycle
- Feature 12: Header Layout Visual Balance, Category Button canonical deduplication
- Integrity & Anti-Cheat Audit
"""

import os
import sys
import time
import json
import socket
import struct
import base64
import subprocess
import tempfile
import urllib.request
import unittest

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))

class MinimalCDPClient:
    def __init__(self, host, port, path):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10.0)
        self.sock.connect((host, port))

        key = base64.b64encode(os.urandom(16)).decode('utf-8')
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode('utf-8'))
        response = self.sock.recv(4096).decode('utf-8', errors='ignore')
        if "101" not in response:
            raise RuntimeError(f"WebSocket upgrade failed: {response}")

        self.msg_id = 0

    def send_command(self, method, params=None):
        self.msg_id += 1
        msg = {"id": self.msg_id, "method": method, "params": params or {}}
        payload = json.dumps(msg).encode('utf-8')

        frame = bytearray()
        frame.append(0x81)  # text frame FIN
        length = len(payload)
        if length <= 125:
            frame.append(0x80 | length)
        elif length <= 65535:
            frame.append(0x80 | 126)
            frame.extend(struct.pack("!H", length))
        else:
            frame.append(0x80 | 127)
            frame.extend(struct.pack("!Q", length))

        mask = os.urandom(4)
        frame.extend(mask)
        masked = bytearray(payload[i] ^ mask[i % 4] for i in range(len(payload)))
        frame.extend(masked)

        self.sock.sendall(frame)
        return self._read_response(self.msg_id)

    def _read_response(self, target_id):
        while True:
            head = self.sock.recv(2)
            if len(head) < 2:
                raise RuntimeError("Connection closed")
            b1, b2 = head[0], head[1]
            length = b2 & 0x7F
            if length == 126:
                length = struct.unpack("!H", self.sock.recv(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self.sock.recv(8))[0]

            data = bytearray()
            while len(data) < length:
                chunk = self.sock.recv(min(4096, length - len(data)))
                if not chunk:
                    break
                data.extend(chunk)

            msg = json.loads(data.decode('utf-8', errors='ignore'))
            if msg.get("id") == target_id:
                return msg.get("result", {})

    def eval_js(self, expression):
        res = self.send_command("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        if "exceptionDetails" in res:
            raise RuntimeError(f"JS Exception: {res['exceptionDetails']}")
        return res.get("result", {}).get("value")

    def close(self):
        try:
            self.sock.close()
        except:
            pass


class TestMilestone3AdversarialReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
        ]
        exe = next((p for p in chrome_paths if os.path.exists(p)), None)
        if not exe:
            raise unittest.SkipTest("Chrome executable not found for live CDP tests")

        cls.user_data_dir = tempfile.mkdtemp(prefix="folio_m3_review_")
        cls.port = 9338
        index_file = os.path.abspath(os.path.join(APP_DIR, "index.html")).replace("\\", "/")
        cls.url = f"file:///{index_file}"

        cls.proc = subprocess.Popen([
            exe,
            "--headless=new",
            f"--remote-debugging-port={cls.port}",
            f"--user-data-dir={cls.user_data_dir}",
            "--remote-allow-origins=*",
            "--disable-gpu",
            "--no-sandbox",
            "--allow-file-access-from-files",
            cls.url
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        time.sleep(2.0)
        try:
            req = urllib.request.urlopen(f"http://localhost:{cls.port}/json", timeout=5)
            tabs = json.loads(req.read().decode())
            page_tabs = [t for t in tabs if t.get("type") == "page" and "index.html" in t.get("url", "")]
            tab = page_tabs[0] if page_tabs else tabs[0]
            ws_url = tab["webSocketDebuggerUrl"]
            path = ws_url.split(f"localhost:{cls.port}")[1]
            cls.client = MinimalCDPClient("localhost", cls.port, path)
            cls.client.send_command("Runtime.enable")
        except Exception as e:
            cls.proc.terminate()
            raise unittest.SkipTest(f"Failed to connect to headless Chrome: {e}")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "client"):
            cls.client.close()
        if hasattr(cls, "proc"):
            cls.proc.terminate()
            cls.proc.wait()

    def test_adv_ux_01_collapsible_formats_stress_and_fallback(self):
        """Feature 10: Rapid toggling, storage corruption resilience, inert visibility when collapsed."""
        res = self.client.eval_js("""
            (() => {
                const toggle = document.getElementById("sidebar-formats-toggle");
                const collapsible = document.getElementById("formats-collapsible");
                
                // 1. Rapid 20 toggles stress
                for (let i = 0; i < 20; i++) {
                    toggle.click();
                }
                const isCollapsedAfter20 = collapsible.classList.contains("collapsed");
                const ariaAfter20 = toggle.getAttribute("aria-expanded");
                const storedAfter20 = localStorage.getItem("foliohaven_formats_collapsed");
                const syncAfter20 = (isCollapsedAfter20 ? ariaAfter20 === "false" && storedAfter20 === "true"
                                                       : ariaAfter20 === "true" && storedAfter20 === "false");
                
                // 2. Inert child check when collapsed
                window.app.setFormatsCollapsed(true, true);
                const computedCollapsed = window.getComputedStyle(collapsible);
                const isHiddenWhenCollapsed = computedCollapsed.visibility === "hidden" && 
                                              computedCollapsed.pointerEvents === "none";
                
                // 3. Corrupted localStorage resilience
                localStorage.setItem("foliohaven_formats_collapsed", "CORRUPTED_VALUE_XYZ_!#$");
                window.app.initCollapsibleFormats();
                const safeFallbackExpanded = !collapsible.classList.contains("collapsed") && 
                                              toggle.getAttribute("aria-expanded") === "true";
                
                // Reset to clean expanded state
                window.app.setFormatsCollapsed(false, true);

                return { syncAfter20, isHiddenWhenCollapsed, safeFallbackExpanded };
            })()
        """)
        self.assertTrue(res["syncAfter20"], "Rapid toggling must maintain strict DOM/ARIA/Storage synchronization")
        self.assertTrue(res["isHiddenWhenCollapsed"], "Collapsed container must have visibility:hidden and pointer-events:none")
        self.assertTrue(res["safeFallbackExpanded"], "Invalid localStorage value must safely fall back to expanded default")

    def test_adv_ux_02_overflow_menu_theme_contrast_compliance(self):
        """Feature 11: Reader overflow menu 4-theme styling and WCAG AA/AAA contrast ratios."""
        res = self.client.eval_js(r"""
            (async () => {
                const books = window.db.getBooks();
                if (books.length > 0) window.app.openBook(books[0]);
                window.app.openReaderOverflowMenu();
                
                const menu = document.getElementById("reader-overflow-menu");
                const btnPrint = document.getElementById("btn-reader-print");
                const themes = ["day", "night", "sepia", "dark-sepia"];
                const results = {};
                
                function parseRgb(colorStr) {
                    const match = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
                    if (!match) return [0, 0, 0];
                    return [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])];
                }
                
                function getLuminance(rgb) {
                    const a = rgb.map(v => {
                        v /= 255;
                        return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
                    });
                    return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
                }
                
                function getContrastRatio(rgb1, rgb2) {
                    const l1 = getLuminance(rgb1);
                    const l2 = getLuminance(rgb2);
                    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
                }
                
                for (const theme of themes) {
                    window.app.setReadingTheme(theme);
                    // Allow CSS transition on .overflow-menu-item to settle
                    await new Promise(r => setTimeout(r, 200));
                    
                    const menuStyle = window.getComputedStyle(menu);
                    const itemStyle = window.getComputedStyle(btnPrint);
                    
                    const bgRgb = parseRgb(menuStyle.backgroundColor);
                    const textRgb = parseRgb(itemStyle.color);
                    const ratio = getContrastRatio(bgRgb, textRgb);
                    
                    results[theme] = {
                        bgColor: menuStyle.backgroundColor,
                        textColor: itemStyle.color,
                        contrastRatio: Math.round(ratio * 100) / 100
                    };
                }
                
                window.app.closeReader();
                return results;
            })()
        """)
        for theme, data in res.items():
            ratio = data["contrastRatio"]
            # WCAG AA requires at least 4.5:1; WCAG AAA requires 7.0:1
            self.assertGreaterEqual(
                ratio, 4.5,
                f"Theme '{theme}' contrast ratio {ratio}:1 is below WCAG AA threshold 4.5:1 (bg: {data['bgColor']}, text: {data['textColor']})"
            )

    def test_adv_ux_03_overflow_focus_restoration_and_reader_reset(self):
        """Feature 11: Focus restoration on Escape, clicking item closes menu, and closeReader reset."""
        res = self.client.eval_js("""
            (() => {
                const books = window.db.getBooks();
                if (books.length > 0) window.app.openBook(books[0]);
                
                const btnOverflow = document.getElementById("btn-reader-overflow");
                const menu = document.getElementById("reader-overflow-menu");
                const btnPrint = document.getElementById("btn-reader-print");
                
                // 1. Open menu and verify focus restoration on Escape
                btnOverflow.click();
                const opened = menu.classList.contains("open");
                
                // Dispatch Escape
                const escEvent = new KeyboardEvent("keydown", { key: "Escape", bubbles: true, cancelable: true });
                document.dispatchEvent(escEvent);
                
                const closedOnEsc = !menu.classList.contains("open");
                const focusRestored = (document.activeElement === btnOverflow);
                const readerStillOpen = (window.app.isReading === true);
                
                // 2. Click item closes menu
                btnOverflow.click();
                btnPrint.click();
                const closedOnItemClick = !menu.classList.contains("open");
                
                // Dismiss print modal if shown
                const printModal = document.getElementById("modal-print");
                if (printModal) printModal.style.display = "none";
                
                // 3. Reset upon closeReader
                btnOverflow.click();
                const openBeforeCloseReader = menu.classList.contains("open");
                window.app.closeReader();
                const closedAfterCloseReader = !menu.classList.contains("open") && 
                                              btnOverflow.getAttribute("aria-expanded") === "false";
                
                return {
                    opened, closedOnEsc, focusRestored, readerStillOpen,
                    closedOnItemClick, openBeforeCloseReader, closedAfterCloseReader
                };
            })()
        """)
        self.assertTrue(res["opened"], "Menu should open")
        self.assertTrue(res["closedOnEsc"], "Menu should close on Escape")
        self.assertTrue(res["focusRestored"], "Focus must be restored to #btn-reader-overflow on Escape dismissal")
        self.assertTrue(res["readerStillOpen"], "Reader must remain active on menu Escape dismissal")
        self.assertTrue(res["closedOnItemClick"], "Clicking an item inside overflow menu must dismiss it")
        self.assertTrue(res["closedAfterCloseReader"], "Closing reader must reset overflow menu state to closed")

    def test_adv_ux_04_header_balance_and_canonical_category(self):
        """Feature 12: Visual balance in header and canonical sidebar category button verification."""
        res = self.client.eval_js("""
            (() => {
                // Check header
                const addFolderInHeader = document.getElementById("btn-add-folder");
                const headerLeft = document.querySelector("#library-header .header-left");
                const btnAddBook = document.getElementById("btn-add-book");
                const searchBox = document.querySelector(".search-container");
                
                const headerLeftStyle = window.getComputedStyle(headerLeft);
                const hasCleanGap = headerLeftStyle.gap !== "" && headerLeftStyle.display === "flex";
                
                // Check sidebar canonical button
                const btnCategorySidebar = document.getElementById("btn-add-category-sidebar");
                const sidebarBtnExists = !!btnCategorySidebar;
                const sidebarBtnVisible = sidebarBtnExists && 
                                          window.getComputedStyle(btnCategorySidebar).display !== "none";
                const sidebarBtnText = sidebarBtnExists ? btnCategorySidebar.innerText.trim() : "";
                
                return {
                    headerRemoved: (addFolderInHeader === null),
                    hasCleanGap,
                    sidebarBtnExists,
                    sidebarBtnVisible,
                    sidebarBtnText
                };
            })()
        """)
        self.assertTrue(res["headerRemoved"], "#btn-add-folder must be completely absent from header DOM")
        self.assertTrue(res["hasCleanGap"], "#library-header .header-left must use clean flex gap layout")
        self.assertTrue(res["sidebarBtnExists"], "#btn-add-category-sidebar must exist in sidebar")
        self.assertTrue(res["sidebarBtnVisible"], "#btn-add-category-sidebar must be visible")
        self.assertIn("Add Category", res["sidebarBtnText"], "Sidebar category button text must be 'Add Category'")

    def test_adv_ux_05_integrity_and_anti_cheat_audit(self):
        """Integrity: Ensure implementation uses genuine logic and no mock short-circuits."""
        with open(os.path.join(APP_DIR, "app.js"), "r", encoding="utf-8") as f:
            app_code = f.read()
        with open(os.path.join(APP_DIR, "index.html"), "r", encoding="utf-8") as f:
            html_code = f.read()

        # Audit for hardcoded test intercepts
        self.assertNotIn("__FOLIO_TEST_MOCK__", app_code)
        self.assertNotIn("bypass_m3", app_code)
        self.assertNotIn("mock_overflow", app_code)

        # Audit genuine localStorage implementation
        self.assertIn("localStorage.setItem(\"foliohaven_formats_collapsed\"", app_code)
        self.assertIn("localStorage.getItem(\"foliohaven_formats_collapsed\"", app_code)

        # Audit genuine overflow toggling and focus restoration
        self.assertIn("btnOver.focus()", app_code)
        self.assertIn("aria-expanded", app_code)


if __name__ == "__main__":
    unittest.main()
