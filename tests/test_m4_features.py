"""
Test Suite: Milestone 4 Verification Suite
FolioHaven Desktop Ebook Reader
Features Covered:
- Feature 13: Native Print Delegation (window.print() invocation & @media print CSS)
- Feature 14: Card Thumbnail Token Migration (.card-thumb var(--color-surface))
- Feature 15: Inline Styles Migration (brand title, reader info, drawers, modals to CSS)
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


class TestMilestone4Static(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(APP_DIR, "index.html"), "r", encoding="utf-8") as f:
            self.html = f.read()
        with open(os.path.join(APP_DIR, "styles.css"), "r", encoding="utf-8") as f:
            self.css = f.read()
        with open(os.path.join(APP_DIR, "app.js"), "r", encoding="utf-8") as f:
            self.app_js = f.read()

    def test_feature13_print_delegation_markup(self):
        """Feature 13: #modal-print retained in DOM defensively with style=display: none."""
        self.assertIn('id="modal-print"', self.html, "Missing #modal-print in DOM")
        self.assertIn('aria-hidden="true"', self.html, "Missing aria-hidden on #modal-print")
        self.assertIn('id="btn-reader-print"', self.html, "Missing #btn-reader-print in DOM")
        self.assertIn('id="btn-confirm-print"', self.html, "Missing #btn-confirm-print in DOM")

    def test_feature13_print_delegation_js(self):
        """Feature 13: delegatePrint method, print delegation handler, and Ctrl+P binding."""
        self.assertIn("delegatePrint()", self.app_js, "Missing delegatePrint method in app.js")
        self.assertIn("window.print()", self.app_js, "Missing window.print() call in delegatePrint")
        self.assertIn('document.getElementById("btn-reader-print").addEventListener("click"', self.app_js)
        self.assertIn('this.delegatePrint();', self.app_js)
        # Ctrl+P shortcut delegation
        self.assertIn('e.ctrlKey && e.key.toLowerCase() === "p"', self.app_js)

    def test_feature13_print_media_css(self):
        """Feature 13: @media print CSS rules hiding chrome and unconstraining reading canvas."""
        self.assertIn("@media print", self.css, "Missing @media print in styles.css")
        # Ensure non-printable chrome is hidden
        print_section = self.css.split("@media print")[1]
        self.assertIn("#sidebar", print_section)
        self.assertIn("#reader-toolbar", print_section)
        self.assertIn("#reader-footer", print_section)
        self.assertIn(".margin-click-zone", print_section)
        self.assertIn(".modal-overlay", print_section)
        self.assertIn("#undo-toast", print_section)
        self.assertIn("#quick-settings-popover", print_section)
        self.assertIn("#reader-overflow-menu", print_section)
        self.assertIn("display: none !important", print_section)
        # Ensure layout container unconstrained
        self.assertIn("#reader-canvas", print_section)
        self.assertIn("#reader-book-content", print_section)
        self.assertIn(".two-column-spread", print_section)
        self.assertIn(".reflow-para", print_section)
        self.assertIn("orphans: 3", print_section)
        self.assertIn("widows: 3", print_section)

    def test_feature14_card_thumb_token(self):
        """Feature 14: .card-thumb uses var(--color-surface) and #e2e8f0 is removed."""
        self.assertNotIn("#e2e8f0", self.css, "Hardcoded color #e2e8f0 must not exist in styles.css")
        self.assertIn("background-color: var(--color-surface);", self.css,
                      ".card-thumb must use background-color: var(--color-surface);")
        # Format badges tokenization
        self.assertIn(".badge-epub { background: #ffedd5; color: var(--color-accent); }", self.css)
        self.assertIn(".badge-pdf  { background: #ffebe6; color: var(--color-danger); }", self.css)
        self.assertIn(".badge-fb2  { background: #e6f9f0; color: var(--color-success); }", self.css)
        self.assertIn(".badge-txt  { background: #f0f3f8; color: var(--color-text-muted); }", self.css)

    def test_feature15_inline_styles_migrated(self):
        """Feature 15: Static inline styles migrated to CSS classes with tokens."""
        # Brand title
        self.assertNotIn('class="brand-title" style=', self.html, "brand-title must not have inline style")
        self.assertIn(".brand-title", self.css)
        self.assertIn("var(--color-sidebar-text)", self.css)

        # Reader page info & progress info
        self.assertNotIn('id="reader-page-info" style=', self.html, "reader-page-info must not have inline style")
        self.assertNotIn('id="reader-progress-info" style=', self.html, "reader-progress-info must not have inline style")
        self.assertIn('class="reader-page-info"', self.html, "reader-page-info element must have reader-page-info class")
        self.assertIn('class="reader-progress-info"', self.html, "reader-progress-info element must have reader-progress-info class")
        self.assertIn(".reader-page-info", self.css)
        self.assertIn(".reader-progress-info", self.css)

        # Navigation SVGs
        self.assertNotIn('style="flex-shrink: 0;"', self.html, "flex-shrink: 0 inline style must be migrated to CSS")
        self.assertIn(".nav-item .item-left svg", self.css)

        # Swatch buttons
        self.assertNotIn('style="background: var(--color-highlight-', self.html, "swatches must not have inline styles")

        # Book properties modal
        self.assertNotIn('id="prop-cover-preview" style=', self.html, "prop-cover-preview must not have inline style")
        self.assertNotIn('id="prop-cover-fallback" style=', self.html, "prop-cover-fallback must not have inline style")
        self.assertIn(".prop-cover-section", self.css)
        self.assertIn("#prop-cover-preview", self.css)
        self.assertIn("#prop-cover-fallback", self.css)

        # Only 1 style attribute in entire index.html (the defensive modal-print)
        style_matches = [line.strip() for line in self.html.splitlines() if 'style=' in line]
        self.assertEqual(len(style_matches), 1, f"Expected exactly 1 style= in index.html, found: {style_matches}")
        self.assertIn('id="modal-print"', style_matches[0], "The sole style= attribute must be on modal-print")


