#ifndef DATABASE_MANAGER_H
#define DATABASE_MANAGER_H

#include <QString>
#include <QVector>
#include <QDateTime>
#include <optional>

struct BookRecord {
    int id{0};
    QString title;
    QString author;
    QString format;
    QString filePath;
    qint64 fileSize{0};
    int currentPage{1};
    int totalPages{1};
    double progressPercent{0.0};
    bool isFavorite{false};
    QString category;
    QString coverPath;
    QDateTime createdAt;
};

struct BookmarkRecord {
    int id{0};
    int bookId{0};
    int page{1};
    QString title;
    QDateTime createdAt;
};

struct AnnotationRecord {
    int id{0};
    int bookId{0};
    QString text;
    QString note;
    QString color; // amber, emerald, azure, rose
    int page{1};
    QDateTime createdAt;
};

class DatabaseManager {
public:
    static DatabaseManager& instance();

    bool init(const QString& customPath = QString());
    void close();

    int insertBook(const BookRecord& book);
    QVector<BookRecord> getBooks(const QString& searchQuery = QString(), const QString& category = QString());
    std::optional<BookRecord> getBookById(int id);
    std::optional<BookRecord> getBookByPath(const QString& filePath);
    bool updateProgress(int bookId, int currentPage, int totalPages, double progressPercent);
    bool toggleFavorite(int bookId, bool isFavorite);
    bool deleteBook(int bookId);

    int addBookmark(int bookId, int page, const QString& title);
    QVector<BookmarkRecord> getBookmarks(int bookId);
    bool deleteBookmark(int bookmarkId);

    int addAnnotation(int bookId, const QString& text, const QString& note, const QString& color, int page);
    QVector<AnnotationRecord> getAnnotations(int bookId);
    bool deleteAnnotation(int annotationId);

    bool clearAllData();

private:
    DatabaseManager() = default;
    ~DatabaseManager();
    DatabaseManager(const DatabaseManager&) = delete;
    DatabaseManager& operator=(const DatabaseManager&) = delete;

    QString m_connectionName{"FolioHaven_Connection"};
};

#endif // DATABASE_MANAGER_H
