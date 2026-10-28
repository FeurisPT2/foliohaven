/**
 * Clean-room Data Layer: Icecream Ebook Reader Replica
 * Mirrors the SQLite schema defined in replica/schema.sql
 */

const SEED_BOOKS = [
  {
    id: "b1a2c3d4-0001-4000-8000-000000000001",
    title: "Alice's Adventures in Wonderland",
    author: "Lewis Carroll",
    format: "EPUB",
    file_path: "books/alice.epub",
    file_size_bytes: 184520,
    file_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    cover_image: null,
    total_pages: 164,
    current_page: 38,
    progress_percent: 23,
    cfi_position: "epubcfi(/6/4[chap02]!/4/2/10)",
    is_favorite: 1,
    is_deleted: 0,
    folder_id: "f01",
    date_added: "2026-10-20T10:15:00Z",
    last_read: "2026-10-28T14:30:00Z",
    description: "Alice falls down a rabbit hole into a whimsical fantasy realm populated by peculiar anthropomorphic creatures.",
    chapters: [
      {
        id: "c1",
        title: "Chapter I: Down the Rabbit-Hole",
        content: `Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do: once or twice she had peeped into the book her sister was reading, but it had no pictures or conversations in it, “and what is the use of a book,” thought Alice “without pictures or conversations?”

So she was considering in her own mind (as well as she could, for the hot day made her feel very sleepy and stupid), whether the pleasure of making a daisy-chain would be worth the trouble of getting up and picking the daisies, when suddenly a White Rabbit with pink eyes ran close by her.

There was nothing so very remarkable in that; nor did Alice think it so very much out of the way to hear the Rabbit say to itself, “Oh dear! Oh dear! I shall be late!” (when she thought it over afterwards, it occurred to her that she ought to have wondered at this, but at the time it all seemed quite natural); but when the Rabbit actually took a watch out of its waistcoat-pocket, and looked at it, and then hurried on, Alice started to her feet, for it flashed across her mind that she had never before seen a rabbit with either a waistcoat-pocket, or a watch to take out of it, and burning with curiosity, she ran across the field after it, and fortunately was just in time to see it pop down a large rabbit-hole under the hedge.

In another moment down went Alice after it, never once considering how in the world she was to get out again. The rabbit-hole went straight on like a tunnel for some way, and then dipped suddenly down, so suddenly that Alice had not a moment to think about stopping herself before she found herself falling down a very deep well.

Either the well was very deep, or she fell very slowly, for she had plenty of time as she went down to look about her and to wonder what was going to happen next. First, she tried to look down and make out what she was coming to, but it was too dark to see anything; then she looked at the sides of the well, and noticed that they were filled with cupboards and book-shelves; here and there she saw maps and pictures hung upon pegs.`
      },
      {
        id: "c2",
        title: "Chapter II: The Pool of Tears",
        content: `“Curiouser and curiouser!” cried Alice (she was so much surprised, that for the moment she quite forgot how to speak good English); “now I’m opening out like the largest telescope that ever was! Good-bye, feet!” (for when she looked down at her feet, they seemed to be almost out of sight, they were getting so far off). “Oh, my poor little feet, I wonder who will put on your shoes and stockings for you now, dears? I’m sure I shan’t be able! I shall be a great deal too far off to trouble myself about you: you must manage the best way you can;—but I must be kind to them,” thought Alice, “or perhaps they won’t walk the way I want to go! Let me see: I’ll give them a new pair of boots every Christmas.”

And she went on planning to herself how she would manage it. “They must go by the carrier,” she thought; “and how funny it’ll seem, sending presents to one’s own feet! And how odd the directions will look!

Alice’s Right Foot, Esq.
Hearthrug,
near the Fender,
(with Alice’s love).

Oh dear, what nonsense I’m talking!”

Just at this moment her head struck against the roof of the hall: in fact she was now more than nine feet high, and she at once took up the little golden key and hurried off to the garden door.`
      },
      {
        id: "c3",
        title: "Chapter III: A Caucus-Race and a Long Tale",
        content: `They were indeed a queer-looking party that assembled on the bank—the birds with draggled feathers, the animals with their fur clinging close to them, and all dripping wet, cross, and uncomfortable.

The first question of course was, how to get dry again: they had a consultation about this, and after a few minutes it seemed quite natural to Alice to find herself talking familiarly with them, as if she had known them all her life. Indeed, she had quite a long argument with the Lory, who at last turned sulky, and would only say, “I am older than you, and must know better;” and this Alice would not allow without knowing how old it was, and, as the Lory positively refused to tell its age, there was no more to be said.`
      }
    ]
  },
  {
    id: "b1a2c3d4-0001-4000-8000-000000000002",
    title: "Pride and Prejudice",
    author: "Jane Austen",
    format: "EPUB",
    file_path: "books/pride_and_prejudice.epub",
    file_size_bytes: 492000,
    file_hash: "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0",
    cover_image: null,
    total_pages: 380,
    current_page: 114,
    progress_percent: 30,
    cfi_position: "epubcfi(/6/12[chap05]!/4/2/4)",
    is_favorite: 1,
    is_deleted: 0,
    folder_id: "f01",
    date_added: "2026-10-18T09:20:00Z",
    last_read: "2026-10-27T19:45:00Z",
    description: "A romantic novel of manners following the turbulent relationship between Elizabeth Bennet and Fitzwilliam Darcy.",
    chapters: [
      {
        id: "c1",
        title: "Chapter 1",
        content: `It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.

However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters.

“My dear Mr. Bennet,” said his lady to him one day, “have you heard that Netherfield Park is let at last?”

Mr. Bennet replied that he had not.

“But it is,” returned she; “for Mrs. Long has just been here, and she told me all about it.”

Mr. Bennet made no answer.

“Do you not want to know who has taken it?” cried his wife impatiently.

“You want to tell me, and I have no objection to hearing it.”

This was invitation enough.`
      }
    ]
  },
  {
    id: "b1a2c3d4-0001-4000-8000-000000000003",
    title: "Frankenstein; or, The Modern Prometheus",
    author: "Mary Shelley",
    format: "PDF",
    file_path: "books/frankenstein.pdf",
    file_size_bytes: 842100,
    file_hash: "b2c3d4e5f6a17890123456789abcdef0123456789abcdef0123456789abcdef1",
    cover_image: null,
    total_pages: 240,
    current_page: 72,
    progress_percent: 30,
    cfi_position: null,
    is_favorite: 0,
    is_deleted: 0,
    folder_id: "f02",
    date_added: "2026-10-15T14:10:00Z",
    last_read: "2026-10-26T21:10:00Z",
    description: "Victor Frankenstein creates a sapient creature in an unorthodox scientific experiment with horrific consequences.",
    chapters: [
      {
        id: "c1",
        title: "Letter 1",
        content: `To Mrs. Saville, England.
St. Petersburgh, Dec. 11th, 17—.

You will rejoice to hear that no disaster has accompanied the commencement of an enterprise which you have regarded with such evil forebodings. I arrived here yesterday, and my first task is to assure my dear sister of my welfare and increasing confidence in the success of my undertaking.

I am already far north of London, and as I walk in the streets of Petersburgh, I feel a cold northern breeze play upon my cheeks, which braces my nerves and fills me with delight.`
      }
    ]
  },
  {
    id: "b1a2c3d4-0001-4000-8000-000000000004",
    title: "The Metamorphosis",
    author: "Franz Kafka",
    format: "MOBI",
    file_path: "books/metamorphosis.mobi",
    file_size_bytes: 124000,
    file_hash: "c3d4e5f6a1b27890123456789abcdef0123456789abcdef0123456789abcdef2",
    cover_image: null,
    total_pages: 85,
    current_page: 85,
    progress_percent: 100,
    cfi_position: null,
    is_favorite: 1,
    is_deleted: 0,
    folder_id: "f02",
    date_added: "2026-10-10T11:00:00Z",
    last_read: "2026-10-25T16:20:00Z",
    description: "Gregor Samsa wakes up one morning to find himself transformed into a monstrous vermin.",
    chapters: [
      {
        id: "c1",
        title: "Section I",
        content: `One morning, when Gregor Samsa woke from troubled dreams, he found himself transformed in his bed into a horrible vermin. He lay on his armour-like back, and if he lifted his head a little he could see his brown belly, slightly domed and divided by arches into stiff sections. The bedding was hardly able to cover it and seemed ready to slide off any moment. His many legs, pitifully thin compared with the size of the rest of him, waved helplessly about before his eyes.`
      }
    ]
  },
  {
    id: "b1a2c3d4-0001-4000-8000-000000000005",
    title: "The Time Machine",
    author: "H.G. Wells",
    format: "FB2",
    file_path: "books/time_machine.fb2",
    file_size_bytes: 156000,
    file_hash: "d4e5f6a1b2c37890123456789abcdef0123456789abcdef0123456789abcdef3",
    cover_image: null,
    total_pages: 130,
    current_page: 0,
    progress_percent: 0,
    cfi_position: null,
    is_favorite: 0,
    is_deleted: 0,
    folder_id: "f02",
    date_added: "2026-10-22T16:00:00Z",
    last_read: null,
    description: "A Victorian English scientist invents a device that enables him to travel into the far future.",
    chapters: [
      {
        id: "c1",
        title: "Chapter I: Introduction",
        content: `The Time Traveller (for so it will be convenient to speak of him) was expounding a recondite matter to us. His grey eyes shone and twinkled, and his usually pale face was flushed and animated. The fire burnt brightly, and the soft radiance of the incandescent lights in the lilies of silver caught the bubbles that flashed and passed in our glasses.`
      }
    ]
  },
  {
    id: "b1a2c3d4-0001-4000-8000-000000000006",
    title: "Adventures of Sherlock Holmes",
    author: "Arthur Conan Doyle",
    format: "TXT",
    file_path: "books/sherlock.txt",
    file_size_bytes: 310000,
    file_hash: "e5f6a1b2c3d47890123456789abcdef0123456789abcdef0123456789abcdef4",
    cover_image: null,
    total_pages: 280,
    current_page: 45,
    progress_percent: 16,
    cfi_position: null,
    is_favorite: 0,
    is_deleted: 0,
    folder_id: null,
    date_added: "2026-10-12T13:40:00Z",
    last_read: "2026-10-24T18:00:00Z",
    description: "A collection of twelve short stories featuring master detective Sherlock Holmes and Dr. John Watson.",
    chapters: [
      {
        id: "c1",
        title: "A Scandal in Bohemia",
        content: `To Sherlock Holmes she is always THE woman. I have seldom heard him mention her under any other name. In his eyes she eclipses and predominates the whole of her sex. It was not that he felt any emotion akin to love for Irene Adler. All emotions, and that one particularly, were abhorrent to his cold, precise but admirably balanced mind.`
      }
    ]
  },
  {
    id: "b1a2c3d4-0001-4000-8000-000000000007",
    title: "Spider-Man: Classic Adventures #1",
    author: "Stan Lee, Steve Ditko",
    format: "CBZ",
    file_path: "books/spiderman01.cbz",
    file_size_bytes: 14500000,
    file_hash: "f6a1b2c3d4e57890123456789abcdef0123456789abcdef0123456789abcdef5",
    cover_image: null,
    total_pages: 36,
    current_page: 12,
    progress_percent: 33,
    cfi_position: null,
    is_favorite: 0,
    is_deleted: 0,
    folder_id: null,
    date_added: "2026-10-25T11:20:00Z",
    last_read: "2026-10-28T09:15:00Z",
    description: "The origin story of Spider-Man and Peter Parker in high-resolution comic book format.",
    chapters: [
      {
        id: "c1",
        title: "Part 1: The Bite",
        content: `High School student Peter Parker visits a science exhibit where a radioactive spider bites his hand, forever altering his life and destiny.`
      }
    ]
  },
  {
    id: "b1a2c3d4-0001-4000-8000-000000000008",
    title: "Deleted Sample Ebook",
    author: "Anonymous",
    format: "EPUB",
    file_path: "books/sample_deleted.epub",
    file_size_bytes: 45000,
    file_hash: "123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef6",
    cover_image: null,
    total_pages: 50,
    current_page: 5,
    progress_percent: 10,
    cfi_position: null,
    is_favorite: 0,
    is_deleted: 1, // In Trash!
    folder_id: null,
    date_added: "2026-09-30T10:00:00Z",
    last_read: "2026-10-05T12:00:00Z",
    description: "A demonstration item residing in the trash bin for soft deletion testing.",
    chapters: [
      {
        id: "c1",
        title: "Archived Notes",
        content: `This item was moved to the trash bin and can be restored or purged permanently.`
      }
    ]
  }
];

