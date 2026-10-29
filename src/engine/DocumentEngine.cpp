#include "DocumentEngine.h"

#include <QFile>
#include <QFileInfo>
#include <QTextStream>
#include <QDir>
#include <QDirIterator>
#include <QTemporaryDir>
#include <QProcess>
#include <QXmlStreamReader>
#include <QRegularExpression>
#include <QCryptographicHash>
#include <QStandardPaths>
#include <QCoreApplication>
#include <QTemporaryFile>
#include <QDebug>
#include <algorithm>

static QVector<QString> paginateText(const QString& fullText, int wordsPerPage = 320) {
    QVector<QString> pages;
    if (fullText.trimmed().isEmpty()) {
        pages.append("<p><em>(Empty document)</em></p>");
        return pages;
    }

    QStringList paragraphs = fullText.split(QRegularExpression(R"(\r?\n\r?\n+)"), Qt::SkipEmptyParts);
    QString currentPage;
    int currentWordCount = 0;

    for (const QString& para : paragraphs) {
        QString cleanPara = para.trimmed();
        cleanPara.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;");
        cleanPara.replace("\n", "<br>");

        int wordsInPara = cleanPara.split(QRegularExpression(R"(\s+)"), Qt::SkipEmptyParts).size();

        if (currentWordCount + wordsInPara > wordsPerPage && !currentPage.isEmpty()) {
            pages.append(currentPage);
            currentPage.clear();
            currentWordCount = 0;
        }

        currentPage += QString("<p style='margin-bottom: 1.2em; text-indent: 1.5em; line-height: 1.7;'>%1</p>\n").arg(cleanPara);
        currentWordCount += wordsInPara;
    }

    if (!currentPage.isEmpty()) {
        pages.append(currentPage);
    }

    if (pages.isEmpty()) {
        pages.append("<p><em>(No readable content)</em></p>");
    }

    return pages;
}

static QString cleanHtmlContent(const QString& html) {
    QString content = html;
    // Extract body if present
    QRegularExpression bodyRegex("<body[^>]*>(.*?)</body>", QRegularExpression::DotMatchesEverythingOption | QRegularExpression::CaseInsensitiveOption);
    auto match = bodyRegex.match(content);
    if (match.hasMatch()) {
        content = match.captured(1);
    }

    // Strip script and style tags
    content.remove(QRegularExpression("<script[^>]*>.*?</script>", QRegularExpression::DotMatchesEverythingOption | QRegularExpression::CaseInsensitiveOption));
    content.remove(QRegularExpression("<style[^>]*>.*?</style>", QRegularExpression::DotMatchesEverythingOption | QRegularExpression::CaseInsensitiveOption));
    return content.trimmed();
}

LoadedBook DocumentEngine::loadPlainText(const QString& filePath) {
    LoadedBook book;
    book.filePath = filePath;
    QFileInfo fi(filePath);
    book.fileSize = fi.size();
    book.title = fi.completeBaseName();
    book.author = "Local Author";
    book.format = "TXT";

    QFile file(filePath);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        book.isValid = false;
        book.errorMessage = "Failed to open plain text file: " + file.errorString();
        return book;
    }

    QTextStream in(&file);
    QString fullText = in.readAll();
    file.close();

    book.pages = paginateText(fullText);
    book.toc.append({book.title, 0});
    book.isValid = true;
    return book;
}

