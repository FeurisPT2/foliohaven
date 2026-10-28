/**
 * Reflowable & Fixed Document Layout Engine
 * Clean-room C++ IDocumentEngine equivalent implemented in browser runtime
 */

class DocumentEngine {
  constructor() {
    this.currentBook = null;
    this.currentChapterIndex = 0;
    this.currentSpreadIndex = 0; // Current column spread
    this.pagesInChapter = [];
    this.columnCount = 2;
    this.fontSize = 16;
    this.lineSpacing = 1.5;
    this.fontFamily = "Georgia";
    this.textAlign = "justify";
    this.isFixedLayout = false;
  }

  loadBook(book, savedSettings = {}) {
    this.currentBook = book;
    this.currentChapterIndex = 0;
    this.currentSpreadIndex = 0;
    this.isFixedLayout = (book.format === "PDF" || book.format === "CBZ");
    
    if (savedSettings.columnCount) this.columnCount = savedSettings.columnCount;
    if (savedSettings.fontSize) this.fontSize = savedSettings.fontSize;
    if (savedSettings.lineSpacing) this.lineSpacing = savedSettings.lineSpacing;
    if (savedSettings.fontFamily) this.fontFamily = savedSettings.fontFamily;
    if (savedSettings.textAlign) this.textAlign = savedSettings.textAlign;

    // Restore saved page if applicable
    this.paginateCurrentChapter();
    return this.renderCurrentView();
  }

  paginateCurrentChapter() {
    if (!this.currentBook || !this.currentBook.chapters) return;
    const chapter = this.currentBook.chapters[this.currentChapterIndex];
    if (!chapter) return;

    if (this.isFixedLayout) {
      // Fixed layout page
      this.pagesInChapter = [
        {
          title: chapter.title,
          paragraphs: [chapter.content]
        }
      ];
      return;
    }

    // Split chapter into readable paragraphs
    const rawParagraphs = chapter.content
      .split(/\n\s*\n/)
      .map(p => p.trim())
      .filter(p => p.length > 0);

    // Heuristic chunking for columns based on character count and font size
    const charsPerColumn = Math.floor(800 * (16 / this.fontSize));
    const columns = [];
    let currentColumn = [];
    let currentLen = 0;

    for (const p of rawParagraphs) {
      if (currentLen + p.length > charsPerColumn && currentColumn.length > 0) {
        columns.push(currentColumn);
        currentColumn = [p];
        currentLen = p.length;
      } else {
        currentColumn.push(p);
        currentLen += p.length;
      }
    }
    if (currentColumn.length > 0) {
      columns.push(currentColumn);
    }

    // If 2 columns, group pairs into spreads
    if (this.columnCount === 2) {
      this.pagesInChapter = [];
      for (let i = 0; i < columns.length; i += 2) {
        this.pagesInChapter.push({
          left: columns[i] || [],
          right: columns[i + 1] || null
        });
      }
    } else {
      this.pagesInChapter = columns.map(c => ({ left: c, right: null }));
    }

    if (this.pagesInChapter.length === 0) {
      this.pagesInChapter = [{ left: ["(Empty chapter)"], right: null }];
    }
  }

  renderCurrentView() {
    if (!this.currentBook || this.pagesInChapter.length === 0) {
      return { html: "<p>No content loaded.</p>", pageInfo: "Page 0 / 0" };
    }

    const spread = this.pagesInChapter[this.currentSpreadIndex] || this.pagesInChapter[0];
    const chapter = this.currentBook.chapters[this.currentChapterIndex];

    let html = "";
    if (this.isFixedLayout) {
      html = `
        <div class="fixed-canvas-container">
          <div class="fixed-page-sheet">
            <h3 class="fixed-doc-title">${chapter.title}</h3>
            <div class="fixed-doc-body">${spread.paragraphs.join("<br><br>")}</div>
          </div>
        </div>
      `;
    } else if (this.columnCount === 2) {
      html = `
        <div class="two-column-spread" style="font-family: ${this.fontFamily}; font-size: ${this.fontSize}px; line-height: ${this.lineSpacing}; text-align: ${this.textAlign};">
          <div class="reader-column column-left">
            ${this.currentSpreadIndex === 0 ? `<h2 class="chapter-heading">${chapter.title}</h2>` : ""}
            ${spread.left.map(p => `<p class="reflow-para">${this.applyHighlights(p)}</p>`).join("")}
          </div>
          <div class="spread-gutter"></div>
          <div class="reader-column column-right">
            ${spread.right ? spread.right.map(p => `<p class="reflow-para">${this.applyHighlights(p)}</p>`).join("") : ""}
          </div>
        </div>
      `;
    } else {
      html = `
        <div class="single-column-spread" style="font-family: ${this.fontFamily}; font-size: ${this.fontSize}px; line-height: ${this.lineSpacing}; text-align: ${this.textAlign};">
          ${this.currentSpreadIndex === 0 ? `<h2 class="chapter-heading">${chapter.title}</h2>` : ""}
          ${spread.left.map(p => `<p class="reflow-para">${this.applyHighlights(p)}</p>`).join("")}
        </div>
      `;
    }

    // Calculate approximate overall page & progress
    const totalChapters = this.currentBook.chapters.length;
    const totalSpreadsInChapter = this.pagesInChapter.length;
    const globalPercent = Math.min(100, Math.round(
      ((this.currentChapterIndex * totalSpreadsInChapter + this.currentSpreadIndex + 1) /
       (totalChapters * totalSpreadsInChapter)) * 100
    ));

    return {
      html,
      chapterTitle: chapter.title,
      spreadIndex: this.currentSpreadIndex + 1,
      totalSpreadsInChapter,
      chapterIndex: this.currentChapterIndex + 1,
      totalChapters,
      globalPercent
    };
  }