const SEED_FOLDERS = [
  { id: "f01", name: "Classics", color: "#1f5fdb", sort_order: 1 },
  { id: "f02", name: "Sci-Fi & Fantasy", color: "#1b7a4b", sort_order: 2 }
];

const SEED_BOOKMARKS = [
  {
    id: "bm01",
    book_id: "b1a2c3d4-0001-4000-8000-000000000001",
    page_number: 14,
    cfi_position: "epubcfi(/6/2[chap01]!/4/2/40)",
    chapter_title: "Chapter I: Down the Rabbit-Hole",
    snippet_text: "There was nothing so very remarkable in that; nor did Alice think it so very much out of the way...",
    created_at: "2026-10-28T11:20:00Z"
  },
  {
    id: "bm02",
    book_id: "b1a2c3d4-0001-4000-8000-000000000001",
    page_number: 38,
    cfi_position: "epubcfi(/6/4[chap02]!/4/2/10)",
    chapter_title: "Chapter II: The Pool of Tears",
    snippet_text: "“Curiouser and curiouser!” cried Alice (she was so much surprised)...",
    created_at: "2026-10-28T14:15:00Z"
  }
];

const SEED_ANNOTATIONS = [
  {
    id: "ann01",
    book_id: "b1a2c3d4-0001-4000-8000-000000000001",
    page_number: 12,
    cfi_start: "epubcfi(/6/2[chap01]!/4/2/12)",
    cfi_end: "epubcfi(/6/2[chap01]!/4/2/24)",
    selected_text: "“and what is the use of a book,” thought Alice “without pictures or conversations?”",
    note_text: "Key opening theme: Alice's inquisitive nature and need for visual storytelling.",
    color_code: "yellow",
    created_at: "2026-10-28T12:00:00Z"
  },
  {
    id: "ann02",
    book_id: "b1a2c3d4-0001-4000-8000-000000000001",
    page_number: 15,
    cfi_start: "epubcfi(/6/2[chap01]!/4/2/50)",
    cfi_end: "epubcfi(/6/2[chap01]!/4/2/62)",
    selected_text: "the Rabbit actually took a watch out of its waistcoat-pocket, and looked at it, and then hurried on",
    note_text: "First clear absurd element breaking Victorian natural law.",
    color_code: "cyan",
    created_at: "2026-10-28T12:05:00Z"
  }
];

