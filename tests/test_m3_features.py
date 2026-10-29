"""
Test Suite: Milestone 3 Verification Suite
FolioHaven Desktop Ebook Reader
Features Covered:
- Feature 10: Collapsible Formats Section with persistence (foliohaven_formats_collapsed)
- Feature 11: Reader Toolbar Overflow Menu with theme compatibility and invariant preservation
- Feature 12: Header Duplicate Category Button Removal
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

class TestMilestone3Static(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(APP_DIR, "index.html"), "r", encoding="utf-8") as f:
            self.html = f.read()
        with open(os.path.join(APP_DIR, "styles.css"), "r", encoding="utf-8") as f:
            self.css = f.read()
        with open(os.path.join(APP_DIR, "app.js"), "r", encoding="utf-8") as f:
            self.app_js = f.read()

    def test_feature10_collapsible_formats_markup(self):
        """Feature 10: Formats section header, toggle, chevron, and collapsible container."""
        self.assertIn('id="sidebar-formats-toggle"', self.html, "Missing #sidebar-formats-toggle")
        self.assertIn('id="formats-chevron"', self.html, "Missing #formats-chevron")
        self.assertIn('id="formats-collapsible"', self.html, "Missing #formats-collapsible")
        self.assertIn('aria-controls="formats-collapsible"', self.html, "Missing aria-controls on toggle")
        self.assertIn('role="button"', self.html, "Missing role=button on toggle")
        self.assertIn('id="nav-formats-toggle"', self.html, "Missing #nav-formats-toggle inner span")
        
        # Verify format badge items remain inside
        for fmt in ["epub", "pdf", "mobi", "fb2", "cbz", "txt"]:
            self.assertIn(f'id="badge-format-{fmt}"', self.html, f"Missing badge-format-{fmt}")

    def test_feature10_collapsible_formats_css(self):
        """Feature 10: Formats section collapse styling, chevron rotation, tokens."""
        self.assertIn(".sidebar-section-header", self.css)
        self.assertIn(".sidebar-collapsible", self.css)
        self.assertIn(".sidebar-collapsible.collapsed", self.css)
        self.assertIn("transform: rotate(-90deg)", self.css)
        self.assertIn("var(--motion-base)", self.css)

    def test_feature10_collapsible_formats_js(self):
        """Feature 10: Persistence key, keyboard support, controller methods."""
        self.assertIn("initCollapsibleFormats", self.app_js)
        self.assertIn("foliohaven_formats_collapsed", self.app_js)
        self.assertIn("setFormatsCollapsed", self.app_js)
        self.assertIn("toggleFormatsCollapsed", self.app_js)

    def test_feature11_overflow_menu_markup(self):
        """Feature 11: Overflow menu markup preserving button IDs."""
        self.assertIn('id="reader-overflow-wrapper"', self.html)
        self.assertIn('id="btn-reader-overflow"', self.html)
        self.assertIn('id="reader-overflow-menu"', self.html)
        self.assertIn('aria-haspopup="true"', self.html)
        
        # Invariant checks: button IDs must be preserved
        self.assertIn('id="btn-reader-print"', self.html)
        self.assertIn('id="btn-reader-fullscreen"', self.html)
        self.assertIn('id="btn-reader-settings"', self.html)

    def test_feature11_overflow_menu_css(self):
        """Feature 11: Overflow menu styles using theme tokens."""
        self.assertIn(".reader-overflow-wrapper", self.css)
        self.assertIn("#btn-reader-overflow", self.css)
        self.assertIn(".reader-overflow-menu", self.css)
        self.assertIn(".overflow-menu-item", self.css)
        self.assertIn("var(--reader-surface", self.css)
        self.assertIn("var(--reader-border", self.css)
        self.assertIn("var(--reader-gutter", self.css)

    def test_feature11_overflow_menu_js(self):
        """Feature 11: Overflow toggle, outside click, Escape dismissal, closeReader reset."""
        self.assertIn("toggleReaderOverflowMenu", self.app_js)
        self.assertIn("openReaderOverflowMenu", self.app_js)
        self.assertIn("closeReaderOverflowMenu", self.app_js)
        self.assertIn("btn-reader-overflow", self.app_js)

    def test_feature12_header_category_removal(self):
        """Feature 12: Duplicate #btn-add-folder removed, canonical #btn-add-category-sidebar preserved."""
        self.assertNotIn('id="btn-add-folder"', self.html, "#btn-add-folder must be removed")
        self.assertIn('id="btn-add-category-sidebar"', self.html, "Canonical #btn-add-category-sidebar must exist")


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


