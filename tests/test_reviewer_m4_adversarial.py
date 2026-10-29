"""
Test Suite: Reviewer M4 Adversarial Stress & Integrity Suite
Author: reviewer_m4_1
Focus:
- Adversarial print delegation (exceptions in window.print, rapid-fire triggers, menu auto-closing)
- Print media rules robustness (@media print chrome suppression and canvas expansion)
- Token consistency & computed style audit (light/dark theme thumbnail background)
- Inline style migration completeness & dynamic runtime style non-interference
- Anti-facade and integrity verification
"""

import os
import sys
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


class TestReviewerM4Adversarial(unittest.TestCase):
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

        cls.port = 9335
        cls.user_data_dir = tempfile.mkdtemp(prefix="chrome_reviewer_m4_")
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

        import time
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

    def test_adv01_print_delegation_resilience_under_fault_injection(self):
        """ADV-01: Verify delegatePrint resilience when window.print throws an error."""
        res = self.client.eval_js("""
            (() => {
                const origPrint = window.print;
                let errorLogged = false;
                const origWarn = console.warn;
                console.warn = (...args) => {
                    errorLogged = true;
                    origWarn(...args);
                };

                // Inject fault into window.print
                window.print = () => {
                    throw new DOMException("The document is sandboxed and does not have the 'allow-modals' flag.", "NotAllowedError");
                };

                const book = window.db.getBooks()[0];
                window.app.openBook(book);

                // Open overflow menu
                window.app.openReaderOverflowMenu();
                const menu = document.getElementById("reader-overflow-menu");

                // Trigger print
                let survived = false;
                try {
                    window.app.delegatePrint();
                    survived = true;
                } catch (e) {
                    survived = false;
                }

                const menuClosed = !menu.classList.contains("open");
                const modalVisible = (document.getElementById("modal-print").style.display === "flex");

                // Restore
                window.print = origPrint;
                console.warn = origWarn;
                window.app.closeReader();

                return { survived, menuClosed, errorLogged, modalVisible };
            })()
        """)
        self.assertTrue(res["survived"], "delegatePrint() must not throw unhandled exception on window.print error")
        self.assertTrue(res["menuClosed"], "Overflow menu must close even if window.print throws")
        self.assertTrue(res["errorLogged"], "Console warning must be logged when window.print fails")
        self.assertFalse(res["modalVisible"], "modal-print must NOT pop up")

    def test_adv02_rapid_fire_print_and_preserved_modal_defenses(self):
        """ADV-02: Rapid-fire print calls (50x) & legacy modal event bindings."""
        res = self.client.eval_js("""
            (() => {
                let callCount = 0;
                const origPrint = window.print;
                window.print = () => { callCount++; };

                const book = window.db.getBooks()[0];
                window.app.openBook(book);

                // Rapid 50 calls
                for (let i = 0; i < 50; i++) {
                    window.app.delegatePrint();
                }

                // Verify preserved modal buttons
                const modalPrint = document.getElementById("modal-print");
                modalPrint.style.display = "flex"; // simulate legacy test forcing modal open
                
                // Click close print
                document.getElementById("btn-close-print").click();
                const closedByBtnClose = (modalPrint.style.display === "none");

                modalPrint.style.display = "flex";
                document.getElementById("btn-cancel-print").click();
                const closedByBtnCancel = (modalPrint.style.display === "none");

                modalPrint.style.display = "flex";
                document.getElementById("btn-confirm-print").click();
                const closedByBtnConfirm = (modalPrint.style.display === "none");

                window.print = origPrint;
                window.app.closeReader();

                return {
                    callCount,
                    closedByBtnClose,
                    closedByBtnCancel,
                    closedByBtnConfirm
                };
            })()
        """)
        self.assertEqual(res["callCount"], 51, "50 rapid delegatePrint() + 1 confirmPrint() must execute 51 times")
        self.assertTrue(res["closedByBtnClose"], "#btn-close-print must close #modal-print")
        self.assertTrue(res["closedByBtnCancel"], "#btn-cancel-print must close #modal-print")
        self.assertTrue(res["closedByBtnConfirm"], "#btn-confirm-print must close #modal-print and delegate")

    def test_adv03_media_print_stylesheet_integrity(self):
        """ADV-03: Verify CSS rules for @media print hide application chrome completely."""
        with open(os.path.join(APP_DIR, "styles.css"), "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn("@media print", css, "Missing @media print in styles.css")
        media_section = css.split("@media print")[1]

        # Crucial elements that MUST be hidden in print preview
        chrome_selectors = [
            "#sidebar",
            "#reader-toolbar",
            "#reader-footer",
            ".margin-click-zone",
            "#dim-overlay",
            "#operations-footer",
            ".drawer",
            ".modal-overlay",
            "#undo-toast",
            "#quick-settings-popover",
            "#reader-overflow-menu"
        ]
        for sel in chrome_selectors:
            self.assertIn(sel, media_section, f"Selector {sel} must be included in @media print hidden group")

        # Crucial layout rules that must unconstrain reading content
        self.assertIn("orphans: 3", media_section)
        self.assertIn("widows: 3", media_section)

    def test_adv04_token_hygiene_and_computed_colors(self):
        """ADV-04: Verify zero #e2e8f0 in styles.css and live computed surface color in both themes."""
        with open(os.path.join(APP_DIR, "styles.css"), "r", encoding="utf-8") as f:
            css = f.read()

        self.assertNotIn("#e2e8f0", css.lower(), "Zero occurrences of #e2e8f0 allowed in styles.css")

        res = self.client.eval_js("""
            (() => {
                const thumb = document.createElement("div");
                thumb.className = "card-thumb";
                document.body.appendChild(thumb);

                document.documentElement.removeAttribute("data-theme");
                const lightSurface = window.getComputedStyle(document.documentElement).getPropertyValue("--color-surface").trim();
                const lightThumbBg = window.getComputedStyle(thumb).backgroundColor;

                document.documentElement.setAttribute("data-theme", "dark");
                const darkSurface = window.getComputedStyle(document.documentElement).getPropertyValue("--color-surface").trim();
                const darkThumbBg = window.getComputedStyle(thumb).backgroundColor;

                document.documentElement.removeAttribute("data-theme");
                thumb.remove();

                return {
                    lightSurface,
                    lightThumbBg,
                    darkSurface,
                    darkThumbBg
                };
            })()
        """)
        self.assertEqual(res["lightSurface"], "#f5f7fa")
        self.assertEqual(res["lightThumbBg"], "rgb(245, 247, 250)")
        self.assertEqual(res["darkSurface"], "#20242c")
        self.assertEqual(res["darkThumbBg"], "rgb(32, 36, 44)")

    def test_adv05_inline_styles_scan_and_dynamic_runtime_immunity(self):
        """ADV-05: Strict audit of index.html style attributes and runtime dynamic stability."""
        with open(os.path.join(APP_DIR, "index.html"), "r", encoding="utf-8") as f:
            html = f.read()

        style_lines = [(i + 1, line.strip()) for i, line in enumerate(html.splitlines()) if 'style=' in line]
        self.assertEqual(len(style_lines), 1, f"Only 1 style= attribute permitted in index.html, found: {style_lines}")
        self.assertIn('id="modal-print"', style_lines[0][1], "The sole style attribute must be on modal-print")

        # Test that runtime modal toggling in app.js still works perfectly with dynamic styles
        res = self.client.eval_js("""
            (() => {
                let proceedClicked = false;
                window.app.showConfirmModal({
                    title: "Test Adversarial Confirm",
                    message: "Are you sure?",
                    proceedLabel: "Do It",
                    onProceed: () => { proceedClicked = true; }
                });

                const confirmModal = document.getElementById("modal-confirm");
                const displayWhileOpen = confirmModal.style.display;

                // Click proceed
                document.getElementById("btn-confirm-proceed").click();
                const displayAfterClose = confirmModal.style.display;

                // Test Undo Toast dynamic display
                let undoClicked = false;
                window.app.showUndoToast("Action done", () => { undoClicked = true; }, 3000);
                const toast = document.getElementById("undo-toast");
                const toastDisplayWhileOpen = toast.style.display;
                document.getElementById("btn-undo-action").click();
                const toastDisplayAfterClose = toast.style.display;

                return {
                    displayWhileOpen,
                    displayAfterClose,
                    proceedClicked,
                    toastDisplayWhileOpen,
                    toastDisplayAfterClose,
                    undoClicked
                };
            })()
        """)
        self.assertEqual(res["displayWhileOpen"], "flex", "Confirm modal must open with display: flex")
        self.assertEqual(res["displayAfterClose"], "none", "Confirm modal must close with display: none")
        self.assertTrue(res["proceedClicked"], "Confirm proceed callback must fire")
        self.assertEqual(res["toastDisplayWhileOpen"], "flex", "Undo toast must open with display: flex")
        self.assertEqual(res["toastDisplayAfterClose"], "none", "Undo toast must close with display: none")
        self.assertTrue(res["undoClicked"], "Undo callback must fire")


if __name__ == "__main__":
    unittest.main()
