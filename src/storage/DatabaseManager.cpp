#include "DatabaseManager.h"

#include <QSqlDatabase>
#include <QSqlQuery>
#include <QSqlError>
#include <QStandardPaths>
#include <QDir>
#include <QDebug>

DatabaseManager& DatabaseManager::instance() {
    static DatabaseManager instance;
    return instance;
}

DatabaseManager::~DatabaseManager() {
    close();
}

void DatabaseManager::close() {
    if (QSqlDatabase::contains(m_connectionName)) {
        QSqlDatabase db = QSqlDatabase::database(m_connectionName);
        if (db.isOpen()) {
            db.close();
        }
    }
}

bool DatabaseManager::init(const QString& customPath) {
    QString dbPath = customPath;
    if (dbPath.isEmpty()) {
        QString appData = QStandardPaths::writableLocation(QStandardPaths::AppDataLocation);
        QDir dir(appData);
        if (!dir.exists()) {
            dir.mkpath(".");
        }
        dbPath = dir.filePath("foliohaven_library.db");
    }

    QSqlDatabase db;
    if (QSqlDatabase::contains(m_connectionName)) {
        db = QSqlDatabase::database(m_connectionName);
    } else {
        db = QSqlDatabase::addDatabase("QSQLITE", m_connectionName);
    }

    db.setDatabaseName(dbPath);
    if (!db.open()) {
        qCritical() << "Failed to open SQLite database:" << db.lastError().text();
        return false;
    }

    QSqlQuery q(db);
    q.exec("PRAGMA foreign_keys = ON;");
    q.exec("PRAGMA journal_mode = WAL;");

    // Create books table
    const QString createBooksTable = R"(
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            format TEXT NOT NULL,
            file_path TEXT NOT NULL UNIQUE,
            file_size INTEGER NOT NULL DEFAULT 0,
            current_page INTEGER NOT NULL DEFAULT 1,
            total_pages INTEGER NOT NULL DEFAULT 1,
            progress_percent REAL NOT NULL DEFAULT 0.0,
            is_favorite INTEGER NOT NULL DEFAULT 0,
            category TEXT DEFAULT 'All Books',
            cover_path TEXT,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        );
    )";
    if (!q.exec(createBooksTable)) {
        qWarning() << "Error creating books table:" << q.lastError().text();
    }

    // Create bookmarks table
    const QString createBookmarksTable = R"(
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            page INTEGER NOT NULL DEFAULT 1,
            title TEXT,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        );
    )";
    q.exec(createBookmarksTable);

    // Create annotations table
    const QString createAnnotationsTable = R"(
        CREATE TABLE IF NOT EXISTS annotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            text TEXT NOT NULL,
            note TEXT,
            color TEXT NOT NULL DEFAULT 'amber',
            page INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        );
    )";
    q.exec(createAnnotationsTable);

    return true;
}

int DatabaseManager::insertBook(const BookRecord& book) {
    QSqlDatabase db = QSqlDatabase::database(m_connectionName);
    QSqlQuery q(db);
    q.prepare(R"(
        INSERT INTO books (title, author, format, file_path, file_size, current_page, total_pages, progress_percent, is_favorite, category, cover_path)
        VALUES (:title, :author, :format, :file_path, :file_size, :current_page, :total_pages, :progress_percent, :is_favorite, :category, :cover_path)
        ON CONFLICT(file_path) DO UPDATE SET
            title = excluded.title,
            author = excluded.author,
            file_size = excluded.file_size
    )");
    q.bindValue(":title", book.title);
    q.bindValue(":author", book.author);
    q.bindValue(":format", book.format);
    q.bindValue(":file_path", book.filePath);
    q.bindValue(":file_size", book.fileSize);
    q.bindValue(":current_page", book.currentPage);
    q.bindValue(":total_pages", book.totalPages);
    q.bindValue(":progress_percent", book.progressPercent);
    q.bindValue(":is_favorite", book.isFavorite ? 1 : 0);
    q.bindValue(":category", book.category.isEmpty() ? "All Books" : book.category);
    q.bindValue(":cover_path", book.coverPath);

    if (!q.exec()) {
        qWarning() << "Failed to insert/update book:" << q.lastError().text();
        return -1;
    }

    QVariant lastId = q.lastInsertId();
    if (lastId.isValid() && lastId.toInt() > 0) {
        return lastId.toInt();
    }

    // If updated, fetch existing ID
    auto existing = getBookByPath(book.filePath);
    return existing ? existing->id : -1;
}

