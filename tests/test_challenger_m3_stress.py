"""
Adversarial Stress Test Suite for Milestone 3 (Phase 3: Interface Distillation)
FolioHaven Ebook Reader Replica
Author: challenger_m3_1 (Milestone 3 Stress Challenger)

Stress Test Scenarios:
1. TC-M3-STRESS-01: Formats Section 100x Rapid Toggling, Keyboard & Sub-element Bubbling Sync
2. TC-M3-STRESS-02: LocalStorage Resilience, Reload Persistence & Fault Injection
3. TC-M3-STRESS-03: Reader Overflow Menu Lifecycle, 100x Stress, Outside Clicks, Escape & Listener Invariants
4. TC-M3-STRESS-04: Preserved Button IDs Backward Compatibility & Category Consolidation
"""

import os
import sys
import time
import json
import socket
import subprocess
import tempfile
import urllib.request
from pathlib import Path


class CDPClient:
    def __init__(self, host, port, path):
        self.sock = socket.create_connection((host, port), timeout=15)
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode('utf-8'))
        resp = self.sock.recv(4096).decode('utf-8', errors='ignore')
        if "101" not in resp:
            raise ConnectionError(f"WebSocket handshake failed: {resp}")
        self._req_id = 0

    def send_command(self, method, params=None):
        self._req_id += 1
        msg = json.dumps({"id": self._req_id, "method": method, "params": params or {}})
        payload = msg.encode('utf-8')
        frame = bytearray([0x81])
        length = len(payload)
        if length <= 125:
            frame.append(0x80 | length)
        elif length <= 65535:
            frame.append(0x80 | 126)
            frame.extend(length.to_bytes(2, 'big'))
        else:
            frame.append(0x80 | 127)
            frame.extend(length.to_bytes(8, 'big'))

        mask = b'\x12\x34\x56\x78'
        frame.extend(mask)
        masked = bytearray(payload)
        for i in range(len(masked)):
            masked[i] ^= mask[i % 4]
        frame.extend(masked)

        self.sock.sendall(frame)

        while True:
            resp = self._read_frame()
            if not resp:
                continue
            try:
                res_json = json.loads(resp.decode('utf-8'))
                if res_json.get("id") == self._req_id:
                    return res_json.get("result", {})
            except Exception:
                pass

    def _read_frame(self):
        head = self.sock.recv(2)
        if len(head) < 2:
            return None
        b1, b2 = head[0], head[1]
        length = b2 & 0x7F
        if length == 126:
            length = int.from_bytes(self.sock.recv(2), 'big')
        elif length == 127:
            length = int.from_bytes(self.sock.recv(8), 'big')

        payload = bytearray()
        while len(payload) < length:
            chunk = self.sock.recv(length - len(payload))
            if not chunk:
                break
            payload.extend(chunk)
        return payload

    def eval_js(self, expression):
        res = self.send_command("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        val = res.get("result", {}).get("value")
        exc = res.get("exceptionDetails")
        if exc:
            raise RuntimeError(f"JS Error: {exc}")
        return val

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


def run_m3_stress_suite():
    print("=" * 76)
    print("  FOLIOHAVEN CHALLENGER M3: EMPIRICAL STRESS & ADVERSARIAL SUITE     ")
    print("=" * 76)

    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
    app_url = f"file:///{app_dir.replace('\\', '/')}/index.html"
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]
    chrome_path = next((p for p in chrome_paths if os.path.exists(p)), None)
    if not chrome_path:
        print("[SKIP] Chrome executable not found")
        return False

    port = 9338
    temp_dir = tempfile.mkdtemp(prefix="foliohaven_m3_stress_")

    chrome_cmd = [
        chrome_path,
        "--headless=new",
        f"--user-data-dir={temp_dir}",
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        "--disable-gpu",
        "--no-sandbox",
        "--allow-file-access-from-files",
        app_url
    ]
    proc = subprocess.Popen(chrome_cmd)
    time.sleep(2.0)

    ws_client = None
    results = []

    def test(test_id, description, fn):
        try:
            fn()
            print(f"  [PASS] {test_id}: {description}")
            results.append((test_id, description, "PASS", None))
        except Exception as e:
            print(f"  [FAIL] {test_id}: {description} -> {e}")
            results.append((test_id, description, "FAIL", str(e)))

    try:
        req = urllib.request.urlopen(f"http://localhost:{port}/json", timeout=5)
        tabs = json.loads(req.read().decode())
        page_tabs = [t for t in tabs if t.get("type") == "page" and "app/index.html" in t.get("url", "")]
        tab = page_tabs[0] if page_tabs else tabs[0]
        ws_url = tab["webSocketDebuggerUrl"]
        path = ws_url.split(f"localhost:{port}")[1]
        ws_client = CDPClient("localhost", port, path)
        ws_client.send_command("Runtime.enable")
        time.sleep(0.5)

        # ----------------------------------------------------------------------
        # TC-M3-STRESS-01: Formats Section 100x Rapid Toggling & ARIA/DOM State Sync
        # ----------------------------------------------------------------------
        def t_stress_01():
            # Initial setup: ensure expanded
            ws_client.eval_js("""
                (function() {
                    window.app.setFormatsCollapsed(false, true);
                })()
            """)

            # 1. 100 rapid programmatic clicks on #sidebar-formats-toggle
            sync_errors = ws_client.eval_js("""
                (function() {
                    const toggle = document.getElementById("sidebar-formats-toggle");
                    const collapsible = document.getElementById("formats-collapsible");
                    const errors = [];

                    for (let i = 0; i < 100; i++) {
                        toggle.click();
                        const expectedCollapsed = (i % 2 === 0); // first click collapses

                        const isCollapsibleCollapsed = collapsible.classList.contains("collapsed");
                        const isToggleCollapsed = toggle.classList.contains("collapsed");
                        const ariaExpanded = toggle.getAttribute("aria-expanded");
                        const lsVal = localStorage.getItem("foliohaven_formats_collapsed");

                        if (isCollapsibleCollapsed !== expectedCollapsed) {
                            errors.push(`Iteration ${i}: collapsible.collapsed expected ${expectedCollapsed}, got ${isCollapsibleCollapsed}`);
                            break;
                        }
                        if (isToggleCollapsed !== expectedCollapsed) {
                            errors.push(`Iteration ${i}: toggle.collapsed expected ${expectedCollapsed}, got ${isToggleCollapsed}`);
                            break;
                        }
                        const expectedAria = expectedCollapsed ? "false" : "true";
                        if (ariaExpanded !== expectedAria) {
                            errors.push(`Iteration ${i}: aria-expanded expected ${expectedAria}, got ${ariaExpanded}`);
                            break;
                        }
                        const expectedLs = expectedCollapsed ? "true" : "false";
                        if (lsVal !== expectedLs) {
                            errors.push(`Iteration ${i}: localStorage expected ${expectedLs}, got ${lsVal}`);
                            break;
                        }
                    }
                    return errors;
                })()
            """)
            assert len(sync_errors) == 0, f"Sync errors during 100x rapid clicks: {sync_errors}"

            # After 100 clicks, state must be expanded again
            final_expanded = ws_client.eval_js('document.getElementById("sidebar-formats-toggle").getAttribute("aria-expanded") === "true"')
            assert final_expanded, "After 100 clicks, state did not return to expanded"

            # 2. 50 rapid alternating Enter & Space keyboard events
            key_errors = ws_client.eval_js("""
                (function() {
                    const toggle = document.getElementById("sidebar-formats-toggle");
                    const collapsible = document.getElementById("formats-collapsible");
                    const errors = [];

                    for (let i = 0; i < 50; i++) {
                        const key = (i % 2 === 0) ? "Enter" : " ";
                        toggle.dispatchEvent(new KeyboardEvent("keydown", { key: key, bubbles: true, cancelable: true }));
                        const expectedCollapsed = (i % 2 === 0); // first key collapses

                        const isCollapsibleCollapsed = collapsible.classList.contains("collapsed");
                        const ariaExpanded = toggle.getAttribute("aria-expanded");
                        const expectedAria = expectedCollapsed ? "false" : "true";

                        if (isCollapsibleCollapsed !== expectedCollapsed || ariaExpanded !== expectedAria) {
                            errors.push(`Key iteration ${i} (${key}): collapsed=${isCollapsibleCollapsed}, aria=${ariaExpanded}, expectedCollapsed=${expectedCollapsed}`);
                            break;
                        }
                    }
                    return errors;
                })()
            """)
            assert len(key_errors) == 0, f"Keyboard toggle errors: {key_errors}"

            # 3. Sub-element bubbling verification:
            # Click directly on chevron icon and title span. Each must toggle exactly once.
            sub_errors = ws_client.eval_js("""
                (function() {
                    const chevron = document.getElementById("formats-chevron");
                    const titleSpan = document.getElementById("nav-formats-toggle");
                    const collapsible = document.getElementById("formats-collapsible");
                    const errors = [];

                    for (let i = 0; i < 20; i++) {
                        const before = collapsible.classList.contains("collapsed");
                        chevron.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
                        const after = collapsible.classList.contains("collapsed");
                        if (after === before) {
                            errors.push(`Chevron click iteration ${i} failed to toggle state`);
                            break;
                        }
                    }

                    for (let i = 0; i < 20; i++) {
                        const before = collapsible.classList.contains("collapsed");
                        titleSpan.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
                        const after = collapsible.classList.contains("collapsed");
                        if (after === before) {
                            errors.push(`TitleSpan click iteration ${i} failed to toggle state`);
                            break;
                        }
                    }
                    return errors;
                })()
            """)
            assert len(sub_errors) == 0, f"Sub-element click bubbling errors: {sub_errors}"

        test("TC-M3-STRESS-01", "Formats Section 100x Rapid Toggling, Keyboard & Sub-element Bubbling Sync", t_stress_01)

        # ----------------------------------------------------------------------
        # TC-M3-STRESS-02: LocalStorage Resilience, Reload Persistence & Fault Injection
        # ----------------------------------------------------------------------
        def t_stress_02():
            # 1. Clean slate test: localStorage empty -> defaults to expanded
            clean_res = ws_client.eval_js("""
                (function() {
                    localStorage.removeItem("foliohaven_formats_collapsed");
                    window.app.initCollapsibleFormats();
                    const toggle = document.getElementById("sidebar-formats-toggle");
                    const collapsible = document.getElementById("formats-collapsible");
                    return {
                        aria: toggle.getAttribute("aria-expanded"),
                        collapsedClass: collapsible.classList.contains("collapsed")
                    };
                })()
            """)
            assert clean_res["aria"] == "true", f"Clean slate expected aria-expanded='true', got {clean_res['aria']}"
            assert clean_res["collapsedClass"] is False, "Clean slate expected no .collapsed class"

            # 2. Simulated reload persistence (collapsed)
            col_res = ws_client.eval_js("""
                (function() {
                    localStorage.setItem("foliohaven_formats_collapsed", "true");
                    window.app.initCollapsibleFormats();
                    const toggle = document.getElementById("sidebar-formats-toggle");
                    const collapsible = document.getElementById("formats-collapsible");
                    return {
                        aria: toggle.getAttribute("aria-expanded"),
                        collapsibleCollapsed: collapsible.classList.contains("collapsed"),
                        toggleCollapsed: toggle.classList.contains("collapsed")
                    };
                })()
            """)
            assert col_res["aria"] == "false", f"Collapsed boot expected aria-expanded='false', got {col_res['aria']}"
            assert col_res["collapsibleCollapsed"] is True, "Collapsed boot expected collapsible to have .collapsed"
            assert col_res["toggleCollapsed"] is True, "Collapsed boot expected toggle to have .collapsed"

            # 3. Simulated reload persistence (expanded)
            exp_res = ws_client.eval_js("""
                (function() {
                    localStorage.setItem("foliohaven_formats_collapsed", "false");
                    window.app.initCollapsibleFormats();
                    const toggle = document.getElementById("sidebar-formats-toggle");
                    const collapsible = document.getElementById("formats-collapsible");
                    return {
                        aria: toggle.getAttribute("aria-expanded"),
                        collapsibleCollapsed: collapsible.classList.contains("collapsed"),
                        toggleCollapsed: toggle.classList.contains("collapsed")
                    };
                })()
            """)
            assert exp_res["aria"] == "true", f"Expanded boot expected aria-expanded='true', got {exp_res['aria']}"
            assert exp_res["collapsibleCollapsed"] is False, "Expanded boot expected collapsible NOT to have .collapsed"
            assert exp_res["toggleCollapsed"] is False, "Expanded boot expected toggle NOT to have .collapsed"

            # 4. Corrupted / Unexpected values fault injection
            corrupt_test = ws_client.eval_js("""
                (function() {
                    const corruptValues = ["corrupt_value", "1", "0", "TRUE", "{}", "[]", "null", "undefined", "NaN"];
                    const results = [];
                    for (const val of corruptValues) {
                        try {
                            localStorage.setItem("foliohaven_formats_collapsed", val);
                            window.app.initCollapsibleFormats();
                            const toggle = document.getElementById("sidebar-formats-toggle");
                            const collapsible = document.getElementById("formats-collapsible");
                            // For any non-'true' value, must gracefully default to expanded
                            const isCollapsed = collapsible.classList.contains("collapsed");
                            const aria = toggle.getAttribute("aria-expanded");
                            if (isCollapsed !== false || aria !== "true") {
                                results.push(`Value '${val}' failed: isCollapsed=${isCollapsed}, aria=${aria}`);
                            }
                        } catch (e) {
                            results.push(`Value '${val}' threw exception: ${e.message}`);
                        }
                    }
                    return results;
                })()
            """)
            assert len(corrupt_test) == 0, f"Corrupted values caused failure: {corrupt_test}"

            # 5. LocalStorage Exception Fault Tolerance (QuotaExceededError / SecurityError simulation)
            exception_test = ws_client.eval_js("""
                (function() {
                    const origSetItem = localStorage.setItem;
                    let errorCaught = false;
                    try {
                        // Mock localStorage.setItem to throw DOMException
                        localStorage.setItem = function() {
                            throw new DOMException("The quota has been exceeded.", "QuotaExceededError");
                        };

                        const toggle = document.getElementById("sidebar-formats-toggle");
                        const collapsible = document.getElementById("formats-collapsible");

                        // Toggle must still work visually without throwing unhandled exception
                        toggle.click();
                        const isCollapsedAfterClick = collapsible.classList.contains("collapsed");
                        return { ok: true, isCollapsed: isCollapsedAfterClick };
                    } catch (err) {
                        return { ok: false, error: err.message };
                    } finally {
                        localStorage.setItem = origSetItem;
                    }
                })()
            """)
            assert exception_test["ok"], f"QuotaExceededError simulation threw unhandled exception: {exception_test.get('error')}"

        test("TC-M3-STRESS-02", "LocalStorage Resilience, Reload Persistence & Fault Injection", t_stress_02)

        # ----------------------------------------------------------------------
        # TC-M3-STRESS-03: Reader Overflow Menu Lifecycle, 100x Stress, Outside Clicks, Escape & Listener Invariants
        # ----------------------------------------------------------------------
        def t_stress_03():
            # Seed a book if library is empty and open reader
            ws_client.eval_js("""
                (function() {
                    let books = window.db.getBooks();
                    if (!books || books.length === 0) {
                        window.db.addBook({
                            id: 'stress-book-m3',
                            title: 'M3 Stress Book',
                            author: 'Challenger',
                            format: 'EPUB',
                            content: 'Stress testing content for Reader Overflow Menu lifecycle.'
                        });
                        window.app.renderLibrary();
                        books = window.db.getBooks();
                    }
                    window.app.openBook(books[0]);
                })()
            """)
            time.sleep(0.3)

            # Verify reader screen is active
            reader_active = ws_client.eval_js('document.getElementById("reader-screen").style.display !== "none" && window.app.isReading === true')
            assert reader_active, "Reader screen failed to mount"

            # 1. 100x Rapid Toggling on #btn-reader-overflow
            overflow_stress_errors = ws_client.eval_js("""
                (function() {
                    const btn = document.getElementById("btn-reader-overflow");
                    const menu = document.getElementById("reader-overflow-menu");
                    const errors = [];

                    for (let i = 0; i < 100; i++) {
                        btn.click();
                        const expectedOpen = (i % 2 === 0); // first click opens
                        const isOpen = menu.classList.contains("open");
                        const aria = btn.getAttribute("aria-expanded");
                        const expectedAria = expectedOpen ? "true" : "false";

                        if (isOpen !== expectedOpen) {
                            errors.push(`Iteration ${i}: menu.open expected ${expectedOpen}, got ${isOpen}`);
                            break;
                        }
                        if (aria !== expectedAria) {
                            errors.push(`Iteration ${i}: aria-expanded expected ${expectedAria}, got ${aria}`);
                            break;
                        }
                    }
                    // Ensure closed at the end
                    if (menu.classList.contains("open")) {
                        window.app.closeReaderOverflowMenu();
                    }
                    return errors;
                })()
            """)
            assert len(overflow_stress_errors) == 0, f"Overflow 100x rapid toggle errors: {overflow_stress_errors}"

            # 2. Outside Click Dismissal Stress (30 iterations)
            outside_click_errors = ws_client.eval_js("""
                (function() {
                    const btn = document.getElementById("btn-reader-overflow");
                    const menu = document.getElementById("reader-overflow-menu");
                    const canvas = document.getElementById("reader-canvas");
                    const errors = [];

                    for (let i = 0; i < 30; i++) {
                        window.app.openReaderOverflowMenu();
                        if (!menu.classList.contains("open")) {
                            errors.push(`Outside click cycle ${i}: failed to open`);
                            break;
                        }
                        // Click outside (on reader canvas)
                        canvas.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
                        if (menu.classList.contains("open")) {
                            errors.push(`Outside click cycle ${i}: failed to close on canvas click`);
                            break;
                        }
                        if (btn.getAttribute("aria-expanded") !== "false") {
                            errors.push(`Outside click cycle ${i}: aria-expanded not reset`);
                            break;
                        }
                    }
                    return errors;
                })()
            """)
            assert len(outside_click_errors) == 0, f"Outside click stress errors: {outside_click_errors}"

            # 3. Escape Key Dismissal: Menu Open vs Menu Closed
            # Case A: Menu Open + Escape -> Closes menu, focuses trigger, DOES NOT close reader
            esc_open_res = ws_client.eval_js("""
                (function() {
                    window.app.openReaderOverflowMenu();
                    const menu = document.getElementById("reader-overflow-menu");
                    const btn = document.getElementById("btn-reader-overflow");

                    // Dispatch Escape keydown on window
                    window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true, cancelable: true }));

                    const isMenuClosed = !menu.classList.contains("open");
                    const isReaderStillOpen = (window.app.isReading === true) && (document.getElementById("reader-screen").style.display !== "none");
                    const isButtonFocused = (document.activeElement === btn);

                    return {
                        isMenuClosed: isMenuClosed,
                        isReaderStillOpen: isReaderStillOpen,
                        isButtonFocused: isButtonFocused
                    };
                })()
            """)
            assert esc_open_res["isMenuClosed"], "Escape key did not close overflow menu"
            assert esc_open_res["isReaderStillOpen"], "Escape key erroneously closed reader when overflow menu was open"
            assert esc_open_res["isButtonFocused"], "Escape key did not restore focus to #btn-reader-overflow"

            # Case B: Menu Closed + Escape -> Closes reader screen
            esc_closed_res = ws_client.eval_js("""
                (function() {
                    window.app.closeReaderOverflowMenu();
                    window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true, cancelable: true }));

                    const isReaderClosed = (window.app.isReading === false) || (document.getElementById("reader-screen").style.display === "none");
                    return { isReaderClosed: isReaderClosed };
                })()
            """)
            assert esc_closed_res["isReaderClosed"], "Escape key with closed menu did not close reader screen"

            # Re-open reader for menu item checks
            ws_client.eval_js("window.app.openBook(window.db.getBooks()[0]);")
            time.sleep(0.2)

            # 4. Menu Item Clicks Auto-Dismissal
            item_dismiss_res = ws_client.eval_js("""
                (function() {
                    const menu = document.getElementById("reader-overflow-menu");

                    // Print item (delegates natively in M4, modal in M3)
                    window.app.openReaderOverflowMenu();
                    window.app._printDelegated = false;
                    document.getElementById("btn-reader-print").click();
                    const printClosed = !menu.classList.contains("open");
                    const printModalVisible = (document.getElementById("modal-print").style.display === "flex") || !!window.app._printDelegated;
                    if (document.getElementById("modal-print").style.display === "flex") {
                        document.getElementById("modal-print").style.display = "none";
                    }

                    // Settings item (opens quick-settings-popover)
                    window.app.openReaderOverflowMenu();
                    document.getElementById("btn-reader-settings").click();
                    const settingsClosed = !menu.classList.contains("open");
                    const settingsPopoverVisible = (document.getElementById("quick-settings-popover").style.display === "flex");
                    document.getElementById("quick-settings-popover").style.display = "none";

                    // Fullscreen item
                    window.app.openReaderOverflowMenu();
                    document.getElementById("btn-reader-fullscreen").click();
                    const fsClosed = !menu.classList.contains("open");

                    return {
                        printClosed: printClosed,
                        printModalVisible: printModalVisible,
                        settingsClosed: settingsClosed,
                        settingsPopoverVisible: settingsPopoverVisible,
                        fsClosed: fsClosed
                    };
                })()
            """)
            assert item_dismiss_res["printClosed"] and item_dismiss_res["printModalVisible"], "Print item click failed auto-dismiss or modal show"
            assert item_dismiss_res["settingsClosed"] and item_dismiss_res["settingsPopoverVisible"], "Settings item click failed auto-dismiss or popover show"
            assert item_dismiss_res["fsClosed"], "Fullscreen item click failed auto-dismiss"

            # 5. Listener Leakage Stress: Cycle openBook/closeReader 15 times
            leak_res = ws_client.eval_js("""
                (function() {
                    const book = window.db.getBooks()[0];
                    for (let i = 0; i < 15; i++) {
                        window.app.closeReader();
                        window.app.openBook(book);
                    }

                    // Test toggle after multiple cycles
                    const btn = document.getElementById("btn-reader-overflow");
                    const menu = document.getElementById("reader-overflow-menu");

                    btn.click();
                    const openedOnce = menu.classList.contains("open");
                    btn.click();
                    const closedOnce = !menu.classList.contains("open");

                    return { openedOnce: openedOnce, closedOnce: closedOnce };
                })()
            """)
            assert leak_res["openedOnce"] and leak_res["closedOnce"], "Repeated reader open/close cycles corrupted overflow listener behavior"

        test("TC-M3-STRESS-03", "Reader Overflow Menu Lifecycle, 100x Stress, Outside Clicks, Escape & Listener Invariants", t_stress_03)

        # ----------------------------------------------------------------------
        # TC-M3-STRESS-04: Preserved Button IDs Backward Compatibility & Category Consolidation
        # ----------------------------------------------------------------------
        def t_stress_04():
            # In reader view, ensure menu is closed
            compat_res = ws_client.eval_js("""
                (function() {
                    window.app.closeReaderOverflowMenu();
                    const menu = document.getElementById("reader-overflow-menu");

                    // Verify menu is visually hidden / closed
                    const isClosed = !menu.classList.contains("open");

                    // 1. Programmatic click on #btn-reader-print while menu closed
                    const btnPrint = document.getElementById("btn-reader-print");
                    window.app._printDelegated = false;
                    btnPrint.click();
                    const printModalVisible = (document.getElementById("modal-print").style.display === "flex") || !!window.app._printDelegated;
                    if (document.getElementById("modal-print").style.display === "flex") {
                        document.getElementById("modal-print").style.display = "none";
                    }

                    // 2. Programmatic click on #btn-reader-settings while menu closed
                    const btnSettings = document.getElementById("btn-reader-settings");
                    btnSettings.click();
                    const settingsPopoverVisible = (document.getElementById("quick-settings-popover").style.display === "flex");
                    document.getElementById("quick-settings-popover").style.display = "none";

                    // 3. Programmatic click on #btn-reader-fullscreen while menu closed
                    let fsError = null;
                    try {
                        const btnFs = document.getElementById("btn-reader-fullscreen");
                        btnFs.click();
                    } catch (e) {
                        fsError = e.message;
                    }

                    // 4. Category button check
                    const duplicateHeaderBtn = document.getElementById("btn-add-folder");
                    const canonicalSidebarBtn = document.getElementById("btn-add-category-sidebar");

                    return {
                        isClosed: isClosed,
                        btnPrintExists: !!btnPrint,
                        printModalVisible: printModalVisible,
                        btnSettingsExists: !!btnSettings,
                        settingsPopoverVisible: settingsPopoverVisible,
                        fsError: fsError,
                        duplicateHeaderBtnRemoved: (duplicateHeaderBtn === null),
                        canonicalSidebarBtnExists: (canonicalSidebarBtn !== null)
                    };
                })()
            """)
            assert compat_res["btnPrintExists"], "#btn-reader-print missing from DOM"
            assert compat_res["printModalVisible"], "Programmatic click on #btn-reader-print failed to open print modal"
            assert compat_res["btnSettingsExists"], "#btn-reader-settings missing from DOM"
            assert compat_res["settingsPopoverVisible"], "Programmatic click on #btn-reader-settings failed to open settings popover"
            assert compat_res["fsError"] is None, f"Programmatic click on #btn-reader-fullscreen threw error: {compat_res['fsError']}"
            assert compat_res["duplicateHeaderBtnRemoved"], "Redundant #btn-add-folder still exists in DOM"
            assert compat_res["canonicalSidebarBtnExists"], "Canonical #btn-add-category-sidebar missing from sidebar"

        test("TC-M3-STRESS-04", "Preserved Button IDs Backward Compatibility & Category Consolidation", t_stress_04)

        # ----------------------------------------------------------------------
        # TC-M3-STRESS-05: Reader Palette Switching Theme Invariants on Overflow Menu & Collapsed Formats Filter State
        # ----------------------------------------------------------------------
        def t_stress_05():
            # 1. Palette theme switching verification on overflow menu
            themes_res = ws_client.eval_js("""
                (function() {
                    const themes = ["day", "night", "sepia", "dark-sepia"];
                    const menu = document.getElementById("reader-overflow-menu");
                    window.app.openReaderOverflowMenu();

                    const results = {};
                    for (const th of themes) {
                        window.app.setReadingTheme(th);
                        const computed = window.getComputedStyle(menu);
                        results[th] = {
                            bg: computed.backgroundColor,
                            color: computed.color,
                            border: computed.borderColor
                        };
                    }
                    window.app.closeReaderOverflowMenu();
                    return results;
                })()
            """)
            # Day vs Night backgrounds must differ
            assert themes_res["day"]["bg"] != themes_res["night"]["bg"], "Overflow menu background did not adapt between Day and Night themes"
            # Sepia background must differ from Day and Night
            assert themes_res["sepia"]["bg"] != themes_res["day"]["bg"], "Overflow menu background did not adapt to Sepia theme"

            # 2. Filter Orthogonality: Collapse Formats section, then verify format selection works programmatically
            filter_res = ws_client.eval_js("""
                (function() {
                    window.app.closeReader();
                    window.app.setFormatsCollapsed(true, true);
                    const isCollapsed = document.getElementById("formats-collapsible").classList.contains("collapsed");

                    // Filter by EPUB via DOM click
                    const epubNav = document.querySelector('.nav-item[data-format="EPUB"]');
                    epubNav.click();
                    const activeFilter = window.app.currentFormatFilter;
                    const epubNavActive = epubNav.classList.contains("active");

                    // Clear filter via clicking 'all' category
                    document.querySelector('.nav-item[data-category="all"]').click();
                    const clearedFilter = window.app.currentFormatFilter;
                    const allCategoryActive = (window.app.currentCategory === "all");

                    // Restore expanded state
                    window.app.setFormatsCollapsed(false, true);

                    return {
                        isCollapsed: isCollapsed,
                        activeFilter: activeFilter,
                        epubNavActive: epubNavActive,
                        clearedFilter: clearedFilter,
                        allCategoryActive: allCategoryActive
                    };
                })()
            """)
            assert filter_res["isCollapsed"], "Formats section was not collapsed"
            assert filter_res["activeFilter"] == "EPUB", "EPUB filter failed when section was collapsed"
            assert filter_res["epubNavActive"], ".nav-item[data-format='EPUB'] did not become active when section was collapsed"
            assert filter_res["clearedFilter"] is None, "Failed to clear format filter"
            assert filter_res["allCategoryActive"], "'all' category not active after clearing format filter"

        test("TC-M3-STRESS-05", "Reader Palette Switching Theme Invariants on Overflow Menu & Collapsed Formats Filter State", t_stress_05)

    finally:
        if ws_client:
            ws_client.close()
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except Exception:
                proc.kill()

    print("=" * 76)
    passed_count = sum(1 for r in results if r[2] == "PASS")
    total_count = len(results)
    print(f"  CHALLENGER M3 SUITE SUMMARY: {passed_count}/{total_count} Passed")
    print("=" * 76)
    return passed_count == total_count and total_count > 0


if __name__ == "__main__":
    success = run_m3_stress_suite()
    sys.exit(0 if success else 1)
