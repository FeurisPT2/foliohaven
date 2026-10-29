#include <QApplication>
#include <QIcon>
#include <QFileInfo>
#include <QDir>
#include <QDebug>

#include "../storage/DatabaseManager.h"
#include "../ui/ReaderWindow.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    app.setApplicationName("FolioHaven");
    app.setApplicationDisplayName("FolioHaven");
    app.setOrganizationName("FolioHaven Team");
    app.setApplicationVersion("1.0.1");

    // Initialize embedded SQLite database
    if (!DatabaseManager::instance().init()) {
        qCritical() << "Fatal: Could not initialize FolioHaven local database.";
    }

    ReaderWindow window;

    // Load App Icon if available
    QString iconPath = QDir::current().filePath("app/icon.ico");
    if (!QFile::exists(iconPath)) {
        iconPath = QDir::current().filePath("app/icon.png");
    }
    if (QFile::exists(iconPath)) {
        window.setWindowIcon(QIcon(iconPath));
        app.setWindowIcon(QIcon(iconPath));
    }

    window.show();

    // Check if initial book passed via CLI args (Unicode safe)
    const QStringList cmdArgs = QCoreApplication::arguments();
    if (cmdArgs.size() > 1) {
        QString initialFile = cmdArgs.at(1);
        if (QFile::exists(initialFile)) {
            window.openBookFile(initialFile);
        }
    }

    return app.exec();
}