QVector<BookRecord> DatabaseManager::getBooks(const QString& searchQuery, const QString& category) {
    QVector<BookRecord> results;
    QSqlDatabase db = QSqlDatabase::database(m_connectionName);
    QSqlQuery q(db);

    QString queryStr = "SELECT id, title, author, format, file_path, file_size, current_page, total_pages, progress_percent, is_favorite, category, cover_path, created_at FROM books WHERE 1=1";

    if (!searchQuery.isEmpty()) {
        queryStr += " AND (title LIKE :search OR author LIKE :search)";
    }
    if (category == "Favorites") {
        queryStr += " AND is_favorite = 1";
    } else if (category == "Currently Reading") {
        queryStr += " AND progress_percent > 0 AND progress_percent < 100";
    } else if (category == "Completed") {
        queryStr += " AND progress_percent >= 100";
    } else if (!category.isEmpty() && category != "All Books") {
        queryStr += " AND (category = :cat OR format = :cat)";
    }

    queryStr += " ORDER BY id DESC";

    q.prepare(queryStr);
    if (!searchQuery.isEmpty()) {
        q.bindValue(":search", "%" + searchQuery + "%");
    }
    if (!category.isEmpty() && category != "All Books" && category != "Favorites" && category != "Currently Reading" && category != "Completed") {
        q.bindValue(":cat", category);
    }

    if (q.exec()) {
        while (q.next()) {
            BookRecord b;
            b.id = q.value(0).toInt();
            b.title = q.value(1).toString();
            b.author = q.value(2).toString();
            b.format = q.value(3).toString();
            b.filePath = q.value(4).toString();
            b.fileSize = q.value(5).toLongLong();
            b.currentPage = q.value(6).toInt();
            b.totalPages = q.value(7).toInt();
            b.progressPercent = q.value(8).toDouble();
            b.isFavorite = q.value(9).toInt() == 1;
            b.category = q.value(10).toString();
            b.coverPath = q.value(11).toString();
            b.createdAt = QDateTime::fromString(q.value(12).toString(), Qt::ISODate);
            results.append(b);
        }
    } else {
        qWarning() << "Failed to fetch books:" << q.lastError().text();
    }
    return results;
}

std::optional<BookRecord> DatabaseManager::getBookById(int id) {
    QSqlDatabase db = QSqlDatabase::database(m_connectionName);
    QSqlQuery q(db);
    q.prepare("SELECT id, title, author, format, file_path, file_size, current_page, total_pages, progress_percent, is_favorite, category, cover_path, created_at FROM books WHERE id = :id");
    q.bindValue(":id", id);
    if (q.exec() && q.next()) {
        BookRecord b;
        b.id = q.value(0).toInt();
        b.title = q.value(1).toString();
        b.author = q.value(2).toString();
        b.format = q.value(3).toString();
        b.filePath = q.value(4).toString();
        b.fileSize = q.value(5).toLongLong();
        b.currentPage = q.value(6).toInt();
        b.totalPages = q.value(7).toInt();
        b.progressPercent = q.value(8).toDouble();
        b.isFavorite = q.value(9).toInt() == 1;
        b.category = q.value(10).toString();
        b.coverPath = q.value(11).toString();
        b.createdAt = QDateTime::fromString(q.value(12).toString(), Qt::ISODate);
        return b;
    }
    return std::nullopt;
}

std::optional<BookRecord> DatabaseManager::getBookByPath(const QString& filePath) {
    QSqlDatabase db = QSqlDatabase::database(m_connectionName);
    QSqlQuery q(db);
    q.prepare("SELECT id, title, author, format, file_path, file_size, current_page, total_pages, progress_percent, is_favorite, category, cover_path, created_at FROM books WHERE file_path = :path");
    q.bindValue(":path", filePath);
    if (q.exec() && q.next()) {
        BookRecord b;
        b.id = q.value(0).toInt();
        b.title = q.value(1).toString();
        b.author = q.value(2).toString();
        b.format = q.value(3).toString();
        b.filePath = q.value(4).toString();
        b.fileSize = q.value(5).toLongLong();
        b.currentPage = q.value(6).toInt();
        b.totalPages = q.value(7).toInt();
        b.progressPercent = q.value(8).toDouble();
        b.isFavorite = q.value(9).toInt() == 1;
        b.category = q.value(10).toString();
        b.coverPath = q.value(11).toString();
        b.createdAt = QDateTime::fromString(q.value(12).toString(), Qt::ISODate);
        return b;
    }
    return std::nullopt;
}

bool DatabaseManager::updateProgress(int bookId, int currentPage, int totalPages, double progressPercent) {
    QSqlDatabase db = QSqlDatabase::database(m_connectionName);
    QSqlQuery q(db);
    q.prepare("UPDATE books SET current_page = :page, total_pages = :total, progress_percent = :progress WHERE id = :id");
    q.bindValue(":page", currentPage);
    q.bindValue(":total", totalPages);
    q.bindValue(":progress", progressPercent);
    q.bindValue(":id", bookId);
    return q.exec();
}

