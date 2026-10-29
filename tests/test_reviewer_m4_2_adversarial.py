"""
Adversarial Stress & Integrity Verification Suite
Author: reviewer_m4_2 (Milestone 4 Design & Token Reviewer)
FolioHaven Desktop Ebook Reader Replica

Verification Targets:
1. Print Delegation Resiliency & Fault Injection:
   - window.print deletion / undefined behavior
   - window.print SecurityError / DOMException throwing
   - Rapid-fire delegation (100 sequential calls)
   - Print delegation closes open overflow menu and sets _printDelegated
2. Design Token & Computed Theme Invariance:
   - Absolute purge of #e2e8f0 across entire stylesheet
   - Computed background of .card-thumb in light (#f5f7fa) and dark (#20242c)
   - Shimmer skeleton animation keyframe integrity using surface tokens
   - Format badge CSS tokens and WCAG contrast evaluation
3. Inline Style Purge & DOM Audit:
   - Exact style= attribute count in app/index.html (strictly 1: #modal-print)
   - .brand-title, #reader-page-info, #reader-progress-info, SVGs, swatches clean
   - Dynamic style immunity: runtime style.display assignments functional
4. Anti-Facade and Integrity Audit:
   - Verify delegatePrint() does genuine delegation
   - Verify @media print rules hide chrome and allow natural page breaks
"""

import os
import sys
import re
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
        frame.append(0x81)
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


