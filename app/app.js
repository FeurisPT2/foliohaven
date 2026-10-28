/**
 * Icecream Ebook Reader Replica: Application Controller
 * Handles UI routing, events, keyboard navigation, and synchronization
 */

class AppController {
  constructor() {
    this.currentViewMode = "grid"; // "grid" or "table"
    this.currentCategory = "all";
    this.currentFormatFilter = null;
    this.searchQuery = "";
    this.selectedBookIds = new Set();
    this.activeBook = null;
    this.isReading = false;
    this.init();
  }

  init() {
    this.bindEvents();
    this.loadSettings();
    this.renderLibrary();
    this.updateBadges();

    // Support URL Hash routing for direct screen verification & screenshots
    if (window.location.hash === "#table") {
      this.setViewMode("table");
    } else if (window.location.hash === "#reader") {
      const books = window.db.getBooks();
      if (books.length > 0) this.openBook(books[0]);
    } else if (window.location.hash === "#drawer-toc") {
      const books = window.db.getBooks();
      if (books.length > 0) {
        this.openBook(books[0]);
        this.toggleDrawer("drawer-toc");
      }
    } else if (window.location.hash === "#settings") {
      document.getElementById("modal-settings").style.display = "flex";
    }
  }

  bindEvents() {
    // --- View Mode Toggles ---
    document.getElementById("btn-view-grid").addEventListener("click", () => this.setViewMode("grid"));
    document.getElementById("btn-view-table").addEventListener("click", () => this.setViewMode("table"));

    // --- Search Input ---
    document.getElementById("library-search").addEventListener("input", (e) => {
      this.searchQuery = e.target.value.toLowerCase().trim();
      this.renderLibrary();
    });

    // --- Sidebar Category Filters ---
    document.querySelectorAll(".nav-item[data-category]").forEach(el => {
      el.addEventListener("click", () => {
        document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
        el.classList.add("active");
        this.currentCategory = el.dataset.category;
        this.currentFormatFilter = null;
        this.renderLibrary();
      });
    });

    // --- Format Filters ---
    document.querySelectorAll(".nav-item[data-format]").forEach(el => {
      el.addEventListener("click", () => {
        document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
        el.classList.add("active");
        this.currentFormatFilter = el.dataset.format;
        this.currentCategory = null;
        this.renderLibrary();
      });
    });

    // --- Add Book File Importer ---
    const fileInput = document.getElementById("file-import-input");
    document.getElementById("btn-add-book").addEventListener("click", () => fileInput.click());
    document.getElementById("btn-empty-add").addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", (e) => {
      const files = Array.from(e.target.files);
      files.forEach(file => {
        const ext = file.name.split(".").pop().toUpperCase();
        const title = file.name.replace(/\.[^/.]+$/, "");
        window.db.addBook({
          title: title,
          author: "Imported Author",
          format: ext || "EPUB",
          file_path: file.name,
          file_size_bytes: file.size,
          content: `Content preview for ${file.name}.\n\nImported successfully into Icecream Ebook Reader clean-room replica library.`
        });
      });
      this.renderLibrary();
      this.updateBadges();
      fileInput.value = "";
    });

    // --- Drag and Drop File Import ---
    const libraryContent = document.getElementById("library-content");
    window.addEventListener("dragover", (e) => {
      e.preventDefault();
      libraryContent.style.backgroundColor = "var(--color-surface-hover)";
    });
    window.addEventListener("dragleave", () => {
      libraryContent.style.backgroundColor = "";
    });
    window.addEventListener("drop", (e) => {
      e.preventDefault();
      libraryContent.style.backgroundColor = "";
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        Array.from(e.dataTransfer.files).forEach(file => {
          const ext = file.name.split(".").pop().toUpperCase();
          const title = file.name.replace(/\.[^/.]+$/, "");
          window.db.addBook({
            title: title,
            author: "Local File",
            format: ext || "EPUB",
            file_path: file.name,
            file_size_bytes: file.size,
            content: `Content of dropped document: ${file.name}.`
          });
        });
        this.renderLibrary();
        this.updateBadges();
      }
    });

    // --- Reader Navigation & Controls ---
    document.getElementById("btn-back-to-library").addEventListener("click", () => this.closeReader());
    document.getElementById("zone-prev").addEventListener("click", () => this.pagePrev());
    document.getElementById("zone-next").addEventListener("click", () => this.pageNext());

    // Scrubber Slider
    document.getElementById("reader-scrubber").addEventListener("input", (e) => {
      const val = parseInt(e.target.value);
      if (this.activeBook && this.activeBook.chapters) {
        const targetChap = Math.min(
          this.activeBook.chapters.length - 1,
          Math.floor((val / 100) * this.activeBook.chapters.length)
        );
        window.engine.jumpToChapter(targetChap);
        this.updateReaderView();
      }
    });

    // Quick Settings Popover
    document.getElementById("btn-reader-settings").addEventListener("click", () => {
      const popover = document.getElementById("quick-settings-popover");
      popover.style.display = (popover.style.display === "flex") ? "none" : "flex";
    });

    // Quick Settings: Theme Pills
    document.querySelectorAll(".theme-pill[data-reading-theme]").forEach(pill => {
      pill.addEventListener("click", () => {
        document.querySelectorAll(".theme-pill").forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.setReadingTheme(pill.dataset.readingTheme);
      });
    });

    // Quick Settings: Column Toggle
    document.getElementById("btn-col-single").addEventListener("click", () => {
      document.getElementById("btn-col-single").classList.replace("btn-secondary", "btn-primary");
      document.getElementById("btn-col-double").classList.replace("btn-primary", "btn-secondary");
      window.engine.setColumnCount(1);
      this.updateReaderView();
    });
    document.getElementById("btn-col-double").addEventListener("click", () => {
      document.getElementById("btn-col-double").classList.replace("btn-secondary", "btn-primary");
      document.getElementById("btn-col-single").classList.replace("btn-primary", "btn-secondary");
      window.engine.setColumnCount(2);
      this.updateReaderView();
    });

    // Quick Settings: Font Size Steppers
    document.getElementById("btn-font-dec").addEventListener("click", () => {
      window.engine.setFontSize(-2);
      document.getElementById("label-font-size").textContent = window.engine.fontSize + "px";
      this.updateReaderView();
    });
    document.getElementById("btn-font-inc").addEventListener("click", () => {
      window.engine.setFontSize(+2);
      document.getElementById("label-font-size").textContent = window.engine.fontSize + "px";
      this.updateReaderView();
    });

    // Quick Settings: Font Family
    document.getElementById("select-font-family").addEventListener("change", (e) => {
      window.engine.setFontFamily(e.target.value);
      this.updateReaderView();
    });

    // Quick Settings: Night Dimmer
    document.getElementById("slider-dimmer").addEventListener("input", (e) => {
      const alpha = (parseInt(e.target.value) / 100);
      document.getElementById("dim-overlay").style.opacity = alpha;
    });

    // --- Drawers (TOC, Bookmarks, Notes, Search) ---
    document.getElementById("btn-toggle-toc").addEventListener("click", () => this.toggleDrawer("drawer-toc"));
    document.getElementById("btn-close-toc").addEventListener("click", () => this.closeDrawer("drawer-toc"));

    document.getElementById("btn-toggle-bookmarks").addEventListener("click", () => {
      this.renderBookmarksList();
      this.toggleDrawer("drawer-bookmarks");
    });
    document.getElementById("btn-close-bookmarks").addEventListener("click", () => this.closeDrawer("drawer-bookmarks"));

    document.getElementById("btn-quick-bookmark").addEventListener("click", () => this.quickAddBookmark());
    document.getElementById("btn-add-bookmark-drawer").addEventListener("click", () => this.quickAddBookmark());
    document.getElementById("btn-clear-all-bookmarks").addEventListener("click", () => {
      if (this.activeBook) {
        window.db.clearBookmarks(this.activeBook.id);
        this.renderBookmarksList();
        this.updateBookmarkCounts();
      }
    });

    document.getElementById("btn-toggle-notes").addEventListener("click", () => {
      this.renderNotesList();
      this.toggleDrawer("drawer-notes");
    });
    document.getElementById("btn-close-notes").addEventListener("click", () => this.closeDrawer("drawer-notes"));
    document.getElementById("btn-clear-all-notes").addEventListener("click", () => {
      if (this.activeBook) {
        window.db.clearAnnotations(this.activeBook.id);
        this.renderNotesList();
        this.updateReaderView();
        this.updateNotesCounts();
      }
    });
    document.getElementById("btn-export-notes-html").addEventListener("click", () => this.exportNotesToHtml());

    document.getElementById("btn-toggle-search").addEventListener("click", () => this.toggleDrawer("drawer-search"));
    document.getElementById("btn-close-search").addEventListener("click", () => this.closeDrawer("drawer-search"));
    document.getElementById("inbook-search-input").addEventListener("input", (e) => this.handleInBookSearch(e.target.value));

    // Fullscreen Toggle
    document.getElementById("btn-reader-fullscreen").addEventListener("click", () => this.toggleFullscreen());

    // TTS Read Aloud with Real-Time Paragraph Spoken Word Highlighting
    const ttsBtn = document.getElementById("btn-tts-play");
    ttsBtn.addEventListener("click", () => {
      if ('speechSynthesis' in window) {
        if (window.speechSynthesis.speaking) {
          window.speechSynthesis.cancel();
          ttsBtn.textContent = "▶ Read Aloud";
          document.querySelectorAll(".reflow-para").forEach(p => p.style.backgroundColor = "");
          return;
        }

        const paragraphs = Array.from(document.querySelectorAll(".reflow-para"));
        if (paragraphs.length === 0) return;

        ttsBtn.textContent = "⏹ Stop Speech";
        let pIndex = 0;

        const speakNextParagraph = () => {
          if (pIndex >= paragraphs.length || !this.isReading) {
            ttsBtn.textContent = "▶ Read Aloud";
            document.querySelectorAll(".reflow-para").forEach(p => p.style.backgroundColor = "");
            return;
          }

          paragraphs.forEach((p, idx) => {
            p.style.backgroundColor = (idx === pIndex) ? "rgba(31, 95, 219, 0.15)" : "";
            p.style.borderRadius = "4px";
          });

          const currentP = paragraphs[pIndex];
          const utterance = new SpeechSynthesisUtterance(currentP.textContent);
          const settings = window.db.getSettings();
          utterance.rate = (settings.ttsSpeed || 10) / 10;
          utterance.volume = (settings.ttsVolume || 80) / 100;

          utterance.onend = () => {
            pIndex++;
            speakNextParagraph();
          };

          utterance.onerror = () => {
            ttsBtn.textContent = "▶ Read Aloud";
            currentP.style.backgroundColor = "";
          };

          window.speechSynthesis.speak(utterance);
        };

        speakNextParagraph();
      } else {
        alert("Text to Speech is not supported in this runtime environment.");
      }
    });

    // Print Dialog
    document.getElementById("btn-reader-print").addEventListener("click", () => {
      document.getElementById("modal-print").style.display = "flex";
    });
    document.getElementById("btn-close-print").addEventListener("click", () => {
      document.getElementById("modal-print").style.display = "none";
    });
    document.getElementById("btn-cancel-print").addEventListener("click", () => {
      document.getElementById("modal-print").style.display = "none";
    });
    document.getElementById("btn-confirm-print").addEventListener("click", () => {
      document.getElementById("modal-print").style.display = "none";
      window.print();
    });

    // Preferences Modal (S08)
    document.getElementById("btn-open-settings").addEventListener("click", () => {
      document.getElementById("modal-settings").style.display = "flex";
    });
    document.getElementById("btn-close-settings-modal").addEventListener("click", () => {
      document.getElementById("modal-settings").style.display = "none";
    });
    document.getElementById("btn-cancel-settings").addEventListener("click", () => {
      document.getElementById("modal-settings").style.display = "none";
    });
    document.getElementById("btn-save-settings").addEventListener("click", () => {
      const chromeTheme = document.getElementById("select-app-chrome-theme").value;
      const readingMode = document.getElementById("select-default-reading-mode").value;
      window.db.saveSettings({ theme: chromeTheme, readingTheme: readingMode });
      this.applyChromeTheme(chromeTheme);
      this.setReadingTheme(readingMode);
      document.getElementById("modal-settings").style.display = "none";
    });

    // Operations Footer Actions
    document.getElementById("btn-select-all").addEventListener("click", () => {
      const visibleBooks = this.getFilteredBooks();
      visibleBooks.forEach(b => this.selectedBookIds.add(b.id));
      this.renderLibrary();
      this.updateOperationsFooter();
    });
    document.getElementById("btn-clear-selection").addEventListener("click", () => {
      this.selectedBookIds.clear();
      this.renderLibrary();
      this.updateOperationsFooter();
    });
    document.getElementById("btn-batch-delete").addEventListener("click", () => {
      this.selectedBookIds.forEach(id => window.db.softDeleteBook(id));
      this.selectedBookIds.clear();
      this.renderLibrary();
      this.updateBadges();
      this.updateOperationsFooter();
    });
    document.getElementById("btn-batch-restore").addEventListener("click", () => {
      this.selectedBookIds.forEach(id => window.db.restoreBook(id));
      this.selectedBookIds.clear();
      this.renderLibrary();
      this.updateBadges();
      this.updateOperationsFooter();
    });
    document.getElementById("btn-batch-purge").addEventListener("click", () => {
      this.selectedBookIds.forEach(id => window.db.purgeBook(id));
      this.selectedBookIds.clear();
      this.renderLibrary();
      this.updateBadges();
      this.updateOperationsFooter();
    });

    // --- Text Selection NotePopup (S06) ---
    document.addEventListener("selectionchange", () => {
      if (!this.isReading) return;
      const sel = window.getSelection();
      const popup = document.getElementById("note-popup");
      if (sel && sel.toString().trim().length > 3) {
        const range = sel.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        popup.style.display = "flex";
        popup.style.top = `${Math.max(10, rect.top - 50)}px`;
        popup.style.left = `${Math.max(10, rect.left + (rect.width / 2) - 100)}px`;
      } else {
        // Only hide if not clicking inside popup
        if (!popup.matches(":hover")) {
          popup.style.display = "none";
        }
      }
    });

    // NotePopup Color Swatches
    document.querySelectorAll(".swatch-btn[data-color]").forEach(btn => {
      btn.addEventListener("click", () => {
        const sel = window.getSelection();
        const text = sel ? sel.toString().trim() : "";
        if (text && this.activeBook) {
          window.db.addAnnotation({
            book_id: this.activeBook.id,
            selected_text: text,
            note_text: "Highlight (" + btn.dataset.color + ")",
            color_code: btn.dataset.color
          });
          document.getElementById("note-popup").style.display = "none";
          this.updateReaderView();
          this.updateNotesCounts();
        }
      });
    });

    // NotePopup Copy Action
    document.getElementById("btn-popup-copy").addEventListener("click", () => {
      const sel = window.getSelection();
      if (sel) {
        navigator.clipboard.writeText(sel.toString());
        document.getElementById("note-popup").style.display = "none";
      }
    });

    // NotePopup Custom Note
    document.getElementById("btn-popup-note").addEventListener("click", () => {
      const sel = window.getSelection();
      const text = sel ? sel.toString().trim() : "";
      if (text && this.activeBook) {
        const comment = prompt("Enter note commentary for selection:", "");
        if (comment !== null) {
          window.db.addAnnotation({
            book_id: this.activeBook.id,
            selected_text: text,
            note_text: comment || "Note",
            color_code: "yellow"
          });
          document.getElementById("note-popup").style.display = "none";
          this.updateReaderView();
          this.updateNotesCounts();
        }
      }
    });

    // --- Complete Keyboard Navigation (C10) ---
    window.addEventListener("keydown", (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.target.tagName === "SELECT") {
        return; // Don't intercept typing in inputs
      }

      if (this.isReading) {
        if (e.key === "ArrowRight" || e.key === " " || e.key === "PageDown" || e.key === "ArrowDown") {
          e.preventDefault();
          this.pageNext();
        } else if (e.key === "ArrowLeft" || e.key === "Backspace" || e.key === "PageUp" || e.key === "ArrowUp") {
          e.preventDefault();
          this.pagePrev();
        } else if (e.key === "Escape") {
          e.preventDefault();
          this.closeReader();
        } else if (e.key === "F11") {
          e.preventDefault();
          this.toggleFullscreen();
        } else if (e.key === "F1") {
          e.preventDefault();
          this.cycleReadingTheme();
        } else if (e.ctrlKey && e.key.toLowerCase() === "b") {
          e.preventDefault();
          this.renderBookmarksList();
          this.toggleDrawer("drawer-bookmarks");
        } else if (e.ctrlKey && e.key.toLowerCase() === "t") {
          e.preventDefault();
          this.toggleDrawer("drawer-toc");
        } else if (e.ctrlKey && e.key.toLowerCase() === "n") {
          e.preventDefault();
          this.renderNotesList();
          this.toggleDrawer("drawer-notes");
        } else if (e.ctrlKey && e.key.toLowerCase() === "f") {
          e.preventDefault();
          this.toggleDrawer("drawer-search");
        } else if (e.ctrlKey && e.key.toLowerCase() === "d") {
          e.preventDefault();
          this.quickAddBookmark();
        } else if (e.ctrlKey && e.key.toLowerCase() === "p") {
          e.preventDefault();
          document.getElementById("modal-print").style.display = "flex";
        }
      }
    });
  }

  loadSettings() {
    const settings = window.db.getSettings();
    if (settings.theme) this.applyChromeTheme(settings.theme);
    if (settings.readingTheme) this.setReadingTheme(settings.readingTheme);
    if (settings.viewMode) this.setViewMode(settings.viewMode);
  }

  applyChromeTheme(theme) {
    if (theme === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
  }

  setReadingTheme(theme) {
    const reader = document.getElementById("reader-screen");
    reader.setAttribute("data-reading-theme", theme);
    document.querySelectorAll(".theme-pill").forEach(p => {
      p.classList.toggle("active", p.dataset.readingTheme === theme);
    });
  }

  cycleReadingTheme() {
    const themes = ["day", "night", "sepia", "dark-sepia"];
    const current = document.getElementById("reader-screen").getAttribute("data-reading-theme") || "day";
    const nextIdx = (themes.indexOf(current) + 1) % themes.length;
    this.setReadingTheme(themes[nextIdx]);
  }

  setViewMode(mode) {
    this.currentViewMode = mode;
    document.getElementById("btn-view-grid").classList.toggle("active", mode === "grid");
    document.getElementById("btn-view-table").classList.toggle("active", mode === "table");
    document.getElementById("grid-view").style.display = (mode === "grid") ? "flex" : "none";
    document.getElementById("table-view").style.display = (mode === "table") ? "table" : "none";
    this.renderLibrary();
  }

  getFilteredBooks() {
    let books = window.db.getBooks();

    // Category Filter
    if (this.currentCategory === "trash") {
      books = books.filter(b => b.is_deleted === 1);
    } else {
      books = books.filter(b => b.is_deleted === 0);
      if (this.currentCategory === "recent") {
        books = books.filter(b => b.last_read !== null).sort((a, b) => new Date(b.last_read) - new Date(a.last_read));
      } else if (this.currentCategory === "favorites") {
        books = books.filter(b => b.is_favorite === 1);
      } else if (this.currentCategory === "read") {
        books = books.filter(b => b.progress_percent >= 99);
      }
    }

    // Format Filter
    if (this.currentFormatFilter) {
      books = books.filter(b => b.format === this.currentFormatFilter);
    }

    // Search Query
    if (this.searchQuery) {
      books = books.filter(b =>
        b.title.toLowerCase().includes(this.searchQuery) ||
        b.author.toLowerCase().includes(this.searchQuery)
      );
    }

    return books;
  }

  renderLibrary() {
    const books = this.getFilteredBooks();
    const gridView = document.getElementById("grid-view");
    const tableBody = document.getElementById("table-body");
    const emptyState = document.getElementById("empty-state");

    if (books.length === 0) {
      emptyState.style.display = "flex";
      gridView.style.display = "none";
      document.getElementById("table-view").style.display = "none";
      return;
    }

    emptyState.style.display = "none";
    gridView.style.display = (this.currentViewMode === "grid") ? "flex" : "none";
    document.getElementById("table-view").style.display = (this.currentViewMode === "table") ? "table" : "none";

    // --- Render Grid Cards (S01A) ---
    gridView.innerHTML = "";
    books.forEach(b => {
      const card = document.createElement("div");
      card.className = "book-card" + (this.selectedBookIds.has(b.id) ? " selected" : "");
      card.innerHTML = `
        <div class="card-thumb">
          <span class="card-format-badge badge-${b.format.toLowerCase()}">${b.format}</span>
          <span class="card-favorite-star ${b.is_favorite ? 'active' : ''}">★</span>
        </div>
        <div class="card-title" title="${escapeHtml(b.title)}">${escapeHtml(b.title)}</div>
        <div class="card-author">${escapeHtml(b.author)}</div>
        <div class="card-progress-track">
          <div class="card-progress-fill" style="width: ${b.progress_percent || 0}%;"></div>
        </div>
      `;

      // Favorite toggle
      card.querySelector(".card-favorite-star").addEventListener("click", (e) => {
        e.stopPropagation();
        window.db.toggleFavorite(b.id);
        this.renderLibrary();
        this.updateBadges();
      });

      // Card selection vs open
      card.addEventListener("click", (e) => {
        if (e.ctrlKey || e.shiftKey) {
          if (this.selectedBookIds.has(b.id)) this.selectedBookIds.delete(b.id);
          else this.selectedBookIds.add(b.id);
          this.renderLibrary();
          this.updateOperationsFooter();
        } else {
          this.openBook(b);
        }
      });

      // Context menu for properties (S09)
      card.addEventListener("contextmenu", (e) => {
        e.preventDefault();
        this.openBookProperties(b);
      });

      gridView.appendChild(card);
    });

    // --- Render Table Rows (S01B) ---
    tableBody.innerHTML = "";
    books.forEach(b => {
      const tr = document.createElement("tr");
      if (this.selectedBookIds.has(b.id)) tr.className = "selected";
      tr.innerHTML = `
        <td style="font-weight: 600;">${escapeHtml(b.title)}</td>
        <td style="color: var(--color-text-muted);">${escapeHtml(b.author)}</td>
        <td>${new Date(b.date_added).toLocaleDateString()}</td>
        <td>
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="flex: 1; height: 6px; background: var(--color-border); border-radius: 3px; overflow: hidden;">
              <div style="height: 100%; background: var(--color-success); width: ${b.progress_percent || 0}%;"></div>
            </div>
            <span style="font-size: 11px; min-width: 32px;">${b.progress_percent || 0}%</span>
          </div>
        </td>
        <td><span class="card-format-badge badge-${b.format.toLowerCase()}">${b.format}</span></td>
      `;

      tr.addEventListener("click", (e) => {
        if (e.ctrlKey || e.shiftKey) {
          if (this.selectedBookIds.has(b.id)) this.selectedBookIds.delete(b.id);
          else this.selectedBookIds.add(b.id);
          this.renderLibrary();
          this.updateOperationsFooter();
        } else {
          this.openBook(b);
        }
      });

      tableBody.appendChild(tr);
    });

    this.updateOperationsFooter();
  }

  updateBadges() {
    const all = window.db.getBooks();
    document.getElementById("badge-all").textContent = all.filter(b => !b.is_deleted).length;
    document.getElementById("badge-recent").textContent = all.filter(b => !b.is_deleted && b.last_read).length;
    document.getElementById("badge-favorites").textContent = all.filter(b => !b.is_deleted && b.is_favorite).length;
    document.getElementById("badge-read").textContent = all.filter(b => !b.is_deleted && b.progress_percent >= 99).length;
    document.getElementById("badge-trash").textContent = all.filter(b => b.is_deleted).length;

    ["EPUB", "PDF", "MOBI", "FB2", "CBZ", "TXT"].forEach(f => {
      const el = document.getElementById(`badge-format-${f.toLowerCase()}`);
      if (el) el.textContent = all.filter(b => !b.is_deleted && b.format === f).length;
    });
  }

  updateOperationsFooter() {
    const footer = document.getElementById("operations-footer");
    const count = this.selectedBookIds.size;
    if (count > 0) {
      footer.style.display = "flex";
      document.getElementById("selection-counter").textContent = `${count} book${count > 1 ? 's' : ''} selected`;

      const isTrashView = (this.currentCategory === "trash");
      document.getElementById("btn-batch-delete").style.display = isTrashView ? "none" : "inline-block";
      document.getElementById("btn-batch-restore").style.display = isTrashView ? "inline-block" : "none";
      document.getElementById("btn-batch-purge").style.display = isTrashView ? "inline-block" : "none";
    } else {
      footer.style.display = "none";
    }
  }

  // --- S02: Open & Read Flow ---
  openBook(book) {
    // DRM Protection Detection & Warning
    if (book.is_drm || (book.file_path && book.file_path.includes(".drm"))) {
      const modal = document.getElementById("modal-confirm");
      document.getElementById("confirm-title").textContent = "DRM Protection Detected";
      document.getElementById("confirm-message").textContent =
        "The document you are attempting to open is encrypted with Digital Rights Management (DRM). Clean-room reading of DRM-locked files is prohibited.";
      document.getElementById("btn-confirm-proceed").style.display = "none";
      document.getElementById("btn-confirm-cancel").textContent = "Dismiss";
      modal.style.display = "flex";
      document.getElementById("btn-confirm-cancel").onclick = () => {
        modal.style.display = "none";
        document.getElementById("btn-confirm-proceed").style.display = "inline-block";
      };
      return;
    }

    this.activeBook = book;
    this.isReading = true;

    // Record last read
    window.db.updateBook(book.id, { last_read: new Date().toISOString() });

    const settings = window.db.getSettings();
    window.engine.loadBook(book, settings);

    document.getElementById("reader-screen").style.display = "flex";
    this.updateReaderView();
    this.renderTocList();
    this.updateBookmarkCounts();
    this.updateNotesCounts();
  }

  closeReader() {
    if (this.activeBook) {
      const view = window.engine.renderCurrentView();
      window.db.updateBook(this.activeBook.id, {
        progress_percent: view.globalPercent,
        current_page: view.spreadIndex
      });
    }
    this.isReading = false;
    document.getElementById("reader-screen").style.display = "none";
    this.closeAllDrawers();
    document.getElementById("quick-settings-popover").style.display = "none";
    this.renderLibrary();
    this.updateBadges();

    // Support URL Hash routing for direct screen verification & screenshots
    if (window.location.hash === "#table") {
      this.setViewMode("table");
    } else if (window.location.hash === "#reader") {
      const books = window.db.getBooks();
      if (books.length > 0) this.openBook(books[0]);
    } else if (window.location.hash === "#drawer-toc") {
      const books = window.db.getBooks();
      if (books.length > 0) {
        this.openBook(books[0]);
        this.toggleDrawer("drawer-toc");
      }
    } else if (window.location.hash === "#settings") {
      document.getElementById("modal-settings").style.display = "flex";
    }
  }

  pageNext() {
    const res = window.engine.nextPage();
    if (res) this.updateReaderView();
  }

  pagePrev() {
    const res = window.engine.prevPage();
    if (res) this.updateReaderView();
  }

  updateReaderView() {
    const view = window.engine.renderCurrentView();
    document.getElementById("reader-book-content").innerHTML = view.html;
    document.getElementById("reader-page-info").textContent =
      `Spread ${view.spreadIndex} / ${view.totalSpreadsInChapter} (Ch. ${view.chapterIndex}/${view.totalChapters})`;
    document.getElementById("reader-progress-info").textContent = `${view.globalPercent}%`;
    document.getElementById("reader-scrubber").value = view.globalPercent;

    if (this.activeBook) {
      window.db.updateBook(this.activeBook.id, {
        progress_percent: view.globalPercent,
        current_page: view.spreadIndex
      });
    }
  }

  toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      if (document.exitFullscreen) document.exitFullscreen();
    }
  }

  // --- Drawers Management ---
  toggleDrawer(id) {
    const drawer = document.getElementById(id);
    const isOpen = drawer.classList.contains("open");
    this.closeAllDrawers();
    if (!isOpen) drawer.classList.add("open");
  }

  closeDrawer(id) {
    document.getElementById(id).classList.remove("open");
  }

  closeAllDrawers() {
    document.querySelectorAll(".drawer").forEach(d => d.classList.remove("open"));
  }

  renderTocList() {
    const container = document.getElementById("toc-list");
    container.innerHTML = "";
    if (!this.activeBook || !this.activeBook.chapters) return;

    this.activeBook.chapters.forEach((chap, idx) => {
      const item = document.createElement("div");
      item.className = "drawer-card";
      item.innerHTML = `<strong>${escapeHtml(chap.title)}</strong>`;
      item.addEventListener("click", () => {
        window.engine.jumpToChapter(idx);
        this.updateReaderView();
        this.closeDrawer("drawer-toc");
      });
      container.appendChild(item);
    });
  }

  renderBookmarksList() {
    const container = document.getElementById("bookmarks-list");
    container.innerHTML = "";
    if (!this.activeBook) return;

    const bms = window.db.getBookmarks(this.activeBook.id);
    if (bms.length === 0) {
      container.innerHTML = `<p style="color: var(--color-text-muted); text-align: center; margin-top: 20px;">No bookmarks added yet.</p>`;
      return;
    }

    bms.forEach(bm => {
      const card = document.createElement("div");
      card.className = "drawer-card";
      card.innerHTML = `
        <div style="font-weight: 600; font-size: 13px;">${escapeHtml(bm.chapter_title || 'Bookmark')}</div>
        <div style="font-size: 12px; color: var(--color-text-muted); margin-top: 4px;">${escapeHtml(bm.snippet_text || '')}</div>
        <div class="drawer-card-meta">
          <span>${new Date(bm.created_at).toLocaleTimeString()}</span>
          <button class="btn btn-ghost" style="padding: 2px 6px; font-size: 11px; color: var(--color-danger);">Delete</button>
        </div>
      `;

      card.querySelector("button").addEventListener("click", (e) => {
        e.stopPropagation();
        window.db.deleteBookmark(bm.id);
        this.renderBookmarksList();
        this.updateBookmarkCounts();
      });

      card.addEventListener("click", () => {
        this.closeDrawer("drawer-bookmarks");
      });

      container.appendChild(card);
    });
  }

  quickAddBookmark() {
    if (!this.activeBook) return;
    const view = window.engine.renderCurrentView();
    window.db.addBookmark({
      book_id: this.activeBook.id,
      page_number: view.spreadIndex,
      chapter_title: view.chapterTitle,
      snippet_text: `Reading position at ${view.globalPercent}%`
    });
    this.updateBookmarkCounts();
    alert("Bookmark saved!");
  }

  updateBookmarkCounts() {
    if (!this.activeBook) return;
    const count = window.db.getBookmarks(this.activeBook.id).length;
    document.getElementById("reader-bookmark-count").textContent = count;
  }

  renderNotesList() {
    const container = document.getElementById("notes-list");
    container.innerHTML = "";
    if (!this.activeBook) return;

    const notes = window.db.getAnnotations(this.activeBook.id);
    if (notes.length === 0) {
      container.innerHTML = `<p style="color: var(--color-text-muted); text-align: center; margin-top: 20px;">No highlights or notes recorded.</p>`;
      return;
    }

    notes.forEach(ann => {
      const card = document.createElement("div");
      card.className = "drawer-card";
      card.innerHTML = `
        <div style="border-left: 3px solid var(--color-highlight-${ann.color_code}); padding-left: 8px;">
          <div style="font-style: italic; font-size: 12px; color: var(--color-text-muted); margin-bottom: 4px;">"${escapeHtml(ann.selected_text)}"</div>
          <div style="font-weight: 500; font-size: 13px;">${escapeHtml(ann.note_text || 'Highlight')}</div>
        </div>
        <div class="drawer-card-meta">
          <span>${new Date(ann.created_at).toLocaleDateString()}</span>
          <button class="btn btn-ghost" style="padding: 2px 6px; font-size: 11px; color: var(--color-danger);">Delete</button>
        </div>
      `;

      card.querySelector("button").addEventListener("click", (e) => {
        e.stopPropagation();
        window.db.deleteAnnotation(ann.id);
        this.renderNotesList();
        this.updateReaderView();
        this.updateNotesCounts();
      });

      container.appendChild(card);
    });
  }

  updateNotesCounts() {
    if (!this.activeBook) return;
    const count = window.db.getAnnotations(this.activeBook.id).length;
    document.getElementById("reader-notes-count").textContent = count;
  }

  exportNotesToHtml() {
    if (!this.activeBook) return;
    const notes = window.db.getAnnotations(this.activeBook.id);
    let html = `<!DOCTYPE html><html><head><title>Notes: ${escapeHtml(this.activeBook.title)}</title><style>body{font-family:sans-serif;max-width:800px;margin:40px auto;padding:20px;line-height:1.6;} .note{border-left:4px solid #1f5fdb;padding:12px;margin:16px 0;background:#f5f7fa;border-radius:4px;}</style></head><body><h1>Study Notes: ${escapeHtml(this.activeBook.title)}</h1><p><strong>Author:</strong> ${escapeHtml(this.activeBook.author)}</p><hr>`;
    notes.forEach(n => {
      html += `<div class="note"><p><em>"${escapeHtml(n.selected_text)}"</em></p><p><strong>Commentary:</strong> ${escapeHtml(n.note_text)}</p><small>${new Date(n.created_at).toLocaleString()}</small></div>`;
    });
    html += `</body></html>`;

    const blob = new Blob([html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${this.activeBook.title.replace(/\s+/g, '_')}_notes.html`;
    a.click();
    URL.revokeObjectURL(url);
  }

  handleInBookSearch(query) {
    const resultsContainer = document.getElementById("inbook-search-results");
    if (!query || query.trim().length === 0) {
      resultsContainer.innerHTML = `<p style="color: var(--color-text-muted); font-size: 13px; text-align: center; margin-top: 24px;">Enter a keyword above to search through the entire book.</p>`;
      return;
    }

    const matches = window.engine.searchInBook(query);
    if (matches.length === 0) {
      resultsContainer.innerHTML = `<p style="color: var(--color-text-muted); font-size: 13px; text-align: center; margin-top: 24px;">No matches found for "${escapeHtml(query)}".</p>`;
      return;
    }

    resultsContainer.innerHTML = `<div style="font-size: 12px; font-weight: 600; margin-bottom: 8px;">${matches.length} results found</div>`;
    matches.forEach(m => {
      const card = document.createElement("div");
      card.className = "drawer-card";
      card.innerHTML = `
        <div style="font-weight: 600; font-size: 12px; color: var(--color-accent);">${escapeHtml(m.chapterTitle)}</div>
        <div style="font-size: 13px; margin-top: 4px;">${escapeHtml(m.snippet)}</div>
      `;
      card.addEventListener("click", () => {
        window.engine.jumpToChapter(m.chapterIndex);
        this.updateReaderView();
        this.closeDrawer("drawer-search");
      });
      resultsContainer.appendChild(card);
    });
  }

  openBookProperties(book) {
    document.getElementById("prop-title").value = book.title;
    document.getElementById("prop-author").value = book.author;
    document.getElementById("prop-desc").value = book.description || "";
    document.getElementById("prop-meta-format").textContent = `Format: ${book.format}`;
    document.getElementById("prop-meta-size").textContent = `Size: ${Math.round((book.file_size_bytes || 0) / 1024)} KB`;
    document.getElementById("prop-meta-hash").textContent = `SHA-256: ${book.file_hash.substring(0, 16)}...`;

    const modal = document.getElementById("modal-properties");
    modal.style.display = "flex";

    const close = () => { modal.style.display = "none"; };
    document.getElementById("btn-close-properties").onclick = close;
    document.getElementById("btn-cancel-properties").onclick = close;

    document.getElementById("btn-save-properties").onclick = () => {
      window.db.updateBook(book.id, {
        title: document.getElementById("prop-title").value,
        author: document.getElementById("prop-author").value,
        description: document.getElementById("prop-desc").value
      });
      close();
      this.renderLibrary();
    };
  }
}

window.addEventListener("DOMContentLoaded", () => {
  window.app = new AppController();
});