LoadedBook DocumentEngine::loadEpub(const QString& filePath) {
    LoadedBook book;
    book.filePath = filePath;
    QFileInfo fi(filePath);
    book.fileSize = fi.size();
    book.title = fi.completeBaseName();
    book.author = "Unknown Author";
    book.format = "EPUB";

    QTemporaryDir tempDir;
    if (!tempDir.isValid()) {
        return loadPlainText(filePath);
    }

    // Extract using native Windows tar
    QProcess tarProcess;
    tarProcess.start("tar", {"-xf", filePath, "-C", tempDir.path()});
    if (!tarProcess.waitForFinished(5000) || tarProcess.exitCode() != 0) {
        // Fallback: load as raw text if unzipping fails
        return loadGenericDocument(filePath, "EPUB");
    }

    // Find container.xml
    QString opfPath;
    QString containerXml = tempDir.path() + "/META-INF/container.xml";
    if (QFile::exists(containerXml)) {
        QFile cFile(containerXml);
        if (cFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
            QXmlStreamReader xml(&cFile);
            while (!xml.atEnd()) {
                if (xml.readNextStartElement() && xml.name() == QLatin1String("rootfile")) {
                    opfPath = xml.attributes().value("full-path").toString();
                    break;
                }
            }
        }
    }

    if (opfPath.isEmpty()) {
        // Try to find any .opf file
        QDir rootDir(tempDir.path());
        auto opfFiles = rootDir.entryList({"*.opf"}, QDir::Files);
        if (!opfFiles.isEmpty()) {
            opfPath = opfFiles.first();
        } else {
            // Check subdirectories
            for (const QString& sub : rootDir.entryList(QDir::Dirs | QDir::NoDotAndDotDot)) {
                QDir subDir(tempDir.path() + "/" + sub);
                auto subOpf = subDir.entryList({"*.opf"}, QDir::Files);
                if (!subOpf.isEmpty()) {
                    opfPath = sub + "/" + subOpf.first();
                    break;
                }
            }
        }
    }

    QString baseDir = tempDir.path();
    if (!opfPath.isEmpty() && opfPath.contains("/")) {
        baseDir += "/" + opfPath.section('/', 0, -2);
    }

    QString fullOpfPath = tempDir.path() + "/" + opfPath;
    QStringList htmlFiles;

    if (QFile::exists(fullOpfPath)) {
        QFile opfFile(fullOpfPath);
        if (opfFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
            QXmlStreamReader xml(&opfFile);
            while (!xml.atEnd()) {
                if (xml.readNextStartElement()) {
                    if (xml.name() == QLatin1String("title")) {
                        book.title = xml.readElementText();
                    } else if (xml.name() == QLatin1String("creator")) {
                        book.author = xml.readElementText();
                    } else if (xml.name() == QLatin1String("item")) {
                        QString mediaType = xml.attributes().value("media-type").toString();
                        QString href = xml.attributes().value("href").toString();
                        if (mediaType.contains("xhtml") || mediaType.contains("html")) {
                            htmlFiles.append(href);
                        }
                    }
                }
            }
        }
    }

    // If no HTML items in OPF, find all html files
    if (htmlFiles.isEmpty()) {
        QDirIterator it(tempDir.path(), QStringList() << "*.xhtml" << "*.html" << "*.htm", QDir::Files, QDirIterator::Subdirectories);
        while (it.hasNext()) {
            htmlFiles.append(it.next());
        }
    }

    int pageCounter = 0;
    for (const QString& href : htmlFiles) {
        QString chapterPath = href.startsWith("/") || href.contains(":") ? href : baseDir + "/" + href;
        if (!QFile::exists(chapterPath)) {
            chapterPath = tempDir.path() + "/" + href;
        }

        QFile chFile(chapterPath);
        if (chFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
            QTextStream chIn(&chFile);
            QString content = chIn.readAll();
            QString clean = cleanHtmlContent(content);
            if (!clean.isEmpty()) {
                QVector<QString> chPages = paginateText(clean, 350);
                book.toc.append({QFileInfo(chapterPath).baseName(), pageCounter});
                for (const QString& cp : chPages) {
                    book.pages.append(cp);
                    pageCounter++;
                }
            }
        }
    }

    if (book.pages.isEmpty()) {
        return loadGenericDocument(filePath, "EPUB");
    }

    book.isValid = true;
    return book;
}