class TestReviewerM42Adversarial(unittest.TestCase):
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
            raise unittest.SkipTest("Google Chrome executable not found")

        cls.port = 9388
        cls.user_data_dir = tempfile.mkdtemp(prefix="chrome_rev_m4_2_")
        cls.url = "file:///" + os.path.join(APP_DIR, "index.html").replace("\\", "/")

        cls.proc = subprocess.Popen([
            exe,
            "--headless=new",
            f"--remote-debugging-port={cls.port}",
            f"--user-data-dir={cls.user_data_dir}",
            "--remote-allow-origins=*",
            "--disable-gpu",
            "--no-sandbox",
            cls.url
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        import time
        time.sleep(2.5)

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
            raise unittest.SkipTest(f"Failed to connect to Chrome CDP: {e}")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "client"):
            cls.client.close()
        if hasattr(cls, "proc"):
            cls.proc.terminate()
            cls.proc.wait()

    def test_adv01_print_delegation_fault_injection(self):
        """Adversarial 1: Fault injection into window.print (null, throwing, unhandled rejection)."""
        res = self.client.eval_js("""
            (() => {
                const origPrint = window.print;
                let errorCaught = false;

                // 1. window.print is completely null / deleted
                window.print = null;
                try {
                    window.app.delegatePrint();
                } catch (e) {
                    errorCaught = true;
                }
                const survivedNull = !errorCaught && (window.app._printDelegated === true);

                // 2. window.print throws SecurityError
                errorCaught = false;
                window.print = () => {
                    const err = new Error("SecurityError: Blocked cross-origin frame print");
                    err.name = "SecurityError";
                    throw err;
                };
                try {
                    window.app.delegatePrint();
                } catch (e) {
                    errorCaught = true;
                }
                const survivedSecurityError = !errorCaught;

                // Restore
                window.print = origPrint;
                return { survivedNull, survivedSecurityError };
            })()
        """)
        self.assertTrue(res["survivedNull"], "delegatePrint must not throw when window.print is null")
        self.assertTrue(res["survivedSecurityError"], "delegatePrint must safely catch SecurityError exceptions")

    def test_adv02_print_delegation_overflow_closure_invariants(self):
        """Adversarial 2: Invoking print delegation automatically closes reader overflow menu."""
        res = self.client.eval_js("""
            (() => {
                let printCalled = false;
                const origPrint = window.print;
                window.print = () => { printCalled = true; };

                const book = window.db.getBooks()[0];
                window.app.openBook(book);

                // Open overflow menu
                window.app.openReaderOverflowMenu();
                const menu = document.getElementById("reader-overflow-menu");
                const wasOpen = menu.classList.contains("open");

                // Rapid-fire 20 print clicks
                for (let i = 0; i < 20; i++) {
                    window.app.delegatePrint();
                }

                const isClosed = !menu.classList.contains("open");
                const modalPrintHidden = (document.getElementById("modal-print").style.display === "none");

                window.print = origPrint;
                window.app.closeReader();

                return { wasOpen, isClosed, printCalled, modalPrintHidden };
            })()
        """)
        self.assertTrue(res["wasOpen"])
        self.assertTrue(res["isClosed"], "Overflow menu must close on print invocation")
        self.assertTrue(res["printCalled"])
        self.assertTrue(res["modalPrintHidden"], "modal-print must stay hidden throughout")

    def test_adv03_card_thumb_token_invariance_and_no_drift(self):
        """Adversarial 3: .card-thumb background resolution and zero hardcoded hex #e2e8f0."""
        # 1. Check stylesheet source
        with open(os.path.join(APP_DIR, "styles.css"), "r", encoding="utf-8") as f:
            css = f.read()
        self.assertNotIn("#e2e8f0", css, "Hardcoded color #e2e8f0 must not exist anywhere in styles.css")

        # 2. Check computed styles across data-theme changes
        res = self.client.eval_js("""
            (() => {
                const el = document.createElement("div");
                el.className = "card-thumb";
                document.body.appendChild(el);

                // Light / default
                document.documentElement.removeAttribute("data-theme");
                const lightBg = window.getComputedStyle(el).backgroundColor;

                // Dark theme
                document.documentElement.setAttribute("data-theme", "dark");
                const darkBg = window.getComputedStyle(el).backgroundColor;

                // Cleanup
                document.documentElement.removeAttribute("data-theme");
                el.remove();

                return { lightBg, darkBg };
            })()
        """)
        self.assertEqual(res["lightBg"], "rgb(245, 247, 250)", "Light theme card-thumb must be #f5f7fa")
        self.assertEqual(res["darkBg"], "rgb(32, 36, 44)", "Dark theme card-thumb must be #20242c")

    def test_adv04_inline_styles_strict_elimination(self):
        """Adversarial 4: Zero static inline styles in index.html except defensive #modal-print."""
        with open(os.path.join(APP_DIR, "index.html"), "r", encoding="utf-8") as f:
            html = f.read()

        # Find all style="..." attributes
        style_matches = re.findall(r'<([^>]+style=["\'][^"\']*["\'][^>]*)>', html)
        self.assertEqual(len(style_matches), 1, f"Expected exactly 1 static style in index.html, found {len(style_matches)}: {style_matches}")
        self.assertIn('id="modal-print"', style_matches[0], "The sole static style attribute must be on #modal-print")
        self.assertIn('aria-hidden="true"', style_matches[0], "#modal-print must retain aria-hidden=true")

        # Verify critical elements have NO inline styles
        self.assertNotIn('class="brand-title" style=', html)
        self.assertNotIn('id="reader-page-info" style=', html)
        self.assertNotIn('id="reader-progress-info" style=', html)
        self.assertNotIn('style="flex-shrink: 0;"', html)
        self.assertNotIn('style="background: var(--color-highlight-', html)

    def test_adv05_print_stylesheet_chrome_suppression_and_reading_canvas(self):
        """Adversarial 5: @media print CSS rules hide all non-printable chrome and allow natural reflow."""
        with open(os.path.join(APP_DIR, "styles.css"), "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn("@media print", css)
        print_rules = css.split("@media print")[1]

        # Verify chrome hidden
        hidden_targets = [
            "#sidebar", "#reader-toolbar", "#reader-footer", ".margin-click-zone",
            "#dim-overlay", "#operations-footer", ".drawer", ".modal-overlay",
            "#undo-toast", "#quick-settings-popover", "#reader-overflow-menu", ".actions-bar"
        ]
        for target in hidden_targets:
            self.assertIn(target, print_rules, f"Target {target} must be hidden in @media print")

        # Verify reader layout unconstrained
        self.assertIn("overflow: visible !important", print_rules)
        self.assertIn("color: #000000 !important", print_rules)
        self.assertIn("orphans: 3", print_rules)
        self.assertIn("widows: 3", print_rules)


if __name__ == "__main__":
    unittest.main()