class Database {
  constructor() {
    this.booksKey = "ebookreader_books_v1";
    this.foldersKey = "ebookreader_folders_v1";
    this.bookmarksKey = "ebookreader_bookmarks_v1";
    this.annotationsKey = "ebookreader_annotations_v1";
    this.settingsKey = "ebookreader_settings_v1";
    this.init();
  }

  init() {
    if (!localStorage.getItem(this.booksKey)) {
      localStorage.setItem(this.booksKey, JSON.stringify(SEED_BOOKS));
    }
    if (!localStorage.getItem(this.foldersKey)) {
      localStorage.setItem(this.foldersKey, JSON.stringify(SEED_FOLDERS));
    }
    if (!localStorage.getItem(this.bookmarksKey)) {
      localStorage.setItem(this.bookmarksKey, JSON.stringify(SEED_BOOKMARKS));
    }
    if (!localStorage.getItem(this.annotationsKey)) {
      localStorage.setItem(this.annotationsKey, JSON.stringify(SEED_ANNOTATIONS));
    }
    if (!localStorage.getItem(this.settingsKey)) {
      localStorage.setItem(this.settingsKey, JSON.stringify({
        theme: "light",
        readingTheme: "day",
        fontSize: 16,
        lineSpacing: 1.5,
        columnCount: 2,
        fontFamily: "Georgia",
        textAlign: "justify",
        screenDim: 0,
        ttsVolume: 80,
        ttsSpeed: 1.0,
        viewMode: "grid" // "grid" or "table"
      }));
    }
  }