# --- Headless Chrome CDP Live Tests ---
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

            msg = json.loads(data.decode('utf-8'))
            if msg.get("id") == target_id:
                return msg

    def eval_js(self, expression):
        res = self.send_command("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        if "error" in res:
            raise RuntimeError(f"CDP error: {res['error']}")
        result = res.get("result", {}).get("result", {})
        if result.get("subtype") == "error":
            raise RuntimeError(f"JS execution error: {result.get('description')}")
        return result.get("value")

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


class TestMilestone4LiveCDP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
        exe = None
        for p in chrome_paths:
            if os.path.exists(p):
                exe = p
                break
        if not exe:
            raise unittest.SkipTest("Google Chrome executable not found for CDP live testing")

        cls.port = 9334
        cls.user_data_dir = tempfile.mkdtemp(prefix="chrome_test_m4_")
        cls.url = "file:///" + os.path.join(APP_DIR, "index.html").replace("\\", "/")

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

    def test_live_print_delegation_invokes_window_print(self):
        """Live: Clicking #btn-reader-print invokes window.print() and closes overflow menu."""
        res = self.client.eval_js("""
            (() => {
                let printCalled = false;
                const origPrint = window.print;
                window.print = () => { printCalled = true; };

                // Open reader with a book
                const book = window.db.getBooks()[0];
                window.app.openBook(book);

                // Open overflow menu
                window.app.openReaderOverflowMenu();
                const menu = document.getElementById("reader-overflow-menu");
                const wasOpen = menu.classList.contains("open");

                // Click print button
                document.getElementById("btn-reader-print").click();

                const isClosed = !menu.classList.contains("open");
                const modalVisible = (document.getElementById("modal-print").style.display === "flex");
                const delegated = !!window.app._printDelegated;

                window.print = origPrint;
                window.app.closeReader();

                return { wasOpen, isClosed, printCalled, modalVisible, delegated };
            })()
        """)
        self.assertTrue(res["wasOpen"], "Overflow menu should have opened")
        self.assertTrue(res["isClosed"], "Overflow menu should have closed after print click")
        self.assertTrue(res["printCalled"], "window.print() should have been called")
        self.assertTrue(res["delegated"], "window.app._printDelegated flag should be true")
        self.assertFalse(res["modalVisible"], "Redundant #modal-print should NOT be visible")

    def test_live_print_shortcut_ctrl_p(self):
        """Live: Pressing Ctrl+P in reader invokes window.print() directly."""
        res = self.client.eval_js("""
            (() => {
                let printCalled = false;
                const origPrint = window.print;
                window.print = () => { printCalled = true; };

                const book = window.db.getBooks()[0];
                window.app.openBook(book);

                window.app._printDelegated = false;
                const event = new KeyboardEvent("keydown", {
                    key: "p",
                    ctrlKey: true,
                    bubbles: true,
                    cancelable: true
                });
                window.dispatchEvent(event);

                const delegated = !!window.app._printDelegated;
                const modalVisible = (document.getElementById("modal-print").style.display === "flex");

                window.print = origPrint;
                window.app.closeReader();

                return { printCalled, delegated, modalVisible };
            })()
        """)
        self.assertTrue(res["printCalled"], "Ctrl+P shortcut should have called window.print()")
        self.assertTrue(res["delegated"], "window.app._printDelegated should be true after Ctrl+P")
        self.assertFalse(res["modalVisible"], "modal-print should remain hidden on Ctrl+P")

    def test_live_card_thumb_token_color(self):
        """Live: .card-thumb background color matches var(--color-surface) in light and dark mode."""
        res = self.client.eval_js("""
            (() => {
                document.documentElement.removeAttribute("data-theme");
                const testThumb = document.createElement("div");
                testThumb.className = "card-thumb";
                document.body.appendChild(testThumb);

                const lightBg = window.getComputedStyle(testThumb).backgroundColor;

                // Toggle dark mode
                document.documentElement.setAttribute("data-theme", "dark");
                const darkBg = window.getComputedStyle(testThumb).backgroundColor;

                // Reset theme & cleanup
                document.documentElement.removeAttribute("data-theme");
                testThumb.remove();

                return { lightBg, darkBg };
            })()
        """)
        # Light surface is #f5f7fa -> rgb(245, 247, 250)
        # Dark surface is #20242c -> rgb(32, 36, 44)
        self.assertEqual(res["lightBg"], "rgb(245, 247, 250)", "Light theme thumbnail background should match --color-surface")
        self.assertEqual(res["darkBg"], "rgb(32, 36, 44)", "Dark theme thumbnail background should match dark --color-surface")

    def test_live_brand_and_reader_info_classes(self):
        """Live: .brand-title and reader info have no inline style overrides."""
        res = self.client.eval_js("""
            (() => {
                const brand = document.querySelector(".brand-title");
                const pageInfo = document.getElementById("reader-page-info");
                const progInfo = document.getElementById("reader-progress-info");

                return {
                    brandStyle: brand ? brand.getAttribute("style") : null,
                    pageInfoStyle: pageInfo ? pageInfo.getAttribute("style") : null,
                    progInfoStyle: progInfo ? progInfo.getAttribute("style") : null,
                    pageInfoHasClass: pageInfo ? pageInfo.classList.contains("reader-page-info") : false,
                    progInfoHasClass: progInfo ? progInfo.classList.contains("reader-progress-info") : false
                };
            })()
        """)
        self.assertIsNone(res["brandStyle"], "brand-title should not have inline style attribute")
        self.assertIsNone(res["pageInfoStyle"], "reader-page-info should not have inline style attribute")
        self.assertIsNone(res["progInfoStyle"], "reader-progress-info should not have inline style attribute")
        self.assertTrue(res["pageInfoHasClass"], "reader-page-info should have reader-page-info class")
        self.assertTrue(res["progInfoHasClass"], "reader-progress-info should have reader-progress-info class")


if __name__ == "__main__":
    unittest.main()