bool DatabaseManager::toggleFavorite(int bookId, bool isFavorite) {
    QSqlDatabase db = QSqlDatabase::database(m_connectionName);
    QSqlQuery q(db);
    q.prepare("UPDATE books SET is_favorite = :fav WHERE id = :id");
    q.bindValue(":fav", isFavorite ? 1 : 0);
    q.bindValue(":id", bookId);
    return q.exec();
}

bool DatabaseManager::deleteBook(int bookId) {
    QSqlDatabase db = QSqlDatabase::database(m_connectionName);
    QSqlQuery q(db);
    q.prepare("DELETE FROM books WHERE id = :id");
    q.bindValue(":id", bookId);
    return q.exec();
}

int DatabaseManager::addBookmark(int bookId, int page, const QString& title) {
    QSqlDatabase db = QSqlDatabase::database(m_connectionName);
    QSqlQuery q(db);
    q.prepare("INSERT INTO bookmarks (book_id, page, title) VALUES (:book_id, :page, :title)");
    q.bindValue(":book_id", bookId);
    q.bindValue(":page", page);
    q.bindValue(":title", title.isEmpty() ? QString("Page %1").arg(page) : title);
    if (q.exec()) {
        return q.lastInsertId().toInt();
    }
    return -1;
}

QVector<BookmarkRecord> DatabaseManager::getBookmarks(int bookId) {
    QVector<BookmarkRecord> list;
    QSqlDatabase db = QSqlDatabase::database(m_connectionName);
    QSqlQuery q(db);
    q.prepare("SELECT id, book_id, page, title, created_at FROM bookmarks WHERE book_id = :book_id ORDER BY page ASC");
    q.bindValue(":book_id", bookId);
    if (q.exec()) {
        while (q.next()) {
            BookmarkRecord bm;
            bm.id = q.value(0).toInt();
            bm.bookId = q.value(1).toInt();
            bm.page = q.value(2).toInt();
            bm.title = q.value(3).toString();
            bm.createdAt = QDateTime::fromString(q.value(4).toString(), Qt::ISODate);
            list.append(bm);
        }
    }
    return list;
}

bool DatabaseManager::deleteBookmark(int bookmarkId) {
    QSqlDatabase db = QSqlDatabase::database(m_connectionName);
    QSqlQuery q(db);
    q.prepare("DELETE FROM bookmarks WHERE id = :id");
    q.bindValue(":id", bookmarkId);
    return q.exec();
}

int DatabaseManager::addAnnotation(int bookId, const QString& text, const QString& note, const QString& color, int page) {
    QSqlDatabase db = QSqlDatabase::database(m_connectionName);
    QSqlQuery q(db);
    q.prepare("INSERT INTO annotations (book_id, text, note, color, page) VALUES (:book_id, :text, :note, :color, :page)");
    q.bindValue(":book_id", bookId);
    q.bindValue(":text", text);
    q.bindValue(":note", note);
    q.bindValue(":color", color);
    q.bindValue(":page", page);
    if (q.exec()) {
        return q.lastInsertId().toInt();
    }
    return -1;
}

QVector<AnnotationRecord> DatabaseManager::getAnnotations(int bookId) {
    QVector<AnnotationRecord> list;
    QSqlDatabase db = QSqlDatabase::database(m_connectionName);
    QSqlQuery q(db);
    q.prepare("SELECT id, book_id, text, note, color, page, created_at FROM annotations WHERE book_id = :book_id ORDER BY page ASC, id ASC");
    q.bindValue(":book_id", bookId);
    if (q.exec()) {
        while (q.next()) {
            AnnotationRecord a;
            a.id = q.value(0).toInt();
            a.bookId = q.value(1).toInt();
            a.text = q.value(2).toString();
            a.note = q.value(3).toString();
            a.color = q.value(4).toString();
            a.page = q.value(5).toInt();
            a.createdAt = QDateTime::fromString(q.value(6).toString(), Qt::ISODate);
            list.append(a);
        }
    }
    return list;
}

bool DatabaseManager::deleteAnnotation(int annotationId) {
    QSqlDatabase db = QSqlDatabase::database(m_connectionName);
    QSqlQuery q(db);
    q.prepare("DELETE FROM annotations WHERE id = :id");
    q.bindValue(":id", annotationId);
    return q.exec();
}

bool DatabaseManager::clearAllData() {
    QSqlDatabase db = QSqlDatabase::database(m_connectionName);
    QSqlQuery q(db);
    return q.exec("DELETE FROM bookmarks;") && q.exec("DELETE FROM annotations;") && q.exec("DELETE FROM books;");
}