  getBooks() {
    return JSON.parse(localStorage.getItem(this.booksKey) || "[]");
  }

  saveBooks(books) {
    localStorage.setItem(this.booksKey, JSON.stringify(books));
  }

  getBookById(id) {
    return this.getBooks().find(b => b.id === id);
  }

  updateBook(id, updates) {
    const books = this.getBooks();
    const index = books.findIndex(b => b.id === id);
    if (index !== -1) {
      books[index] = { ...books[index], ...updates };
      this.saveBooks(books);
      return books[index];
    }
    return null;
  }

  addBook(book) {
    const books = this.getBooks();
    const newBook = {
      id: "b_" + Date.now().toString(36),
      title: book.title || "Untitled Document",
      author: book.author || "Unknown Author",
      format: book.format || "EPUB",
      file_path: book.file_path || "imported/" + (book.title || "document"),
      file_size_bytes: book.file_size_bytes || 102400,
      file_hash: book.file_hash || Math.random().toString(16).substring(2),
      cover_image: book.cover_image || null,
      total_pages: book.total_pages || 100,
      current_page: 0,
      progress_percent: 0,
      cfi_position: null,
      is_favorite: 0,
      is_deleted: 0,
      folder_id: null,
      date_added: new Date().toISOString(),
      last_read: null,
      description: book.description || "Imported ebook document.",
      chapters: book.chapters || [
        {
          id: "c1",
          title: "Introduction",
          content: book.content || "Document content imported into reader canvas."
        }
      ]
    };
    books.unshift(newBook);
    this.saveBooks(books);
    return newBook;
  }