  nextPage() {
    if (this.currentSpreadIndex < this.pagesInChapter.length - 1) {
      this.currentSpreadIndex++;
      return this.renderCurrentView();
    } else if (this.currentChapterIndex < this.currentBook.chapters.length - 1) {
      this.currentChapterIndex++;
      this.currentSpreadIndex = 0;
      this.paginateCurrentChapter();
      return this.renderCurrentView();
    }
    return null; // At end of book
  }

  prevPage() {
    if (this.currentSpreadIndex > 0) {
      this.currentSpreadIndex--;
      return this.renderCurrentView();
    } else if (this.currentChapterIndex > 0) {
      this.currentChapterIndex--;
      this.paginateCurrentChapter();
      this.currentSpreadIndex = this.pagesInChapter.length - 1;
      return this.renderCurrentView();
    }
    return null; // At start of book
  }

  jumpToChapter(chapterIndex) {
    if (chapterIndex >= 0 && chapterIndex < this.currentBook.chapters.length) {
      this.currentChapterIndex = chapterIndex;
      this.currentSpreadIndex = 0;
      this.paginateCurrentChapter();
      return this.renderCurrentView();
    }
    return null;
  }

  setColumnCount(count) {
    this.columnCount = count;
    this.paginateCurrentChapter();
    if (this.currentSpreadIndex >= this.pagesInChapter.length) {
      this.currentSpreadIndex = this.pagesInChapter.length - 1;
    }
    return this.renderCurrentView();
  }

  setFontSize(delta) {
    this.fontSize = Math.max(12, Math.min(32, this.fontSize + delta));
    this.paginateCurrentChapter();
    return this.renderCurrentView();
  }

  setLineSpacing(spacing) {
    this.lineSpacing = spacing;
    this.paginateCurrentChapter();
    return this.renderCurrentView();
  }

  setFontFamily(family) {
    this.fontFamily = family;
    return this.renderCurrentView();
  }

  setTextAlign(align) {
    this.textAlign = align;
    return this.renderCurrentView();
  }

  applyHighlights(text) {
    if (!this.currentBook) return text;
    const annotations = window.db ? window.db.getAnnotations(this.currentBook.id) : [];
    let highlighted = text;
    for (const ann of annotations) {
      if (ann.selected_text && text.includes(ann.selected_text)) {
        const regex = new RegExp(escapeRegExp(ann.selected_text), "g");
        highlighted = highlighted.replace(
          regex,
          `<mark class="highlight-${ann.color_code}" data-ann-id="${ann.id}" title="${escapeHtml(ann.note_text || 'Highlight')}">${escapeHtml(ann.selected_text)}</mark>`
        );
      }
    }
    return highlighted;
  }

  searchInBook(query) {
    if (!this.currentBook || !query || query.trim().length === 0) return [];
    const results = [];
    const q = query.toLowerCase();

    this.currentBook.chapters.forEach((chap, cIdx) => {
      const text = chap.content;
      let pos = 0;
      while ((pos = text.toLowerCase().indexOf(q, pos)) !== -1) {
        const start = Math.max(0, pos - 40);
        const end = Math.min(text.length, pos + query.length + 40);
        const snippet = (start > 0 ? "..." : "") + text.substring(start, end) + (end < text.length ? "..." : "");
        results.push({
          chapterIndex: cIdx,
          chapterTitle: chap.title,
          snippet,
          pos
        });
        pos += query.length;
      }
    });
    return results;
  }
}

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function escapeHtml(string) {
  return String(string)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

window.engine = new DocumentEngine();
