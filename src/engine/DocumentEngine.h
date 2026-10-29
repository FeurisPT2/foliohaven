#ifndef DOCUMENT_ENGINE_H
#define DOCUMENT_ENGINE_H

#include <QString>
#include <QVector>
#include <QPair>

struct SearchHit {
    int pageIndex{0};
    QString snippet;
};

struct LoadedBook {
    QString title;
    QString author;
    QString format;
    QString filePath;
    qint64 fileSize{0};
    QVector<QString> pages;
    QVector<QPair<QString, int>> toc; // Title, pageIndex
    bool isValid{false};
    QString errorMessage;
};

class DocumentEngine {
public:
    static LoadedBook loadDocument(const QString& filePath);
    static QVector<SearchHit> search(const LoadedBook& book, const QString& query);

private:
    static LoadedBook loadPlainText(const QString& filePath);
    static LoadedBook loadEpub(const QString& filePath);
    static LoadedBook loadPdf(const QString& filePath);
    static LoadedBook loadCbz(const QString& filePath);
    static LoadedBook loadFb2(const QString& filePath);
    static LoadedBook loadGenericDocument(const QString& filePath, const QString& format);
};

#endif // DOCUMENT_ENGINE_H