  softDeleteBook(id) {
    return this.updateBook(id, { is_deleted: 1 });
  }

  restoreBook(id) {
    return this.updateBook(id, { is_deleted: 0 });
  }

  purgeBook(id) {
    const books = this.getBooks().filter(b => b.id !== id);
    this.saveBooks(books);
  }

  toggleFavorite(id) {
    const book = this.getBookById(id);
    if (book) {
      return this.updateBook(id, { is_favorite: book.is_favorite ? 0 : 1 });
    }
    return null;
  }

  getFolders() {
    return JSON.parse(localStorage.getItem(this.foldersKey) || "[]");
  }

  addFolder(name) {
    const folders = this.getFolders();
    const newFolder = {
      id: "f_" + Date.now().toString(36),
      name,
      color: "#1f5fdb",
      sort_order: folders.length + 1
    };
    folders.push(newFolder);
    localStorage.setItem(this.foldersKey, JSON.stringify(folders));
    return newFolder;
  }

  getBookmarks(bookId) {
    const all = JSON.parse(localStorage.getItem(this.bookmarksKey) || "[]");
    return bookId ? all.filter(bm => bm.book_id === bookId) : all;
  }

  addBookmark(bookmark) {
    const all = JSON.parse(localStorage.getItem(this.bookmarksKey) || "[]");
    const item = {
      id: "bm_" + Date.now().toString(36),
      created_at: new Date().toISOString(),
      ...bookmark
    };
    all.push(item);
    localStorage.setItem(this.bookmarksKey, JSON.stringify(all));
    return item;
  }

  deleteBookmark(id) {
    const all = JSON.parse(localStorage.getItem(this.bookmarksKey) || "[]").filter(bm => bm.id !== id);
    localStorage.setItem(this.bookmarksKey, JSON.stringify(all));
  }

  clearBookmarks(bookId) {
    const all = JSON.parse(localStorage.getItem(this.bookmarksKey) || "[]").filter(bm => bm.book_id !== bookId);
    localStorage.setItem(this.bookmarksKey, JSON.stringify(all));
  }

  getAnnotations(bookId) {
    const all = JSON.parse(localStorage.getItem(this.annotationsKey) || "[]");
    return bookId ? all.filter(a => a.book_id === bookId) : all;
  }

  addAnnotation(annotation) {
    const all = JSON.parse(localStorage.getItem(this.annotationsKey) || "[]");
    const item = {
      id: "ann_" + Date.now().toString(36),
      created_at: new Date().toISOString(),
      ...annotation
    };
    all.push(item);
    localStorage.setItem(this.annotationsKey, JSON.stringify(all));
    return item;
  }

  deleteAnnotation(id) {
    const all = JSON.parse(localStorage.getItem(this.annotationsKey) || "[]").filter(a => a.id !== id);
    localStorage.setItem(this.annotationsKey, JSON.stringify(all));
  }

  clearAnnotations(bookId) {
    const all = JSON.parse(localStorage.getItem(this.annotationsKey) || "[]").filter(a => a.book_id !== bookId);
    localStorage.setItem(this.annotationsKey, JSON.stringify(all));
  }

  getSettings() {
    return JSON.parse(localStorage.getItem(this.settingsKey) || "{}");
  }

  saveSettings(settings) {
    const current = this.getSettings();
    const updated = { ...current, ...settings };
    localStorage.setItem(this.settingsKey, JSON.stringify(updated));
    return updated;
  }
}

window.db = new Database();