class TestMilestone3LiveCDP(unittest.TestCase):
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

        cls.user_data_dir = tempfile.mkdtemp(prefix="folio_m3_test_")
        cls.port = 9335
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

    def test_live_collapsible_formats_toggle(self):
        """Live: Clicking #sidebar-formats-toggle collapses and expands with localStorage persistence."""
        res = self.client.eval_js("""
            (() => {
                localStorage.removeItem("foliohaven_formats_collapsed");
                window.app.initCollapsibleFormats();

                const toggle = document.getElementById("sidebar-formats-toggle");
                const collapsible = document.getElementById("formats-collapsible");
                
                const initExpanded = !collapsible.classList.contains("collapsed") && toggle.getAttribute("aria-expanded") === "true";
                
                // Click to collapse
                toggle.click();
                const afterCollapse = collapsible.classList.contains("collapsed") && 
                                      toggle.getAttribute("aria-expanded") === "false" &&
                                      localStorage.getItem("foliohaven_formats_collapsed") === "true";
                
                // Click to expand
                toggle.click();
                const afterExpand = !collapsible.classList.contains("collapsed") && 
                                    toggle.getAttribute("aria-expanded") === "true" &&
                                    localStorage.getItem("foliohaven_formats_collapsed") === "false";
                
                return { initExpanded, afterCollapse, afterExpand };
            })()
        """)
        self.assertTrue(res["initExpanded"], "Initial state should be expanded")
        self.assertTrue(res["afterCollapse"], "Section should collapse after click and persist 'true'")
        self.assertTrue(res["afterExpand"], "Section should expand after click and persist 'false'")

    def test_live_collapsible_formats_keyboard(self):
        """Live: Pressing Enter or Space on #sidebar-formats-toggle toggles state."""
        res = self.client.eval_js("""
            (() => {
                const toggle = document.getElementById("sidebar-formats-toggle");
                const collapsible = document.getElementById("formats-collapsible");
                
                // Reset to expanded
                window.app.setFormatsCollapsed(false, true);
                
                // Trigger Enter key
                const enterEvent = new KeyboardEvent("keydown", { key: "Enter", bubbles: true });
                toggle.dispatchEvent(enterEvent);
                const collapsedByEnter = collapsible.classList.contains("collapsed");
                
                // Trigger Space key
                const spaceEvent = new KeyboardEvent("keydown", { key: " ", bubbles: true });
                toggle.dispatchEvent(spaceEvent);
                const expandedBySpace = !collapsible.classList.contains("collapsed");
                
                return { collapsedByEnter, expandedBySpace };
            })()
        """)
        self.assertTrue(res["collapsedByEnter"], "Enter key should collapse section")
        self.assertTrue(res["expandedBySpace"], "Space key should expand section")

    def test_live_reader_overflow_menu_lifecycle(self):
        """Live: Overflow menu toggles, closes on outside click, and closes on Escape."""
        res = self.client.eval_js("""
            (() => {
                const books = window.db.getBooks();
                if (books.length > 0) window.app.openBook(books[0]);
                
                const btnOverflow = document.getElementById("btn-reader-overflow");
                const menu = document.getElementById("reader-overflow-menu");
                
                // 1. Initial state
                const initClosed = !menu.classList.contains("open") && btnOverflow.getAttribute("aria-expanded") === "false";
                
                // 2. Open via button click
                btnOverflow.click();
                const opened = menu.classList.contains("open") && btnOverflow.getAttribute("aria-expanded") === "true";
                
                // 3. Close via Escape
                const escEvent = new KeyboardEvent("keydown", { key: "Escape", bubbles: true, cancelable: true });
                document.dispatchEvent(escEvent);
                const closedByEsc = !menu.classList.contains("open") && window.app.isReading === true;
                
                // 4. Open again and close via outside click
                btnOverflow.click();
                const openedAgain = menu.classList.contains("open");
                document.body.click();
                const closedByOutside = !menu.classList.contains("open");
                
                // 5. Verify preserved buttons exist inside
                const hasPrint = !!document.getElementById("btn-reader-print");
                const hasFullscreen = !!document.getElementById("btn-reader-fullscreen");
                const hasSettings = !!document.getElementById("btn-reader-settings");
                
                window.app.closeReader();
                
                return {
                    initClosed, opened, closedByEsc, openedAgain, closedByOutside,
                    hasPrint, hasFullscreen, hasSettings
                };
            })()
        """)
        self.assertTrue(res["initClosed"], "Overflow menu should initially be closed")
        self.assertTrue(res["opened"], "Overflow menu should open on trigger click")
        self.assertTrue(res["closedByEsc"], "Escape should close overflow menu without exiting reader")
        self.assertTrue(res["openedAgain"], "Overflow menu should open again")
        self.assertTrue(res["closedByOutside"], "Outside click should close overflow menu")
        self.assertTrue(res["hasPrint"] and res["hasFullscreen"] and res["hasSettings"], "Preserved inner button IDs must exist")


if __name__ == "__main__":
    unittest.main()