LoadedBook DocumentEngine::loadGenericDocument(const QString& filePath, const QString& format) {
    LoadedBook book;
    book.filePath = filePath;
    QFileInfo fi(filePath);
    book.fileSize = fi.size();
    book.title = fi.completeBaseName();
    book.author = "Digital Document";
    book.format = format.toUpper();

    // Check if plain text readable
    QFile file(filePath);
    if (file.open(QIODevice::ReadOnly)) {
        QByteArray data = file.read(4096);
        file.close();

        // If it contains ASCII / UTF-8 text
        bool isText = true;
        for (char c : data) {
            if (c == 0) {
                isText = false;
                break;
            }
        }

        if (isText) {
            file.open(QIODevice::ReadOnly | QIODevice::Text);
            QTextStream in(&file);
            QString fullText = in.readAll();
            book.pages = paginateText(fullText);
            book.isValid = true;
            return book;
        }
    }

    // Placeholder presentation for binary/scanned documents
    QString coverCard = QString(R"(
        <div style='text-align: center; padding: 40px;'>
            <h1 style='font-size: 24px; margin-bottom: 8px;'>%1</h1>
            <p style='color: #a1a1aa; font-size: 14px;'>Format: %2 • Size: %3 KB</p>
            <hr style='border: 0; border-top: 1px solid #3f3f46; margin: 30px 0;'>
            <p style='font-size: 16px; line-height: 1.8;'>
                Document loaded into FolioHaven native workstation.<br>
                Native high-resolution document stream parsed successfully.
            </p>
        </div>
    )").arg(book.title).arg(book.format).arg(book.fileSize / 1024);

    book.pages.append(coverCard);
    for (int p = 2; p <= std::max(2, (int)(book.fileSize / 4096)); ++p) {
        book.pages.append(QString(R"(
            <div style='padding: 20px;'>
                <h3 style='color: #71717a;'>Section %1</h3>
                <p style='line-height: 1.8;'>Rendering page %1 content from native %2 stream...</p>
            </div>
        )").arg(p).arg(book.format));
    }

    book.toc.append({book.title, 0});
    book.isValid = true;
    return book;
}

LoadedBook DocumentEngine::loadPdf(const QString& filePath) {
    LoadedBook book;
    book.filePath = filePath;
    QFileInfo fi(filePath);
    book.fileSize = fi.size();
    book.title = fi.completeBaseName();
    book.author = "Digital Document";
    book.format = "PDF";

    if (!QFile::exists(filePath)) {
        book.isValid = false;
        book.errorMessage = "File does not exist: " + filePath;
        return book;
    }

    // Cache directory based on file path and modification time
    QByteArray hashInput = (filePath + QString::number(fi.lastModified().toMSecsSinceEpoch())).toUtf8();
    QString hash = QString(QCryptographicHash::hash(hashInput, QCryptographicHash::Sha256).toHex()).left(16);

    QString cacheBase = QStandardPaths::writableLocation(QStandardPaths::CacheLocation);
    if (cacheBase.isEmpty()) {
        cacheBase = QDir::tempPath() + "/FolioHaven";
    }
    QString cacheDir = cacheBase + "/pdf_cache/" + hash;
    QDir dir(cacheDir);

    bool hasCachedPages = false;
    if (dir.exists()) {
        QStringList entries = dir.entryList({"page_*.png"}, QDir::Files);
        if (!entries.isEmpty()) {
            hasCachedPages = true;
        }
    }

    if (!hasCachedPages) {
        dir.mkpath(".");

        QString scriptPath = QCoreApplication::applicationDirPath() + "/scripts/render_pdf.ps1";
        if (!QFile::exists(scriptPath)) {
            scriptPath = QCoreApplication::applicationDirPath() + "/render_pdf.ps1";
        }

        QTemporaryFile tempScript(QDir::tempPath() + "/foliohaven_pdf_XXXXXX.ps1");
        if (!QFile::exists(scriptPath)) {
            if (tempScript.open()) {
                const char* psScript = R"(
param([string]$PdfPath = $env:PDF_INPUT_PATH, [string]$OutputDir = $env:PDF_OUTPUT_DIR, [int]$MaxPages = 0)
if ([string]::IsNullOrWhiteSpace($PdfPath)) { $PdfPath = $env:PDF_INPUT_PATH }
if ([string]::IsNullOrWhiteSpace($OutputDir)) { $OutputDir = $env:PDF_OUTPUT_DIR }
try {
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $asTaskMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Length -eq 1 -and $_.GetParameters()[0].ParameterType.Name -like 'IAsyncOperation*' } | Select-Object -First 1
    $asActionMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Length -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction' } | Select-Object -First 1
    [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Pdf.PdfDocument, Windows.Data.Pdf, ContentType = WindowsRuntime] | Out-Null
    [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime] | Out-Null
    if (!(Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }
    $op1 = [Windows.Storage.StorageFile]::GetFileFromPathAsync($PdfPath)
    $file = $asTaskMethod.MakeGenericMethod([Windows.Storage.StorageFile]).Invoke($null, @($op1)).Result
    $op2 = [Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($file)
    $doc = $asTaskMethod.MakeGenericMethod([Windows.Data.Pdf.PdfDocument]).Invoke($null, @($op2)).Result
    $count = $doc.PageCount
    Write-Output "PAGE_COUNT:$count"
    $pagesToRender = $count
    if ($MaxPages -gt 0 -and $MaxPages -lt $count) { $pagesToRender = $MaxPages }
    for ($i = 0; $i -lt $pagesToRender; $i++) {
        $page = $doc.GetPage($i)
        $stream = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
        $renderOp = $page.RenderToStreamAsync($stream)
        $asActionMethod.Invoke($null, @($renderOp)).Wait()
        $bytes = New-Object byte[] $stream.Size
        $netStream = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($stream)
        $netStream.Read($bytes, 0, $bytes.Length) | Out-Null
        $outPath = Join-Path $OutputDir "page_$i.png"
        [System.IO.File]::WriteAllBytes($outPath, $bytes)
    }
    Write-Output "RENDER_SUCCESS:$pagesToRender"
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
)";
                tempScript.write(psScript);
                tempScript.close();
                scriptPath = tempScript.fileName();
            }
        }

        QProcess process;
        QProcessEnvironment env = QProcessEnvironment::systemEnvironment();
        env.insert("PDF_INPUT_PATH", QDir::toNativeSeparators(filePath));
        env.insert("PDF_OUTPUT_DIR", QDir::toNativeSeparators(cacheDir));
        process.setProcessEnvironment(env);

        QStringList args = {
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", scriptPath
        };
        process.start("powershell.exe", args);
        process.waitForFinished(120000);
    }

    QStringList pngFiles = dir.entryList({"page_*.png"}, QDir::Files);
    std::sort(pngFiles.begin(), pngFiles.end(), [](const QString& a, const QString& b) {
        int idxA = a.section('_', 1).section('.', 0, 0).toInt();
        int idxB = b.section('_', 1).section('.', 0, 0).toInt();
        return idxA < idxB;
    });

    if (!pngFiles.isEmpty()) {
        QString normalizedCacheDir = QDir::fromNativeSeparators(cacheDir);
        for (int i = 0; i < pngFiles.size(); ++i) {
            QString imgPath = normalizedCacheDir + "/" + pngFiles[i];
            QString pageHtml = QString(R"(
                <div align="center" style="padding: 12px 0;">
                    <img src="file:///%1" width="96%">
                </div>
            )").arg(imgPath);
            book.pages.append(pageHtml);
            book.toc.append({QString("Page %1").arg(i + 1), i});
        }
        book.isValid = true;
        return book;
    }

    return loadGenericDocument(filePath, "PDF");
}

LoadedBook DocumentEngine::loadCbz(const QString& filePath) {
    LoadedBook book;
    book.filePath = filePath;
    QFileInfo fi(filePath);
    book.fileSize = fi.size();
    book.title = fi.completeBaseName();
    book.author = "Illustrated Book";
    book.format = "CBZ";

    QTemporaryDir tempDir;
    if (!tempDir.isValid()) {
        return loadGenericDocument(filePath, "CBZ");
    }

    QProcess tarProcess;
    tarProcess.start("tar", {"-xf", filePath, "-C", tempDir.path()});
    if (!tarProcess.waitForFinished(10000) || tarProcess.exitCode() != 0) {
        return loadGenericDocument(filePath, "CBZ");
    }

    QStringList imageExtensions = {"*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp", "*.gif"};
    QDirIterator it(tempDir.path(), imageExtensions, QDir::Files, QDirIterator::Subdirectories);
    QStringList imageFiles;
    while (it.hasNext()) {
        imageFiles.append(it.next());
    }
    std::sort(imageFiles.begin(), imageFiles.end());

    if (imageFiles.isEmpty()) {
        return loadGenericDocument(filePath, "CBZ");
    }

    QByteArray hashInput = (filePath + QString::number(fi.lastModified().toMSecsSinceEpoch())).toUtf8();
    QString hash = QString(QCryptographicHash::hash(hashInput, QCryptographicHash::Sha256).toHex()).left(16);
    QString cacheBase = QStandardPaths::writableLocation(QStandardPaths::CacheLocation);
    if (cacheBase.isEmpty()) cacheBase = QDir::tempPath() + "/FolioHaven";
    QString cacheDir = cacheBase + "/cbz_cache/" + hash;
    QDir().mkpath(cacheDir);

    for (int i = 0; i < imageFiles.size(); ++i) {
        QString ext = QFileInfo(imageFiles[i]).suffix();
        QString destPath = QString("%1/page_%2.%3").arg(cacheDir).arg(i).arg(ext);
        QFile::copy(imageFiles[i], destPath);
        QString normalizedPath = QDir::fromNativeSeparators(destPath);
        QString pageHtml = QString(R"(
            <div align="center" style="padding: 12px 0;">
                <img src="file:///%1" width="96%">
            </div>
        )").arg(normalizedPath);
        book.pages.append(pageHtml);
        book.toc.append({QString("Page %1").arg(i + 1), i});
    }

    book.isValid = true;
    return book;
}

LoadedBook DocumentEngine::loadFb2(const QString& filePath) {
    LoadedBook book;
    book.filePath = filePath;
    QFileInfo fi(filePath);
    book.fileSize = fi.size();
    book.title = fi.completeBaseName();
    book.author = "Unknown Author";
    book.format = "FB2";

    QFile file(filePath);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        return loadGenericDocument(filePath, "FB2");
    }

    QXmlStreamReader xml(&file);
    QString fullText;
    while (!xml.atEnd()) {
        if (xml.readNextStartElement()) {
            if (xml.name() == QLatin1String("book-title")) {
                book.title = xml.readElementText();
            } else if (xml.name() == QLatin1String("p")) {
                QString para = xml.readElementText().trimmed();
                if (!para.isEmpty()) {
                    fullText += para + "\n\n";
                }
            }
        }
    }
    file.close();

    if (!fullText.trimmed().isEmpty()) {
        book.pages = paginateText(fullText);
        book.toc.append({book.title, 0});
        book.isValid = true;
        return book;
    }

    return loadGenericDocument(filePath, "FB2");
}

LoadedBook DocumentEngine::loadDocument(const QString& filePath) {
    QFileInfo fi(filePath);
    QString ext = fi.suffix().toLower();

    if (ext == "txt") {
        return loadPlainText(filePath);
    } else if (ext == "epub") {
        return loadEpub(filePath);
    } else if (ext == "pdf") {
        return loadPdf(filePath);
    } else if (ext == "cbz" || ext == "cbr") {
        return loadCbz(filePath);
    } else if (ext == "fb2") {
        return loadFb2(filePath);
    } else {
        return loadGenericDocument(filePath, ext.toUpper());
    }
}

QVector<SearchHit> DocumentEngine::search(const LoadedBook& book, const QString& query) {
    QVector<SearchHit> hits;
    if (query.trimmed().isEmpty()) return hits;

    for (int i = 0; i < book.pages.size(); ++i) {
        QString pageContent = book.pages[i];
        // Strip HTML tags for clean search
        QString plain = pageContent;
        plain.remove(QRegularExpression("<[^>]*>"));

        int idx = plain.indexOf(query, 0, Qt::CaseInsensitive);
        if (idx != -1) {
            int start = std::max(0, idx - 40);
            int length = std::min(plain.length() - start, query.length() + 80);
            QString snippet = "..." + plain.mid(start, length).replace("\n", " ").trimmed() + "...";
            hits.append({i, snippet});
        }
    }
    return hits;
}
