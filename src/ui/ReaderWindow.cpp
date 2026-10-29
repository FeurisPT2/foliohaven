#include "ReaderWindow.h"

#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QFileDialog>
#include <QMessageBox>
#include <QHeaderView>
#include <QDragEnterEvent>
#include <QDropEvent>
#include <QMimeData>
#include <QFileInfo>
#include <QScrollBar>
#include <QSplitter>
#include <QPainter>
#include <QFile>
#include <QTextStream>
#include <QDesktopServices>
#include <QUrl>
#include <QApplication>
#include <QSvgRenderer>
#include <QPixmap>
#include <QIcon>
#include <QToolTip>
#include <QDialog>
#include <QTabWidget>
#include <QComboBox>
#include <QSpinBox>
#include <QFormLayout>
#include <QDirIterator>
#include <QStandardPaths>
#include <QMenu>
#include <QAction>
#include <QInputDialog>

#ifdef Q_OS_WIN
#include <windows.h>
#include <initguid.h>
#include <sapi.h>
static ISpVoice *g_pVoice = nullptr;
#endif

static QIcon createSvgIcon(const QString& svgPathData, int size = 16, const QString& strokeColor = "#d6d3d1", double strokeWidth = 2.0, bool fill = false) {
    QString svgXml = QString(R"(
        <svg xmlns="http://www.w3.org/2000/svg" width="%1" height="%1" viewBox="0 0 24 24" 
             fill="%2" stroke="%3" stroke-width="%4" stroke-linecap="round" stroke-linejoin="round">
            %5
        </svg>
    )").arg(size).arg(fill ? strokeColor : "none").arg(strokeColor).arg(strokeWidth).arg(svgPathData);

    QByteArray data = svgXml.toUtf8();
    QSvgRenderer renderer(data);
    QPixmap pixmap(size * 2, size * 2);
    pixmap.fill(Qt::transparent);
    QPainter painter(&pixmap);
    painter.setRenderHint(QPainter::Antialiasing);
    renderer.render(&painter);
    return QIcon(pixmap);
}

static QIcon createColorSwatchIcon(const QString& fillColor, const QString& borderColor, int size = 14) {
    QPixmap pixmap(size * 2, size * 2);
    pixmap.fill(Qt::transparent);
    QPainter painter(&pixmap);
    painter.setRenderHint(QPainter::Antialiasing);

    QPen pen(QColor(borderColor), 2.0);
    painter.setPen(pen);
    painter.setBrush(QBrush(QColor(fillColor)));
    painter.drawEllipse(2, 2, (size * 2) - 4, (size * 2) - 4);

    return QIcon(pixmap);
}

static QPixmap createBrandLogoPixmap(int size = 32) {
    const QString svgXml = QString(R"(
        <svg xmlns="http://www.w3.org/2000/svg" width="%1" height="%1" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="7" fill="#c2410c"/>
            <path d="M8 9C8 7.89543 8.89543 7 10 7H22C23.1046 7 24 7.89543 24 9V24H10C8.89543 24 8 23.1046 8 22.1V9Z" fill="#ffffff" fill-opacity="0.25"/>
            <path d="M10 9H22V22H11C9.89543 22 9 21.1046 9 20V10C9 9.44772 9.44772 9 10 9Z" fill="#ffffff"/>
            <path d="M13 12H19M13 15.5H19M13 19H17" stroke="#c2410c" stroke-width="1.75" stroke-linecap="round"/>
        </svg>
    )").arg(size);

    QSvgRenderer renderer(svgXml.toUtf8());
    QPixmap pixmap(size * 2, size * 2);
    pixmap.fill(Qt::transparent);
    pixmap.setDevicePixelRatio(2.0);
    QPainter painter(&pixmap);
    painter.setRenderHint(QPainter::Antialiasing);
    renderer.render(&painter);
    return pixmap;
}

static QPixmap createEmptyStateIllustration() {
    QPixmap pix(220, 130);
    pix.fill(Qt::transparent);
    QPainter p(&pix);
    p.setRenderHint(QPainter::Antialiasing);

    // Shelf base plank
    p.setBrush(QColor("#3d3835"));
    p.setPen(Qt::NoPen);
    p.drawRoundedRect(20, 105, 180, 6, 3, 3);

    // Shelf support brackets
    p.setPen(QPen(QColor("#57534e"), 1.5));
    p.drawLine(40, 111, 40, 120);
    p.drawLine(180, 111, 180, 120);

    // Left bookend
    p.drawLine(28, 105, 28, 75);
    p.drawLine(28, 75, 34, 75);

    // Right bookend
    p.drawLine(192, 105, 192, 75);
    p.drawLine(192, 75, 186, 75);

    // Ghost Book 1 (Left tall)
    p.setBrush(QColor(41, 37, 36, 140));
    p.setPen(QPen(QColor("#78716c"), 1.2, Qt::DashLine));
    p.drawRoundedRect(42, 38, 20, 67, 2, 2);

    // Ghost Book 2 (Medium)
    p.drawRoundedRect(66, 48, 18, 57, 2, 2);

    // Ghost Book 3 (Center feature with bookmark)
    p.setBrush(QColor(68, 64, 60, 180));
    p.setPen(QPen(QColor("#a8a29e"), 1.5));
    p.drawRoundedRect(88, 28, 28, 77, 3, 3);

    // Terracotta ribbon bookmark on Center Book
    p.setBrush(QColor("#c2410c"));
    p.setPen(Qt::NoPen);
    QPolygon ribbon;
    ribbon << QPoint(100, 28) << QPoint(100, 48) << QPoint(104, 44) << QPoint(108, 48) << QPoint(108, 28);
    p.drawPolygon(ribbon);

    // Ghost Book 4 (Compact)
    p.setBrush(QColor(41, 37, 36, 140));
    p.setPen(QPen(QColor("#78716c"), 1.2, Qt::DashLine));
    p.drawRoundedRect(120, 52, 18, 53, 2, 2);

    // Ghost Book 5 (Right medium tall)
    p.drawRoundedRect(142, 42, 22, 63, 2, 2);

    return pix;
}

static QString toolbarBtnStyle(bool isActive = false) {
    if (isActive) {
        return R"(
            QPushButton {
                background-color: #382a20;
                border: 1.5px solid #ea580c;
                border-radius: 6px;
                padding: 5px 12px;
                color: #ffedd5;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #443224;
            }
        )";
    }
    return R"(
        QPushButton {
            background-color: #24201e;
            border: 1px solid #3d3835;
            border-radius: 6px;
            padding: 5px 12px;
            color: #d6d3d1;
            font-size: 12px;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #332d29;
            border-color: #57534e;
            color: #ffffff;
        }
        QPushButton:pressed {
            background-color: #1a1716;
        }
    )";
}

ReaderWindow::ReaderWindow(QWidget *parent)
    : QMainWindow(parent) {
    setWindowTitle("FolioHaven — Native Desktop Ebook Reader");
    setWindowIcon(QIcon(createBrandLogoPixmap(64)));
    resize(1280, 850);
    setMinimumSize(960, 640);
    setAcceptDrops(true);

#ifdef Q_OS_WIN
    CoInitialize(nullptr);
    CoCreateInstance(CLSID_SpVoice, nullptr, CLSCTX_ALL, IID_ISpVoice, (void **)&g_pVoice);
#endif

    setupUi();
    refreshLibrary();
    applyTheme(ReaderTheme::Sepia);
}

ReaderWindow::~ReaderWindow() {
#ifdef Q_OS_WIN
    if (g_pVoice) {
        g_pVoice->Release();
        g_pVoice = nullptr;
    }
    CoUninitialize();
#endif
}

void ReaderWindow::setupUi() {
    m_stackWidget = new QStackedWidget(this);
    setCentralWidget(m_stackWidget);

    setupLibraryView();
    setupReaderView();
    setupDrawers();

    m_stackWidget->addWidget(m_libraryWidget);    // 0: Library
    m_stackWidget->addWidget(m_readerViewWidget); // 1: Reader

    // Application Dark Theme Stylesheet
    setStyleSheet(R"(
        QMainWindow {
            background-color: #1c1917;
            color: #f5f5f4;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        QWidget {
            color: #f5f5f4;
        }
        QLineEdit {
            background-color: #24201e;
            border: 1px solid #3d3835;
            border-radius: 6px;
            padding: 8px 12px;
            color: #f5f5f4;
            font-size: 13px;
        }
        QLineEdit:focus {
            border: 1px solid #ea580c;
        }
        QPushButton {
            background-color: #24201e;
            border: 1px solid #3d3835;
            border-radius: 6px;
            padding: 6px 12px;
            color: #f5f5f4;
            font-size: 12px;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #332d29;
            border-color: #57534e;
        }
        QPushButton:pressed {
            background-color: #1a1716;
        }
        QListWidget, QTableWidget {
            background-color: #1c1917;
            border: none;
            outline: none;
        }
        QListWidget::item {
            padding: 8px 12px;
            border-radius: 6px;
            margin: 2px 4px;
        }
        QListWidget::item:selected {
            background-color: #c2410c;
            color: #ffffff;
        }
        QListWidget::item:hover:!selected {
            background-color: #292524;
        }
        QHeaderView::section {
            background-color: #24201e;
            color: #a8a29e;
            padding: 8px;
            border: none;
            border-bottom: 1px solid #3d3835;
            font-weight: 600;
            font-size: 12px;
        }
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #292524;
        }
        QTableWidget::item:selected {
            background-color: #3b3532;
            color: #f5f5f4;
        }
        QSlider::groove:horizontal {
            border: none;
            height: 4px;
            background: #44403c;
            border-radius: 2px;
        }
        QSlider::sub-page:horizontal {
            background: #c2410c;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #f5f5f4;
            border: 1px solid #c2410c;
            width: 14px;
            margin-top: -5px;
            margin-bottom: -5px;
            border-radius: 7px;
        }
        QDockWidget {
            color: #f5f5f4;
        }
        QDockWidget::title {
            background: #24201e;
            padding: 8px;
            font-weight: 600;
            border-bottom: 1px solid #3d3835;
        }
    )");
}

void ReaderWindow::setupLibraryView() {
    m_libraryWidget = new QWidget(this);
    QHBoxLayout *mainLayout = new QHBoxLayout(m_libraryWidget);
    mainLayout->setContentsMargins(0, 0, 0, 0);
    mainLayout->setSpacing(0);

    // Left Sidebar
    QWidget *sidebarWidget = new QWidget(m_libraryWidget);
    sidebarWidget->setFixedWidth(240);
    sidebarWidget->setStyleSheet("background-color: #171514; border-right: 1px solid #292524;");
    QVBoxLayout *sideLayout = new QVBoxLayout(sidebarWidget);
    sideLayout->setContentsMargins(16, 20, 16, 20);
    sideLayout->setSpacing(12);

    // Brand Identity Header (Logo Icon + Title + Subtitle at top left)
    QWidget *brandHeader = new QWidget(sidebarWidget);
    QHBoxLayout *brandLayout = new QHBoxLayout(brandHeader);
    brandLayout->setContentsMargins(0, 0, 0, 8);
    brandLayout->setSpacing(10);

    QLabel *logoIconLabel = new QLabel(brandHeader);
    logoIconLabel->setFixedSize(32, 32);
    logoIconLabel->setPixmap(createBrandLogoPixmap(32));
    brandLayout->addWidget(logoIconLabel);

    QVBoxLayout *brandTextLayout = new QVBoxLayout();
    brandTextLayout->setContentsMargins(0, 0, 0, 0);
    brandTextLayout->setSpacing(2);

    QLabel *logoLabel = new QLabel("FolioHaven", brandHeader);
    logoLabel->setStyleSheet("font-size: 18px; font-weight: 700; color: #f5f5f4; letter-spacing: -0.3px;");
    brandTextLayout->addWidget(logoLabel);

    QLabel *subLogo = new QLabel("Desktop Ebook Library", brandHeader);
    subLogo->setStyleSheet("font-size: 11px; color: #a8a29e;");
    brandTextLayout->addWidget(subLogo);

    brandLayout->addLayout(brandTextLayout);
    brandLayout->addStretch();
    sideLayout->addWidget(brandHeader);

    m_addBookBtn = new QPushButton("Add Books...", sidebarWidget);
    m_addBookBtn->setIcon(createSvgIcon("M12 5v14 M5 12h14", 16, "#ffffff", 2.5));
    m_addBookBtn->setCursor(Qt::PointingHandCursor);
    m_addBookBtn->setStyleSheet(R"(
        QPushButton {
            background-color: #c2410c;
            color: #ffffff;
            font-weight: 600;
            font-size: 13px;
            border: 1px solid #ea580c;
            padding: 10px 16px;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #ea580c;
            border-color: #f97316;
        }
        QPushButton:pressed {
            background-color: #9a3412;
        }
    )");
    connect(m_addBookBtn, &QPushButton::clicked, this, &ReaderWindow::onAddBookClicked);
    sideLayout->addWidget(m_addBookBtn);

    m_sidebarList = new QListWidget(sidebarWidget);
    m_sidebarList->setStyleSheet(R"(
        QListWidget {
            background: transparent;
            border: none;
            outline: none;
        }
        QListWidget::item {
            padding: 9px 12px;
            border-radius: 6px;
            margin: 2px 0px;
            color: #d6d3d1;
            font-size: 13px;
            font-weight: 500;
        }
        QListWidget::item:hover:!selected {
            background-color: #292524;
            color: #ffffff;
        }
        QListWidget::item:selected {
            background-color: #c2410c;
            color: #ffffff;
            font-weight: 600;
        }
    )");

    auto addCatItem = [this](const QString& title, const QString& svgPath) {
        QListWidgetItem *it = new QListWidgetItem(m_sidebarList);
        it->setText(title);
        it->setData(Qt::UserRole, title);
        it->setIcon(createSvgIcon(svgPath, 16, "#d6d3d1"));
    };

    addCatItem("All Books", "M4 19.5A2.5 2.5 0 0 1 6.5 17H20 M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z");
    addCatItem("Favorites", "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z");
    addCatItem("Currently Reading", "M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z");
    addCatItem("Completed", "M22 11.08V12a10 10 0 1 1-5.93-9.14 M22 4L12 14.01l-3-3");
    addCatItem("EPUB Documents", "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6");
    addCatItem("PDF Documents", "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M10 12h4 M10 16h4");
    addCatItem("MOBI Ebooks", "M4 6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6z M9 10h6 M9 14h6");
    addCatItem("TXT Files", "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M10 13h4");

    m_sidebarList->setCurrentRow(0);
    connect(m_sidebarList, &QListWidget::itemClicked, this, &ReaderWindow::onCategorySelected);
    sideLayout->addWidget(m_sidebarList);

    m_addCategoryBtn = new QPushButton("+ Add Category", sidebarWidget);
    m_addCategoryBtn->setStyleSheet(R"(
        QPushButton {
            background-color: transparent;
            border: 1px dashed #44403c;
            border-radius: 6px;
            color: #a8a29e;
            font-size: 12px;
            font-weight: 500;
            padding: 7px 12px;
            text-align: left;
            margin-top: 4px;
        }
        QPushButton:hover {
            background-color: #292524;
            border-color: #78716c;
            color: #f5f5f4;
        }
    )");
    m_addCategoryBtn->setCursor(Qt::PointingHandCursor);
    connect(m_addCategoryBtn, &QPushButton::clicked, this, &ReaderWindow::onAddCategoryClicked);
    sideLayout->addWidget(m_addCategoryBtn);

    sideLayout->addStretch();

    QLabel *dropTip = new QLabel("Tip: Drag & drop any book file into the app to import.", sidebarWidget);
    dropTip->setWordWrap(true);
    dropTip->setStyleSheet("font-size: 11px; color: #78716c; margin-bottom: 6px;");
    sideLayout->addWidget(dropTip);

    m_settingsBtn = new QPushButton("Settings", sidebarWidget);
    m_settingsBtn->setIcon(createSvgIcon("M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z", 14, "#d6d3d1"));
    m_settingsBtn->setCursor(Qt::PointingHandCursor);
    m_settingsBtn->setToolTip("Preferences & Settings");
    m_settingsBtn->setStyleSheet(toolbarBtnStyle(false));
    connect(m_settingsBtn, &QPushButton::clicked, this, &ReaderWindow::onOpenSettingsDialog);
    sideLayout->addWidget(m_settingsBtn);

    mainLayout->addWidget(sidebarWidget);

    // Right Content Area
    QWidget *contentArea = new QWidget(m_libraryWidget);
    QVBoxLayout *contentLayout = new QVBoxLayout(contentArea);
    contentLayout->setContentsMargins(24, 20, 24, 20);
    contentLayout->setSpacing(16);

    // Top Header Toolbar
    QHBoxLayout *topBar = new QHBoxLayout();
    m_searchLibraryEdit = new QLineEdit(contentArea);
    m_searchLibraryEdit->setPlaceholderText("Search books by title, author...");
    m_searchLibraryEdit->setClearButtonEnabled(true);
    m_searchLibraryEdit->setFixedWidth(320);
    connect(m_searchLibraryEdit, &QLineEdit::textChanged, this, &ReaderWindow::onSearchLibraryChanged);
    topBar->addWidget(m_searchLibraryEdit);

    topBar->addStretch();

    m_viewGridBtn = new QPushButton("Grid", contentArea);
    m_viewGridBtn->setIcon(createSvgIcon("M3 3h7v7H3z M14 3h7v7h-7z M14 14h7v7h-7z M3 14h7v7H3z", 14, "#d6d3d1"));
    m_viewGridBtn->setCursor(Qt::PointingHandCursor);

    m_viewTableBtn = new QPushButton("Table", contentArea);
    m_viewTableBtn->setIcon(createSvgIcon("M8 6h13 M8 12h13 M8 18h13 M3 6h.01 M3 12h.01 M3 18h.01", 14, "#d6d3d1"));
    m_viewTableBtn->setCursor(Qt::PointingHandCursor);

    connect(m_viewGridBtn, &QPushButton::clicked, [this]() { onViewModeToggled(0); });
    connect(m_viewTableBtn, &QPushButton::clicked, [this]() { onViewModeToggled(1); });
    topBar->addWidget(m_viewGridBtn);
    topBar->addWidget(m_viewTableBtn);
    updateViewModeButtons(0);

    contentLayout->addLayout(topBar);

    // Empty State Widget (Archival Bookshelf Plank)
    m_emptyStateWidget = new QWidget(contentArea);
    QVBoxLayout *emptyLayout = new QVBoxLayout(m_emptyStateWidget);
    emptyLayout->setAlignment(Qt::AlignCenter);
    emptyLayout->setSpacing(14);

    QLabel *emptyIcon = new QLabel(m_emptyStateWidget);
    emptyIcon->setPixmap(createEmptyStateIllustration());
    emptyIcon->setAlignment(Qt::AlignCenter);
    emptyLayout->addWidget(emptyIcon);

    QLabel *emptyTitle = new QLabel("Your Library is Waiting", m_emptyStateWidget);
    emptyTitle->setStyleSheet("font-size: 22px; font-weight: 700; color: #f5f5f4;");
    emptyTitle->setAlignment(Qt::AlignCenter);
    emptyLayout->addWidget(emptyTitle);

    QLabel *emptySubtitle = new QLabel("A calm place for your books — no nags, no timers, no subscriptions. Just pure reading.", m_emptyStateWidget);
    emptySubtitle->setStyleSheet("font-size: 14px; color: #a8a29e;");
    emptySubtitle->setWordWrap(true);
    emptySubtitle->setAlignment(Qt::AlignCenter);
    emptyLayout->addWidget(emptySubtitle);

    QPushButton *emptyAddBtn = new QPushButton("+ Add Your First Book", m_emptyStateWidget);
    emptyAddBtn->setCursor(Qt::PointingHandCursor);
    emptyAddBtn->setStyleSheet(R"(
        QPushButton {
            background-color: #c2410c;
            color: #ffffff;
            border: 1px solid #ea580c;
            border-radius: 6px;
            padding: 10px 24px;
            font-size: 14px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #ea580c;
        }
    )");
    connect(emptyAddBtn, &QPushButton::clicked, this, &ReaderWindow::onAddBookClicked);
    emptyLayout->addWidget(emptyAddBtn, 0, Qt::AlignCenter);

    QLabel *emptyHint = new QLabel("Supports EPUB, PDF, MOBI, FB2, CBZ, and TXT • Drop files anywhere to import", m_emptyStateWidget);
    emptyHint->setStyleSheet("font-size: 12px; color: #78716c; margin-top: 6px;");
    emptyHint->setAlignment(Qt::AlignCenter);
    emptyLayout->addWidget(emptyHint);

    contentLayout->addWidget(m_emptyStateWidget);

    // View Modes Stack
    m_viewModeStack = new QStackedWidget(contentArea);

    // Mode 0: Grid List
    m_bookGridList = new QListWidget(m_viewModeStack);
    m_bookGridList->setViewMode(QListView::IconMode);
    m_bookGridList->setIconSize(QSize(140, 200));
    m_bookGridList->setGridSize(QSize(170, 270));
    m_bookGridList->setSpacing(16);
    m_bookGridList->setResizeMode(QListView::Adjust);
    m_bookGridList->setWordWrap(true);
    m_bookGridList->setContextMenuPolicy(Qt::CustomContextMenu);
    connect(m_bookGridList, &QListWidget::itemDoubleClicked, this, &ReaderWindow::onBookDoubleClicked);
    connect(m_bookGridList, &QListWidget::customContextMenuRequested, this, &ReaderWindow::onBookGridContextMenu);
    m_viewModeStack->addWidget(m_bookGridList);

    // Mode 1: Table List
    m_bookTableWidget = new QTableWidget(m_viewModeStack);
    m_bookTableWidget->setColumnCount(6);
    m_bookTableWidget->setHorizontalHeaderLabels({"Title", "Author", "Format", "Progress", "Size", "Date Added"});
    m_bookTableWidget->horizontalHeader()->setStretchLastSection(true);
    m_bookTableWidget->horizontalHeader()->setSectionResizeMode(0, QHeaderView::Stretch);
    m_bookTableWidget->setSelectionBehavior(QAbstractItemView::SelectRows);
    m_bookTableWidget->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_bookTableWidget->setContextMenuPolicy(Qt::CustomContextMenu);
    connect(m_bookTableWidget, &QTableWidget::cellDoubleClicked, this, &ReaderWindow::onBookTableRowDoubleClicked);
    connect(m_bookTableWidget, &QTableWidget::customContextMenuRequested, this, &ReaderWindow::onBookTableContextMenu);
    m_viewModeStack->addWidget(m_bookTableWidget);

    contentLayout->addWidget(m_viewModeStack);

    // Bottom status bar in library
    m_statusLabel = new QLabel("0 books loaded", contentArea);
    m_statusLabel->setStyleSheet("color: #78716c; font-size: 12px;");
    contentLayout->addWidget(m_statusLabel);

    mainLayout->addWidget(contentArea);
}

void ReaderWindow::setupReaderView() {
    m_readerViewWidget = new QWidget(this);
    QVBoxLayout *readerLayout = new QVBoxLayout(m_readerViewWidget);
    readerLayout->setContentsMargins(0, 0, 0, 0);
    readerLayout->setSpacing(0);

    // Reader Top Navigation Bar
    QWidget *topNav = new QWidget(m_readerViewWidget);
    topNav->setStyleSheet("background-color: #171514; border-bottom: 1px solid #292524; padding: 6px 16px;");
    QHBoxLayout *navLayout = new QHBoxLayout(topNav);
    navLayout->setContentsMargins(0, 0, 0, 0);
    navLayout->setSpacing(8);

    // --- Cluster 1 (Left): Navigation & Book Identity ---
    m_backBtn = new QPushButton("Library", topNav);
    m_backBtn->setIcon(createSvgIcon("M19 12H5 M12 19l-7-7 7-7", 14, "#d6d3d1"));
    m_backBtn->setToolTip("Return to Library (Esc)");
    m_backBtn->setCursor(Qt::PointingHandCursor);
    m_backBtn->setStyleSheet(toolbarBtnStyle(false));
    connect(m_backBtn, &QPushButton::clicked, this, &ReaderWindow::onCloseReader);
    navLayout->addWidget(m_backBtn);

    QFrame *sepLeft = new QFrame(topNav);
    sepLeft->setFrameShape(QFrame::VLine);
    sepLeft->setStyleSheet("color: #383330;");
    navLayout->addWidget(sepLeft);

    m_readerTitleLabel = new QLabel("Book Title", topNav);
    m_readerTitleLabel->setMaximumWidth(260);
    m_readerTitleLabel->setStyleSheet("font-weight: 600; font-size: 13px; color: #f5f5f4;");
    navLayout->addWidget(m_readerTitleLabel);

    m_readerFormatBadge = new QLabel("PDF", topNav);
    m_readerFormatBadge->setStyleSheet(R"(
        background-color: rgba(194, 65, 12, 0.2);
        color: #fb923c;
        border: 1px solid rgba(234, 88, 12, 0.4);
        border-radius: 4px;
        padding: 2px 7px;
        font-size: 11px;
        font-weight: 700;
    )");
    navLayout->addWidget(m_readerFormatBadge);

    navLayout->addStretch(1);

    // --- Cluster 2 (Center): Reading Canvas Display Controls ---
    m_themeDayBtn = new QPushButton("Day", topNav);
    m_themeDayBtn->setIcon(createColorSwatchIcon("#fafaf9", "#a8a29e"));
    m_themeDayBtn->setCursor(Qt::PointingHandCursor);
    connect(m_themeDayBtn, &QPushButton::clicked, [this]() { onThemeChanged(ReaderTheme::Day); });

    m_themeSepiaBtn = new QPushButton("Sepia", topNav);
    m_themeSepiaBtn->setIcon(createColorSwatchIcon("#f5ebd7", "#b49b78"));
    m_themeSepiaBtn->setCursor(Qt::PointingHandCursor);
    connect(m_themeSepiaBtn, &QPushButton::clicked, [this]() { onThemeChanged(ReaderTheme::Sepia); });

    m_themeNightBtn = new QPushButton("Night", topNav);
    m_themeNightBtn->setIcon(createColorSwatchIcon("#121212", "#52525b"));
    m_themeNightBtn->setCursor(Qt::PointingHandCursor);
    connect(m_themeNightBtn, &QPushButton::clicked, [this]() { onThemeChanged(ReaderTheme::Night); });

    m_themeDarkSepiaBtn = new QPushButton("Dark Sepia", topNav);
    m_themeDarkSepiaBtn->setIcon(createColorSwatchIcon("#251d16", "#634832"));
    m_themeDarkSepiaBtn->setCursor(Qt::PointingHandCursor);
    connect(m_themeDarkSepiaBtn, &QPushButton::clicked, [this]() { onThemeChanged(ReaderTheme::DarkSepia); });

    navLayout->addWidget(m_themeDayBtn);
    navLayout->addWidget(m_themeSepiaBtn);
    navLayout->addWidget(m_themeNightBtn);
    navLayout->addWidget(m_themeDarkSepiaBtn);
    updateThemeButtons();

    QFrame *sepCenter = new QFrame(topNav);
    sepCenter->setFrameShape(QFrame::VLine);
    sepCenter->setStyleSheet("color: #383330;");
    navLayout->addWidget(sepCenter);

    m_twoPagesBtn = new QPushButton(topNav);
    m_twoPagesBtn->setCursor(Qt::PointingHandCursor);
    connect(m_twoPagesBtn, &QPushButton::clicked, this, &ReaderWindow::onToggleTwoPages);
    updateLayoutButton();
    navLayout->addWidget(m_twoPagesBtn);

    m_zoomOutBtn = new QPushButton("A-", topNav);
    m_zoomOutBtn->setCursor(Qt::PointingHandCursor);
    m_zoomOutBtn->setToolTip("Decrease Font Size");
    connect(m_zoomOutBtn, &QPushButton::clicked, this, &ReaderWindow::onZoomOut);

    m_zoomInBtn = new QPushButton("A+", topNav);
    m_zoomInBtn->setCursor(Qt::PointingHandCursor);
    m_zoomInBtn->setToolTip("Increase Font Size");
    connect(m_zoomInBtn, &QPushButton::clicked, this, &ReaderWindow::onZoomIn);

    m_zoomOutBtn->setStyleSheet(R"(
        QPushButton {
            background-color: #24201e;
            border: 1px solid #3d3835;
            border-right: none;
            border-top-left-radius: 6px;
            border-bottom-left-radius: 6px;
            border-top-right-radius: 0px;
            border-bottom-right-radius: 0px;
            padding: 5px 10px;
            color: #d6d3d1;
            font-size: 12px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #332d29;
            color: #ffffff;
        }
        QPushButton:pressed {
            background-color: #1a1716;
        }
    )");

    m_zoomInBtn->setStyleSheet(R"(
        QPushButton {
            background-color: #24201e;
            border: 1px solid #3d3835;
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
            padding: 5px 10px;
            color: #d6d3d1;
            font-size: 12px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #332d29;
            color: #ffffff;
        }
        QPushButton:pressed {
            background-color: #1a1716;
        }
    )");

    navLayout->addWidget(m_zoomOutBtn);
    navLayout->addWidget(m_zoomInBtn);

    navLayout->addStretch(1);

    // --- Cluster 3 (Right): Research, Study Tools & Settings ---
    m_tocBtn = new QPushButton("Contents", topNav);
    m_tocBtn->setIcon(createSvgIcon("M4 6h16 M4 12h16 M4 18h10", 14, "#d6d3d1"));
    m_tocBtn->setCursor(Qt::PointingHandCursor);
    m_tocBtn->setToolTip("Table of Contents (Chapters)");
    m_tocBtn->setStyleSheet(toolbarBtnStyle(false));
    connect(m_tocBtn, &QPushButton::clicked, this, &ReaderWindow::onToggleTocDrawer);
    navLayout->addWidget(m_tocBtn);

    m_searchBtn = new QPushButton("Search", topNav);
    m_searchBtn->setIcon(createSvgIcon("M21 21l-4.35-4.35 M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16z", 14, "#d6d3d1"));
    m_searchBtn->setCursor(Qt::PointingHandCursor);
    m_searchBtn->setStyleSheet(toolbarBtnStyle(false));
    connect(m_searchBtn, &QPushButton::clicked, this, &ReaderWindow::onToggleSearchDrawer);
    navLayout->addWidget(m_searchBtn);

    m_bookmarkBtn = new QPushButton("Bookmark", topNav);
    m_bookmarkBtn->setIcon(createSvgIcon("M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z", 14, "#d6d3d1"));
    m_bookmarkBtn->setCursor(Qt::PointingHandCursor);
    m_bookmarkBtn->setStyleSheet(toolbarBtnStyle(false));
    connect(m_bookmarkBtn, &QPushButton::clicked, this, &ReaderWindow::onAddBookmark);
    navLayout->addWidget(m_bookmarkBtn);

    m_notesBtn = new QPushButton("Notes", topNav);
    m_notesBtn->setIcon(createSvgIcon("M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7 M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z", 14, "#d6d3d1"));
    m_notesBtn->setCursor(Qt::PointingHandCursor);
    m_notesBtn->setToolTip("Bookmarks & Annotations");
    m_notesBtn->setStyleSheet(toolbarBtnStyle(false));
    connect(m_notesBtn, &QPushButton::clicked, this, &ReaderWindow::onToggleNotesDrawer);
    navLayout->addWidget(m_notesBtn);

    m_speakBtn = new QPushButton("Read Aloud", topNav);
    m_speakBtn->setIcon(createSvgIcon("M11 5L6 9H2v6h4l5 4V5z M19.07 4.93a10 10 0 0 1 0 14.14 M15.54 8.46a5 5 0 0 1 0 7.07", 14, "#d6d3d1"));
    m_speakBtn->setCursor(Qt::PointingHandCursor);
    m_speakBtn->setStyleSheet(toolbarBtnStyle(false));
    connect(m_speakBtn, &QPushButton::clicked, this, &ReaderWindow::onToggleReadAloud);
    navLayout->addWidget(m_speakBtn);

    m_fsBtn = new QPushButton("Fullscreen", topNav);
    m_fsBtn->setIcon(createSvgIcon("M8 3H5a2 2 0 0 0-2 2v3 M16 3h3a2 2 0 0 1 2 2v3 M8 21H5a2 2 0 0 1-2-2v-3 M16 21h3a2 2 0 0 0 2-2v-3", 14, "#d6d3d1"));
    m_fsBtn->setToolTip("Toggle Fullscreen (F)");
    m_fsBtn->setCursor(Qt::PointingHandCursor);
    m_fsBtn->setStyleSheet(toolbarBtnStyle(false));
    connect(m_fsBtn, &QPushButton::clicked, this, &ReaderWindow::onToggleFullscreen);
    navLayout->addWidget(m_fsBtn);

    m_readerSettingsBtn = new QPushButton("Settings", topNav);
    m_readerSettingsBtn->setIcon(createSvgIcon("M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z", 14, "#d6d3d1"));
    m_readerSettingsBtn->setToolTip("Preferences & Settings");
    m_readerSettingsBtn->setCursor(Qt::PointingHandCursor);
    m_readerSettingsBtn->setStyleSheet(toolbarBtnStyle(false));
    connect(m_readerSettingsBtn, &QPushButton::clicked, this, &ReaderWindow::onOpenSettingsDialog);
    navLayout->addWidget(m_readerSettingsBtn);

    readerLayout->addWidget(topNav);

    // Reading Canvas (Center)
    QWidget *canvasContainer = new QWidget(m_readerViewWidget);
    QHBoxLayout *canvasLayout = new QHBoxLayout(canvasContainer);
    canvasLayout->setContentsMargins(32, 16, 32, 16);
    canvasLayout->setSpacing(20);

    m_prevBtn = new QPushButton(canvasContainer);
    m_prevBtn->setIcon(createSvgIcon("M15 18l-6-6 6-6", 20, "#d6d3d1", 2.2));
    m_prevBtn->setIconSize(QSize(22, 22));
    m_prevBtn->setFixedSize(36, 72);
    m_prevBtn->setCursor(Qt::PointingHandCursor);
    m_prevBtn->setToolTip("Previous Page (Left Arrow / Page Up)");
    m_prevBtn->setStyleSheet(R"(
        QPushButton {
            background-color: rgba(30, 27, 25, 0.45);
            border: 1px solid rgba(87, 83, 78, 0.3);
            border-radius: 18px;
        }
        QPushButton:hover {
            background-color: rgba(194, 65, 12, 0.85);
            border-color: #ea580c;
        }
        QPushButton:pressed {
            background-color: #9a3412;
        }
    )");
    connect(m_prevBtn, &QPushButton::clicked, this, &ReaderWindow::onPrevPage);
    canvasLayout->addWidget(m_prevBtn);

    m_leftPageBrowser = new QTextBrowser(canvasContainer);
    m_leftPageBrowser->setOpenExternalLinks(false);
    m_leftPageBrowser->setFrameShape(QFrame::NoFrame);
    m_leftPageBrowser->setMaximumWidth(860);
    canvasLayout->addWidget(m_leftPageBrowser, 1);

    m_rightPageBrowser = new QTextBrowser(canvasContainer);
    m_rightPageBrowser->setOpenExternalLinks(false);
    m_rightPageBrowser->setFrameShape(QFrame::NoFrame);
    m_rightPageBrowser->setMaximumWidth(860);
    m_rightPageBrowser->setVisible(false);
    canvasLayout->addWidget(m_rightPageBrowser, 1);

    m_nextBtn = new QPushButton(canvasContainer);
    m_nextBtn->setIcon(createSvgIcon("M9 18l6-6-6-6", 20, "#d6d3d1", 2.2));
    m_nextBtn->setIconSize(QSize(22, 22));
    m_nextBtn->setFixedSize(36, 72);
    m_nextBtn->setCursor(Qt::PointingHandCursor);
    m_nextBtn->setToolTip("Next Page (Right Arrow / Space / Page Down)");
    m_nextBtn->setStyleSheet(R"(
        QPushButton {
            background-color: rgba(30, 27, 25, 0.45);
            border: 1px solid rgba(87, 83, 78, 0.3);
            border-radius: 18px;
        }
        QPushButton:hover {
            background-color: rgba(194, 65, 12, 0.85);
            border-color: #ea580c;
        }
        QPushButton:pressed {
            background-color: #9a3412;
        }
    )");
    connect(m_nextBtn, &QPushButton::clicked, this, &ReaderWindow::onNextPage);
    canvasLayout->addWidget(m_nextBtn);

    readerLayout->addWidget(canvasContainer, 1);

    // Bottom Navigation Bar
    QWidget *bottomBar = new QWidget(m_readerViewWidget);
    bottomBar->setStyleSheet("background-color: #171514; border-top: 1px solid #292524; padding: 6px 20px;");
    QHBoxLayout *bottomLayout = new QHBoxLayout(bottomBar);
    bottomLayout->setContentsMargins(0, 0, 0, 0);
    bottomLayout->setSpacing(12);

    QPushButton *prevPageBtn = new QPushButton(bottomBar);
    prevPageBtn->setIcon(createSvgIcon("M15 18l-6-6 6-6", 13, "#a8a29e"));
    prevPageBtn->setText("Prev");
    prevPageBtn->setCursor(Qt::PointingHandCursor);
    prevPageBtn->setStyleSheet(toolbarBtnStyle(false));
    connect(prevPageBtn, &QPushButton::clicked, this, &ReaderWindow::onPrevPage);
    bottomLayout->addWidget(prevPageBtn);

    m_pageSlider = new QSlider(Qt::Horizontal, bottomBar);
    m_pageSlider->setMinimum(1);
    m_pageSlider->setMaximum(1);
    m_pageSlider->setStyleSheet(R"(
        QSlider::groove:horizontal {
            height: 4px;
            background: #3d3835;
            border-radius: 2px;
        }
        QSlider::sub-page:horizontal {
            background: #c2410c;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #f5f5f4;
            border: 2px solid #ea580c;
            width: 14px;
            margin-top: -5px;
            margin-bottom: -5px;
            border-radius: 7px;
        }
        QSlider::handle:horizontal:hover {
            background: #ea580c;
            border-color: #ffffff;
        }
    )");
    connect(m_pageSlider, &QSlider::valueChanged, this, &ReaderWindow::onSliderPageChanged);
    bottomLayout->addWidget(m_pageSlider, 1);

    QPushButton *nextPageBtn = new QPushButton(bottomBar);
    nextPageBtn->setIcon(createSvgIcon("M9 18l6-6-6-6", 13, "#a8a29e"));
    nextPageBtn->setText("Next");
    nextPageBtn->setCursor(Qt::PointingHandCursor);
    nextPageBtn->setStyleSheet(toolbarBtnStyle(false));
    connect(nextPageBtn, &QPushButton::clicked, this, &ReaderWindow::onNextPage);
    bottomLayout->addWidget(nextPageBtn);

    m_pageIndicatorLabel = new QLabel("Page 1 of 1 • 0%", bottomBar);
    m_pageIndicatorLabel->setStyleSheet(R"(
        background-color: #24201e;
        border: 1px solid #3d3835;
        border-radius: 12px;
        padding: 4px 14px;
        color: #e7e5e4;
        font-size: 12px;
        font-weight: 600;
        min-width: 130px;
    )");
    m_pageIndicatorLabel->setAlignment(Qt::AlignCenter);
    bottomLayout->addWidget(m_pageIndicatorLabel);

    readerLayout->addWidget(bottomBar);
}

void ReaderWindow::setupDrawers() {
    // Table of Contents Dock
    m_tocDock = new QDockWidget("Table of Contents", this);
    m_tocDock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    QWidget *tocWidget = new QWidget(m_tocDock);
    QVBoxLayout *tLayout = new QVBoxLayout(tocWidget);
    tLayout->setContentsMargins(12, 12, 12, 12);
    tLayout->setSpacing(8);

    QLabel *tHeader = new QLabel("Chapters & Navigation:", tocWidget);
    tHeader->setStyleSheet("font-weight: 600; color: #c2410c; font-size: 13px;");
    tLayout->addWidget(tHeader);

    m_tocList = new QListWidget(tocWidget);
    m_tocList->setStyleSheet(R"(
        QListWidget {
            background-color: #171514;
            border: 1px solid #292524;
            border-radius: 6px;
            outline: none;
        }
        QListWidget::item {
            padding: 8px 12px;
            border-radius: 4px;
            color: #d6d3d1;
            font-size: 12px;
            margin: 1px 0px;
        }
        QListWidget::item:hover {
            background-color: #24201e;
            color: #ffffff;
        }
        QListWidget::item:selected {
            background-color: #c2410c;
            color: #ffffff;
            font-weight: 600;
        }
    )");
    connect(m_tocList, &QListWidget::itemClicked, this, &ReaderWindow::onTocHitSelected);
    tLayout->addWidget(m_tocList, 1);

    m_tocDock->setWidget(tocWidget);
    addDockWidget(Qt::LeftDockWidgetArea, m_tocDock);
    m_tocDock->hide();

    // Search In Book Dock
    m_searchDock = new QDockWidget("In-Book Search", this);
    m_searchDock->setAllowedAreas(Qt::RightDockWidgetArea);
    QWidget *searchWidget = new QWidget(m_searchDock);
    QVBoxLayout *sLayout = new QVBoxLayout(searchWidget);
    sLayout->setContentsMargins(12, 12, 12, 12);
    sLayout->setSpacing(10);

    QHBoxLayout *searchRow = new QHBoxLayout();
    m_inBookSearchEdit = new QLineEdit(searchWidget);
    m_inBookSearchEdit->setPlaceholderText("Search keyword in active book...");
    connect(m_inBookSearchEdit, &QLineEdit::returnPressed, this, &ReaderWindow::onExecuteSearch);
    searchRow->addWidget(m_inBookSearchEdit, 1);

    QPushButton *searchExecBtn = new QPushButton("Find", searchWidget);
    searchExecBtn->setIcon(createSvgIcon("M21 21l-4.35-4.35 M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16z", 13, "#ffffff"));
    searchExecBtn->setCursor(Qt::PointingHandCursor);
    searchExecBtn->setStyleSheet(R"(
        QPushButton {
            background-color: #c2410c;
            border: 1px solid #ea580c;
            border-radius: 6px;
            padding: 7px 12px;
            color: #ffffff;
            font-size: 12px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #ea580c;
        }
    )");
    connect(searchExecBtn, &QPushButton::clicked, this, &ReaderWindow::onExecuteSearch);
    searchRow->addWidget(searchExecBtn);
    sLayout->addLayout(searchRow);

    m_searchResultsList = new QListWidget(searchWidget);
    connect(m_searchResultsList, &QListWidget::itemClicked, this, &ReaderWindow::onSearchHitSelected);
    sLayout->addWidget(m_searchResultsList);

    m_searchDock->setWidget(searchWidget);
    addDockWidget(Qt::RightDockWidgetArea, m_searchDock);
    m_searchDock->hide();

    // Notes and Bookmarks Dock
    m_notesDock = new QDockWidget("Bookmarks & Notes", this);
    m_notesDock->setAllowedAreas(Qt::RightDockWidgetArea);
    QWidget *notesWidget = new QWidget(m_notesDock);
    QVBoxLayout *nLayout = new QVBoxLayout(notesWidget);
    nLayout->setContentsMargins(12, 12, 12, 12);
    nLayout->setSpacing(8);

    QLabel *bmHeader = new QLabel("Saved Bookmarks:", notesWidget);
    bmHeader->setStyleSheet("font-weight: 600; color: #c2410c;");
    nLayout->addWidget(bmHeader);

    m_bookmarksList = new QListWidget(notesWidget);
    m_bookmarksList->setMaximumHeight(150);
    connect(m_bookmarksList, &QListWidget::itemClicked, [this](QListWidgetItem *item) {
        int page = item->data(Qt::UserRole).toInt();
        if (page >= 1 && page <= m_loadedBook.pages.size()) {
            m_currentPageIndex = page - 1;
            displayCurrentPage();
        }
    });
    nLayout->addWidget(m_bookmarksList);

    QLabel *annHeader = new QLabel("Highlights & Commentary:", notesWidget);
    annHeader->setStyleSheet("font-weight: 600; color: #c2410c;");
    nLayout->addWidget(annHeader);

    m_annotationsList = new QListWidget(notesWidget);
    nLayout->addWidget(m_annotationsList, 1);

    // 4-Color Highlighter Palette Row
    QHBoxLayout *colorRow = new QHBoxLayout();
    QLabel *colorLabel = new QLabel("Highlight Color:", notesWidget);
    colorLabel->setStyleSheet("color: #a8a29e; font-size: 11px;");
    colorRow->addWidget(colorLabel);

    auto makeColorBtn = [this, notesWidget](const QString& hex, const QString& name) {
        QPushButton *btn = new QPushButton(notesWidget);
        btn->setFixedSize(22, 22);
        btn->setCursor(Qt::PointingHandCursor);
        btn->setToolTip(name + " Highlight");
        btn->setStyleSheet(QString(
            "QPushButton { background-color: %1; border: 2px solid #57534e; border-radius: 11px; }"
            "QPushButton:hover { border-color: #ffffff; }"
        ).arg(hex));
        connect(btn, &QPushButton::clicked, [this, name]() {
            onAddHighlightWithColor(name.toLower());
        });
        return btn;
    };

    m_hlAmberBtn = makeColorBtn("#ffe270", "Amber");
    m_hlEmeraldBtn = makeColorBtn("#a8f29a", "Emerald");
    m_hlAzureBtn = makeColorBtn("#7be5f8", "Azure");
    m_hlRoseBtn = makeColorBtn("#ffa0c5", "Rose");
    colorRow->addWidget(m_hlAmberBtn);
    colorRow->addWidget(m_hlEmeraldBtn);
    colorRow->addWidget(m_hlAzureBtn);
    colorRow->addWidget(m_hlRoseBtn);
    colorRow->addStretch();
    nLayout->addLayout(colorRow);

    QHBoxLayout *notesActions = new QHBoxLayout();
    QPushButton *highlightBtn = new QPushButton("Highlight Selected", notesWidget);
    highlightBtn->setIcon(createSvgIcon("m9 11-6 6v3h3l6-6 M22 12l-4.6 4.6a2 2 0 0 1-2.8 0l-5.2-5.2a2 2 0 0 1 0-2.8L14 4", 14, "#d6d3d1"));
    highlightBtn->setCursor(Qt::PointingHandCursor);
    highlightBtn->setStyleSheet(R"(
        QPushButton {
            background-color: #24201e;
            border: 1px solid #3d3835;
            border-radius: 6px;
            padding: 7px 12px;
            color: #d6d3d1;
            font-size: 12px;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #332d29;
            border-color: #57534e;
            color: #ffffff;
        }
    )");
    connect(highlightBtn, &QPushButton::clicked, this, &ReaderWindow::onAddHighlight);

    QPushButton *exportBtn = new QPushButton("Export HTML", notesWidget);
    exportBtn->setIcon(createSvgIcon("M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4 M7 10l5 5 5-5 M12 15V3", 14, "#ffffff"));
    exportBtn->setCursor(Qt::PointingHandCursor);
    exportBtn->setStyleSheet(R"(
        QPushButton {
            background-color: #c2410c;
            border: 1px solid #ea580c;
            border-radius: 6px;
            padding: 7px 14px;
            color: #ffffff;
            font-size: 12px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #ea580c;
        }
    )");
    connect(exportBtn, &QPushButton::clicked, this, &ReaderWindow::onExportNotesHtml);
    notesActions->addWidget(highlightBtn);
    notesActions->addWidget(exportBtn);
    nLayout->addLayout(notesActions);

    m_notesDock->setWidget(notesWidget);
    addDockWidget(Qt::RightDockWidgetArea, m_notesDock);
    m_notesDock->hide();
}

void ReaderWindow::applyTheme(ReaderTheme theme) {
    m_currentTheme = theme;
    QString bg, text, border;

    switch (theme) {
        case ReaderTheme::Day:
            bg = "#fafaf9";
            text = "#1c1917";
            border = "#e7e5e4";
            break;
        case ReaderTheme::Sepia:
            bg = "#f5ebd7";
            text = "#3d2f1d";
            border = "#e8dac0";
            break;
        case ReaderTheme::Night:
            bg = "#121212";
            text = "#d4d4d8";
            border = "#27272a";
            break;
        case ReaderTheme::DarkSepia:
            bg = "#251d16";
            text = "#c7b79d";
            border = "#3a3026";
            break;
    }

    QString browserStyle = QString(R"(
        QTextBrowser {
            background-color: %1;
            color: %2;
            border: 1px solid %3;
            border-radius: 8px;
            padding: %4px %5px;
            font-family: '%6', 'Georgia', serif;
            font-size: %7pt;
            selection-background-color: #c2410c;
            selection-color: #ffffff;
        }
        p {
            line-height: %8;
            margin-bottom: 1.25em;
        }
    )").arg(bg).arg(text).arg(border)
      .arg(m_pageMargin).arg(m_pageMargin + 10)
      .arg(m_fontFamily).arg(m_fontSizePt)
      .arg(m_lineHeight);

    m_leftPageBrowser->setStyleSheet(browserStyle);
    m_rightPageBrowser->setStyleSheet(browserStyle);

    updateThemeButtons();
}

void ReaderWindow::updateThemeButtons() {
    auto makeThemeStyle = [this](ReaderTheme theme) {
        bool isActive = (m_currentTheme == theme);
        if (isActive) {
            return QString(R"(
                QPushButton {
                    background-color: #382a20;
                    border: 1.5px solid #ea580c;
                    border-radius: 6px;
                    padding: 5px 11px;
                    color: #ffedd5;
                    font-size: 12px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #443224;
                }
            )");
        } else {
            return QString(R"(
                QPushButton {
                    background-color: #24201e;
                    border: 1px solid #3d3835;
                    border-radius: 6px;
                    padding: 5px 11px;
                    color: #a8a29e;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #2f2a27;
                    border-color: #57534e;
                    color: #f5f5f4;
                }
            )");
        }
    };

    if (m_themeDayBtn) m_themeDayBtn->setStyleSheet(makeThemeStyle(ReaderTheme::Day));
    if (m_themeSepiaBtn) m_themeSepiaBtn->setStyleSheet(makeThemeStyle(ReaderTheme::Sepia));
    if (m_themeNightBtn) m_themeNightBtn->setStyleSheet(makeThemeStyle(ReaderTheme::Night));
    if (m_themeDarkSepiaBtn) m_themeDarkSepiaBtn->setStyleSheet(makeThemeStyle(ReaderTheme::DarkSepia));
}

void ReaderWindow::updateLayoutButton() {
    if (!m_twoPagesBtn) return;
    if (m_isTwoPages) {
        m_twoPagesBtn->setIcon(createSvgIcon("M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z", 14, "#ffedd5"));
        m_twoPagesBtn->setText("2 Pages");
        m_twoPagesBtn->setToolTip("Switch to 1 Page View");
        m_twoPagesBtn->setStyleSheet(toolbarBtnStyle(true));
    } else {
        m_twoPagesBtn->setIcon(createSvgIcon("M4 2h16a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z M8 6h8 M8 10h8 M8 14h4", 14, "#d6d3d1"));
        m_twoPagesBtn->setText("1 Page");
        m_twoPagesBtn->setToolTip("Switch to 2 Pages View");
        m_twoPagesBtn->setStyleSheet(toolbarBtnStyle(false));
    }
}

void ReaderWindow::updateViewModeButtons(int modeIndex) {
    if (!m_viewGridBtn || !m_viewTableBtn) return;
    if (modeIndex == 0) { // Grid active
        m_viewGridBtn->setStyleSheet(R"(
            QPushButton {
                background-color: #c2410c;
                border: 1px solid #ea580c;
                border-top-left-radius: 6px;
                border-bottom-left-radius: 6px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                border-right: none;
                padding: 6px 14px;
                color: #ffffff;
                font-size: 12px;
                font-weight: 600;
            }
        )");
        m_viewTableBtn->setStyleSheet(R"(
            QPushButton {
                background-color: #24201e;
                border: 1px solid #3d3835;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                padding: 6px 14px;
                color: #a8a29e;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #332d29;
                color: #ffffff;
            }
        )");
    } else { // Table active
        m_viewGridBtn->setStyleSheet(R"(
            QPushButton {
                background-color: #24201e;
                border: 1px solid #3d3835;
                border-top-left-radius: 6px;
                border-bottom-left-radius: 6px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                border-right: none;
                padding: 6px 14px;
                color: #a8a29e;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #332d29;
                color: #ffffff;
            }
        )");
        m_viewTableBtn->setStyleSheet(R"(
            QPushButton {
                background-color: #c2410c;
                border: 1px solid #ea580c;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                padding: 6px 14px;
                color: #ffffff;
                font-size: 12px;
                font-weight: 600;
            }
        )");
    }
}

void ReaderWindow::updateDrawerButtons() {
    if (m_tocBtn) {
        bool active = m_tocDock && m_tocDock->isVisible();
        m_tocBtn->setStyleSheet(toolbarBtnStyle(active));
    }
    if (m_searchBtn) {
        bool active = m_searchDock && m_searchDock->isVisible();
        m_searchBtn->setStyleSheet(toolbarBtnStyle(active));
    }
    if (m_notesBtn) {
        bool active = m_notesDock && m_notesDock->isVisible();
        m_notesBtn->setStyleSheet(toolbarBtnStyle(active));
    }
}

void ReaderWindow::onThemeChanged(ReaderTheme theme) {
    applyTheme(theme);
}

void ReaderWindow::onToggleTwoPages() {
    m_isTwoPages = !m_isTwoPages;
    updateLayoutButton();
    m_rightPageBrowser->setVisible(m_isTwoPages);
    displayCurrentPage();
}

void ReaderWindow::onZoomIn() {
    if (m_fontSizePt < 32) {
        m_fontSizePt += 2;
        applyTheme(m_currentTheme);
    }
}

void ReaderWindow::onZoomOut() {
    if (m_fontSizePt > 10) {
        m_fontSizePt -= 2;
        applyTheme(m_currentTheme);
    }
}

void ReaderWindow::onToggleFullscreen() {
    if (isFullScreen()) {
        showNormal();
    } else {
        showFullScreen();
    }
}

void ReaderWindow::refreshLibrary() {
    m_currentBooks = DatabaseManager::instance().getBooks(m_searchLibraryEdit->text(), m_activeCategory);

    // Empty state handling
    if (m_emptyStateWidget && m_viewModeStack) {
        if (m_currentBooks.isEmpty()) {
            m_emptyStateWidget->show();
            m_viewModeStack->hide();
        } else {
            m_emptyStateWidget->hide();
            m_viewModeStack->show();
        }
    }

    // Refresh Grid View
    m_bookGridList->clear();
    for (const BookRecord& b : m_currentBooks) {
        QListWidgetItem *item = new QListWidgetItem(m_bookGridList);
        item->setText(QString("%1\n%2").arg(b.title).arg(b.author));
        item->setData(Qt::UserRole, b.id);
        item->setToolTip(QString("Title: %1\nAuthor: %2\nFormat: %3\nProgress: %4%\nFile: %5")
                         .arg(b.title).arg(b.author).arg(b.format).arg((int)b.progressPercent).arg(b.filePath));

        // Create archival book cover card
        QPixmap cardPix(140, 200);
        cardPix.fill(Qt::transparent);
        QPainter p(&cardPix);
        p.setRenderHint(QPainter::Antialiasing);

        // Palette tailored by format
        QColor clothColor("#292524");
        QColor accentBadge("#c2410c");
        if (b.format == "EPUB") {
            clothColor = QColor("#1e293b"); // Deep slate navy
            accentBadge = QColor("#0284c7");
        } else if (b.format == "PDF") {
            clothColor = QColor("#3c1f1e"); // Burgundy clay
            accentBadge = QColor("#dc2626");
        } else if (b.format == "MOBI") {
            clothColor = QColor("#1e2e24"); // Forest leather
            accentBadge = QColor("#16a34a");
        }

        // Cover background
        p.setBrush(clothColor);
        p.setPen(QPen(QColor("#44403c"), 1.5));
        p.drawRoundedRect(1, 1, 138, 198, 4, 4);

        // 3D Spine Shadow on left margin
        QLinearGradient spineGrad(1, 0, 10, 0);
        spineGrad.setColorAt(0, QColor(0, 0, 0, 150));
        spineGrad.setColorAt(1, QColor(0, 0, 0, 0));
        p.fillRect(QRect(1, 1, 10, 198), spineGrad);

        // Inner frame line
        p.setPen(QPen(QColor(214, 211, 209, 50), 1));
        p.drawRoundedRect(10, 10, 120, 180, 2, 2);

        // Format pill badge top right
        p.setBrush(accentBadge);
        p.setPen(Qt::NoPen);
        p.drawRoundedRect(QRect(84, 16, 42, 16), 3, 3);
        p.setPen(Qt::white);
        p.setFont(QFont("Segoe UI", 8, QFont::Bold));
        p.drawText(QRect(84, 16, 42, 16), Qt::AlignCenter, b.format);

        // Book Title (Serif, wrapped, centered)
        p.setPen(QColor("#f5f0eb"));
        QFont titleFont("Georgia", 9, QFont::Bold);
        p.setFont(titleFont);
        QRect titleRect(14, 46, 112, 68);
        p.drawText(titleRect, Qt::AlignCenter | Qt::TextWordWrap, b.title);

        // Terracotta divider line
        p.setPen(QPen(QColor("#c2410c"), 1.2));
        p.drawLine(52, 122, 88, 122);

        // Author
        p.setPen(QColor("#a8a29e"));
        QFont authorFont("Segoe UI", 8);
        p.setFont(authorFont);
        QRect authorRect(14, 130, 112, 36);
        p.drawText(authorRect, Qt::AlignCenter | Qt::TextWordWrap, b.author);

        // Progress bar at bottom
        p.setBrush(QColor("#171514"));
        p.setPen(Qt::NoPen);
        p.drawRoundedRect(QRect(16, 178, 108, 4), 2, 2);
        if (b.progressPercent > 0) {
            p.setBrush(QColor("#ea580c"));
            int fillW = qBound(4, (int)(108.0 * (b.progressPercent / 100.0)), 108);
            p.drawRoundedRect(QRect(16, 178, fillW, 4), 2, 2);
        }

        item->setIcon(QIcon(cardPix));
        m_bookGridList->addItem(item);
    }

    // Refresh Table View
    m_bookTableWidget->setRowCount(m_currentBooks.size());
    for (int i = 0; i < m_currentBooks.size(); ++i) {
        const BookRecord& b = m_currentBooks[i];
        m_bookTableWidget->setItem(i, 0, new QTableWidgetItem(b.title));
        m_bookTableWidget->setItem(i, 1, new QTableWidgetItem(b.author));
        m_bookTableWidget->setItem(i, 2, new QTableWidgetItem(b.format));
        m_bookTableWidget->setItem(i, 3, new QTableWidgetItem(QString("%1%").arg((int)b.progressPercent)));
        m_bookTableWidget->setItem(i, 4, new QTableWidgetItem(QString("%1 KB").arg(b.fileSize / 1024)));
        m_bookTableWidget->setItem(i, 5, new QTableWidgetItem(b.createdAt.toString("yyyy-MM-dd")));
    }

    m_statusLabel->setText(QString("%1 books in collection • Filter: %2").arg(m_currentBooks.size()).arg(m_activeCategory));
    updateSidebarBadges();
}

void ReaderWindow::onAddBookClicked() {
    QStringList files = QFileDialog::getOpenFileNames(
        this,
        "Import Ebooks into FolioHaven",
        QString(),
        "Supported Books (*.epub *.pdf *.mobi *.fb2 *.cbz *.txt);;EPUB Ebooks (*.epub);;PDF Documents (*.pdf);;All Files (*.*)"
    );

    for (const QString& f : files) {
        openBookFile(f);
    }
}

void ReaderWindow::openBookFile(const QString& filePath) {
    if (!QFile::exists(filePath)) return;

    LoadedBook book = DocumentEngine::loadDocument(filePath);
    if (!book.isValid) {
        QMessageBox::warning(this, "Failed to Open Book", book.errorMessage.isEmpty() ? "The file could not be parsed." : book.errorMessage);
        return;
    }

    // Save to database
    BookRecord rec;
    rec.title = book.title;
    rec.author = book.author;
    rec.format = book.format;
    rec.filePath = book.filePath;
    rec.fileSize = book.fileSize;
    rec.totalPages = std::max(1, (int)book.pages.size());
    rec.currentPage = 1;
    rec.progressPercent = 0.0;

    int bookId = DatabaseManager::instance().insertBook(rec);
    rec.id = bookId;

    m_activeBookRecord = rec;
    m_loadedBook = book;
    m_currentPageIndex = 0;

    // Switch to Reader View
    m_readerTitleLabel->setText(QString("%1 — %2").arg(book.title).arg(book.author));
    if (m_readerFormatBadge) {
        m_readerFormatBadge->setText(book.format);
    }
    m_pageSlider->setMaximum(std::max(1, (int)book.pages.size()));
    m_pageSlider->setValue(1);

    m_stackWidget->setCurrentIndex(1);
    applyTheme(m_currentTheme);
    updateLayoutButton();
    updateDrawerButtons();

    // Populate Table of Contents
    if (m_tocList) {
        m_tocList->clear();
        for (const auto& item : book.toc) {
            const QString& title = item.first;
            int pageIndex = item.second;
            QListWidgetItem *it = new QListWidgetItem(title, m_tocList);
            it->setData(Qt::UserRole, pageIndex);
            it->setToolTip(QString("Jump to Page %1").arg(pageIndex + 1));
        }
    }

    displayCurrentPage();
    refreshLibrary();
}

void ReaderWindow::displayCurrentPage() {
    if (!m_loadedBook.isValid || m_loadedBook.pages.isEmpty()) return;

    int total = m_loadedBook.pages.size();
    if (m_currentPageIndex < 0) m_currentPageIndex = 0;
    if (m_currentPageIndex >= total) m_currentPageIndex = total - 1;

    m_leftPageBrowser->setHtml(m_loadedBook.pages[m_currentPageIndex]);

    if (m_isTwoPages) {
        if (m_currentPageIndex + 1 < total) {
            m_rightPageBrowser->setHtml(m_loadedBook.pages[m_currentPageIndex + 1]);
        } else {
            m_rightPageBrowser->setHtml("<p><em>(End of publication)</em></p>");
        }
    }

    updateProgressDisplay();
}

void ReaderWindow::updateProgressDisplay() {
    int total = std::max(1, (int)m_loadedBook.pages.size());
    int cur = m_currentPageIndex + 1;
    double pct = (double)cur / (double)total * 100.0;

    m_pageSlider->blockSignals(true);
    m_pageSlider->setValue(cur);
    m_pageSlider->blockSignals(false);

    m_pageIndicatorLabel->setText(QString("Page %1 of %2 • %3%").arg(cur).arg(total).arg((int)pct));
    saveCurrentProgress();
}

void ReaderWindow::saveCurrentProgress() {
    if (m_activeBookRecord.id > 0 && !m_loadedBook.pages.isEmpty()) {
        int total = m_loadedBook.pages.size();
        int cur = m_currentPageIndex + 1;
        double pct = (double)cur / (double)total * 100.0;
        DatabaseManager::instance().updateProgress(m_activeBookRecord.id, cur, total, pct);
    }
}

void ReaderWindow::onPrevPage() {
    int step = m_isTwoPages ? 2 : 1;
    if (m_currentPageIndex > 0) {
        m_currentPageIndex = std::max(0, m_currentPageIndex - step);
        displayCurrentPage();
    }
}

void ReaderWindow::onNextPage() {
    int step = m_isTwoPages ? 2 : 1;
    if (m_currentPageIndex + step < m_loadedBook.pages.size()) {
        m_currentPageIndex += step;
        displayCurrentPage();
    }
}

void ReaderWindow::onSliderPageChanged(int value) {
    m_currentPageIndex = value - 1;
    displayCurrentPage();
}

void ReaderWindow::onCloseReader() {
    saveCurrentProgress();
    if (m_tocDock) m_tocDock->hide();
    m_searchDock->hide();
    m_notesDock->hide();
    updateDrawerButtons();
    m_stackWidget->setCurrentIndex(0);
    refreshLibrary();
}

void ReaderWindow::onCategorySelected(QListWidgetItem *item) {
    if (!item) return;
    QString key = item->data(Qt::UserRole).toString();
    if (key.isEmpty()) {
        key = item->text();
        int p = key.lastIndexOf(" (");
        if (p > 0) key = key.left(p);
    }
    if (key == "EPUB Documents") m_activeCategory = "EPUB";
    else if (key == "PDF Documents") m_activeCategory = "PDF";
    else if (key == "MOBI Ebooks") m_activeCategory = "MOBI";
    else if (key == "TXT Files") m_activeCategory = "TXT";
    else m_activeCategory = key;

    refreshLibrary();
}

void ReaderWindow::onSearchLibraryChanged(const QString& /*text*/) {
    refreshLibrary();
}

void ReaderWindow::onViewModeToggled(int modeIndex) {
    m_viewModeStack->setCurrentIndex(modeIndex);
    updateViewModeButtons(modeIndex);
}

void ReaderWindow::onBookDoubleClicked(QListWidgetItem *item) {
    if (!item) return;
    int bookId = item->data(Qt::UserRole).toInt();
    auto book = DatabaseManager::instance().getBookById(bookId);
    if (book) {
        openBookFile(book->filePath);
    }
}

void ReaderWindow::onBookTableRowDoubleClicked(int row, int /*column*/) {
    if (row >= 0 && row < m_currentBooks.size()) {
        openBookFile(m_currentBooks[row].filePath);
    }
}

void ReaderWindow::onToggleSearchDrawer() {
    m_searchDock->setVisible(!m_searchDock->isVisible());
    if (m_searchDock->isVisible()) {
        m_inBookSearchEdit->setFocus();
    }
    updateDrawerButtons();
}

void ReaderWindow::onExecuteSearch() {
    QString q = m_inBookSearchEdit->text();
    m_searchResultsList->clear();
    if (q.trimmed().isEmpty()) return;

    auto hits = DocumentEngine::search(m_loadedBook, q);
    for (const SearchHit& h : hits) {
        QListWidgetItem *item = new QListWidgetItem(QString("Page %1: %2").arg(h.pageIndex + 1).arg(h.snippet));
        item->setData(Qt::UserRole, h.pageIndex);
        m_searchResultsList->addItem(item);
    }
}

void ReaderWindow::onSearchHitSelected(QListWidgetItem *item) {
    if (!item) return;
    int pageIdx = item->data(Qt::UserRole).toInt();
    m_currentPageIndex = pageIdx;
    displayCurrentPage();
}

void ReaderWindow::onToggleNotesDrawer() {
    m_notesDock->setVisible(!m_notesDock->isVisible());
    updateDrawerButtons();
    if (m_notesDock->isVisible() && m_activeBookRecord.id > 0) {
        // Refresh Bookmarks
        m_bookmarksList->clear();
        auto bms = DatabaseManager::instance().getBookmarks(m_activeBookRecord.id);
        for (const auto& bm : bms) {
            QListWidgetItem *it = new QListWidgetItem(QString("Page %1 — %2").arg(bm.page).arg(bm.title));
            it->setData(Qt::UserRole, bm.page);
            m_bookmarksList->addItem(it);
        }

        // Refresh Annotations
        m_annotationsList->clear();
        auto anns = DatabaseManager::instance().getAnnotations(m_activeBookRecord.id);
        for (const auto& a : anns) {
            m_annotationsList->addItem(QString("[P.%1] \"%2\" — Note: %3").arg(a.page).arg(a.text).arg(a.note));
        }
    }
}

void ReaderWindow::onAddBookmark() {
    if (m_activeBookRecord.id > 0) {
        int page = m_currentPageIndex + 1;
        DatabaseManager::instance().addBookmark(m_activeBookRecord.id, page, QString("Bookmark at Page %1").arg(page));
        QMessageBox::information(this, "Bookmark Added", QString("Page %1 has been bookmarked.").arg(page));
        if (m_notesDock->isVisible()) {
            onToggleNotesDrawer();
            onToggleNotesDrawer();
        }
    }
}

void ReaderWindow::onAddHighlight() {
    QTextCursor cursor = m_leftPageBrowser->textCursor();
    if (cursor.hasSelection() && m_activeBookRecord.id > 0) {
        QString selected = cursor.selectedText();
        int page = m_currentPageIndex + 1;
        DatabaseManager::instance().addAnnotation(m_activeBookRecord.id, selected, "Quick highlight", "amber", page);
        QMessageBox::information(this, "Highlight Saved", "Passage saved to your study notes.");
    } else {
        QMessageBox::information(this, "Select Text", "Please highlight text on the reading canvas first.");
    }
}

void ReaderWindow::onExportNotesHtml() {
    if (m_activeBookRecord.id <= 0) return;

    QString savePath = QFileDialog::getSaveFileName(this, "Export Study Notes", QString("%1_Notes.html").arg(m_activeBookRecord.title), "HTML Files (*.html)");
    if (savePath.isEmpty()) return;

    auto anns = DatabaseManager::instance().getAnnotations(m_activeBookRecord.id);
    auto bms = DatabaseManager::instance().getBookmarks(m_activeBookRecord.id);

    QString html = QString(R"(
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Study Notes — %1</title>
            <style>
                body { font-family: 'Segoe UI', system-ui, sans-serif; max-width: 800px; margin: 40px auto; line-height: 1.6; color: #1c1917; background: #fafaf9; }
                h1 { color: #c2410c; border-bottom: 2px solid #c2410c; padding-bottom: 8px; }
                .quote { background: #fffbeb; border: 1px solid rgba(245, 158, 11, 0.4); padding: 14px 18px; margin: 12px 0; border-radius: 6px; }
                .bookmark { background: #f5f5f4; border: 1px solid #d6d3d1; padding: 8px 12px; border-radius: 4px; margin-bottom: 6px; }
            </style>
        </head>
        <body>
            <h1>Study Notes: %1</h1>
            <p><strong>Author:</strong> %2 | <strong>Format:</strong> %3</p>
            <hr>
            <h2>Bookmarks</h2>
    )").arg(m_activeBookRecord.title).arg(m_activeBookRecord.author).arg(m_activeBookRecord.format);

    for (const auto& bm : bms) {
        html += QString("<div class='bookmark'>Bookmark on Page %1: %2</div>").arg(bm.page).arg(bm.title);
    }

    html += "<h2>Highlights & Annotations</h2>";
    for (const auto& a : anns) {
        html += QString("<div class='quote'><strong>Page %1:</strong> \"%2\"<br><em>Note: %3</em></div>").arg(a.page).arg(a.text).arg(a.note);
    }

    html += "</body></html>";

    QFile file(savePath);
    if (file.open(QIODevice::WriteOnly | QIODevice::Text)) {
        QTextStream out(&file);
        out << html;
        file.close();
        QDesktopServices::openUrl(QUrl::fromLocalFile(savePath));
    }
}

void ReaderWindow::onToggleReadAloud() {
#ifdef Q_OS_WIN
    if (!g_pVoice) return;

    if (m_isSpeaking) {
        g_pVoice->Pause();
        m_isSpeaking = false;
        m_speakBtn->setText("Read Aloud");
        m_speakBtn->setIcon(createSvgIcon("M11 5L6 9H2v6h4l5 4V5z M19.07 4.93a10 10 0 0 1 0 14.14 M15.54 8.46a5 5 0 0 1 0 7.07", 14, "#d6d3d1"));
        m_speakBtn->setStyleSheet(toolbarBtnStyle(false));
    } else {
        QString textToSpeak = m_leftPageBrowser->toPlainText();
        if (textToSpeak.trimmed().isEmpty()) return;

        m_isSpeaking = true;
        m_speakBtn->setText("Pause");
        m_speakBtn->setIcon(createSvgIcon("M6 4h4v16H6z M14 4h4v16h-4z", 14, "#ffffff"));
        m_speakBtn->setStyleSheet(R"(
            QPushButton {
                background-color: #c2410c;
                border: 1px solid #ea580c;
                border-radius: 6px;
                padding: 5px 12px;
                color: #ffffff;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #ea580c;
            }
        )");
        g_pVoice->Speak(textToSpeak.toStdWString().c_str(), SPF_ASYNC | SPF_PURGEBEFORESPEAK, nullptr);
    }
#endif
}

void ReaderWindow::onOpenSettingsDialog() {
    QDialog dialog(this);
    dialog.setWindowTitle("FolioHaven — Preferences & Settings");
    dialog.setFixedSize(540, 520);
    dialog.setStyleSheet(R"(
        QDialog {
            background-color: #1c1917;
            color: #f5f5f4;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        QLabel {
            color: #f5f5f4;
            font-size: 13px;
        }
        QTabWidget::pane {
            border: 1px solid #3d3835;
            background-color: #171514;
            border-radius: 8px;
            padding: 16px;
        }
        QTabBar::tab {
            background-color: #24201e;
            color: #a8a29e;
            border: 1px solid #3d3835;
            border-bottom: none;
            padding: 8px 18px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        QTabBar::tab:selected {
            background-color: #171514;
            color: #ea580c;
            border-top: 2px solid #ea580c;
        }
        QComboBox, QSpinBox {
            background-color: #24201e;
            border: 1px solid #3d3835;
            border-radius: 6px;
            padding: 6px 12px;
            color: #f5f5f4;
            font-size: 13px;
        }
        QComboBox:focus, QSpinBox:focus {
            border-color: #ea580c;
        }
        QComboBox::drop-down {
            border: none;
        }
        QPushButton {
            background-color: #24201e;
            border: 1px solid #3d3835;
            border-radius: 6px;
            padding: 8px 16px;
            color: #f5f5f4;
            font-size: 13px;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #332d29;
            border-color: #57534e;
        }
    )");

    QVBoxLayout *dlgLayout = new QVBoxLayout(&dialog);
    dlgLayout->setContentsMargins(20, 20, 20, 20);
    dlgLayout->setSpacing(16);

    QHBoxLayout *headerLayout = new QHBoxLayout();
    QLabel *titleLabel = new QLabel("Preferences & Settings", &dialog);
    titleLabel->setStyleSheet("font-size: 18px; font-weight: 700; color: #f5f5f4;");
    headerLayout->addWidget(titleLabel);
    headerLayout->addStretch();
    dlgLayout->addLayout(headerLayout);

    QTabWidget *tabs = new QTabWidget(&dialog);

    // Tab 1: Reading & Display
    QWidget *readTab = new QWidget();
    QVBoxLayout *readLayout = new QVBoxLayout(readTab);
    readLayout->setSpacing(14);

    QFormLayout *form = new QFormLayout();
    form->setLabelAlignment(Qt::AlignLeft);
    form->setFormAlignment(Qt::AlignLeft | Qt::AlignTop);
    form->setHorizontalSpacing(20);
    form->setVerticalSpacing(14);

    QComboBox *themeCombo = new QComboBox(readTab);
    themeCombo->addItem("Sepia (Archival Warm)", static_cast<int>(ReaderTheme::Sepia));
    themeCombo->addItem("Day (Crisp Ivory)", static_cast<int>(ReaderTheme::Day));
    themeCombo->addItem("Night (Low Glare OLED)", static_cast<int>(ReaderTheme::Night));
    themeCombo->addItem("Dark Sepia (Deep Tobacco)", static_cast<int>(ReaderTheme::DarkSepia));
    themeCombo->setCurrentIndex(static_cast<int>(m_currentTheme));
    form->addRow("Default Reading Theme:", themeCombo);

    QComboBox *layoutCombo = new QComboBox(readTab);
    layoutCombo->addItem("Single Page (Reflowable)", false);
    layoutCombo->addItem("Two Pages (Book Spread)", true);
    layoutCombo->setCurrentIndex(m_isTwoPages ? 1 : 0);
    form->addRow("Page Layout Mode:", layoutCombo);

    QComboBox *fontFamCombo = new QComboBox(readTab);
    fontFamCombo->addItem("Georgia (Classic Serif)", "Georgia");
    fontFamCombo->addItem("Palatino Linotype (Editorial)", "Palatino Linotype");
    fontFamCombo->addItem("Segoe UI (Modern Sans)", "Segoe UI");
    fontFamCombo->addItem("Consolas (Monospace)", "Consolas");
    int curFamIdx = fontFamCombo->findData(m_fontFamily);
    if (curFamIdx >= 0) fontFamCombo->setCurrentIndex(curFamIdx);
    form->addRow("Font Family:", fontFamCombo);

    QSpinBox *fontSpin = new QSpinBox(readTab);
    fontSpin->setRange(10, 36);
    fontSpin->setValue(m_fontSizePt);
    fontSpin->setSuffix(" pt");
    form->addRow("Font Size:", fontSpin);

    QComboBox *lineSpacingCombo = new QComboBox(readTab);
    lineSpacingCombo->addItem("1.4x (Compact)", 1.4);
    lineSpacingCombo->addItem("1.7x (Optimal Reading)", 1.7);
    lineSpacingCombo->addItem("2.0x (Double Spaced)", 2.0);
    int curLineIdx = (m_lineHeight == 1.4 ? 0 : (m_lineHeight == 2.0 ? 2 : 1));
    lineSpacingCombo->setCurrentIndex(curLineIdx);
    form->addRow("Line Spacing:", lineSpacingCombo);

    QComboBox *marginCombo = new QComboBox(readTab);
    marginCombo->addItem("Narrow (24px)", 24);
    marginCombo->addItem("Normal (40px)", 40);
    marginCombo->addItem("Generous (60px)", 60);
    int curMarginIdx = (m_pageMargin == 24 ? 0 : (m_pageMargin == 60 ? 2 : 1));
    marginCombo->setCurrentIndex(curMarginIdx);
    form->addRow("Page Margins:", marginCombo);

    readLayout->addLayout(form);
    readLayout->addStretch();
    tabs->addTab(readTab, "Reading & Display");

    // Tab 2: Speech & Cache
    QWidget *sysTab = new QWidget();
    QVBoxLayout *sysLayout = new QVBoxLayout(sysTab);
    sysLayout->setSpacing(14);

    QLabel *ttsDesc = new QLabel("Speech Synthesis (Windows SAPI):", sysTab);
    ttsDesc->setStyleSheet("font-weight: 600; color: #ea580c;");
    sysLayout->addWidget(ttsDesc);

    QLabel *ttsInfo = new QLabel("High-speed offline text-to-speech using native Windows speech runtime.\nShortcut: Press F7 or click 'Read Aloud' in reader toolbar.", sysTab);
    ttsInfo->setStyleSheet("color: #a8a29e; font-size: 12px;");
    ttsInfo->setWordWrap(true);
    sysLayout->addWidget(ttsInfo);

    QFrame *div = new QFrame(sysTab);
    div->setFrameShape(QFrame::HLine);
    div->setStyleSheet("color: #3d3835; margin: 10px 0;");
    sysLayout->addWidget(div);

    QLabel *cacheHeader = new QLabel("Document & PDF Hardware Render Cache:", sysTab);
    cacheHeader->setStyleSheet("font-weight: 600; color: #ea580c;");
    sysLayout->addWidget(cacheHeader);

    QString cachePath = QStandardPaths::writableLocation(QStandardPaths::CacheLocation) + "/pdf_cache";
    QDir cacheDir(cachePath);
    qint64 cacheSizeBytes = 0;
    if (cacheDir.exists()) {
        QDirIterator it(cachePath, QDir::Files, QDirIterator::Subdirectories);
        while (it.hasNext()) {
            it.next();
            cacheSizeBytes += it.fileInfo().size();
        }
    }
    double cacheMb = (double)cacheSizeBytes / (1024.0 * 1024.0);

    QLabel *cacheInfoLabel = new QLabel(QString("Current cache location:\n%1\nCached size: %2 MB").arg(cachePath).arg(QString::number(cacheMb, 'f', 2)), sysTab);
    cacheInfoLabel->setStyleSheet("color: #a8a29e; font-size: 12px; font-family: monospace;");
    cacheInfoLabel->setWordWrap(true);
    sysLayout->addWidget(cacheInfoLabel);

    QPushButton *clearCacheBtn = new QPushButton("Clear Hardware PDF Cache", sysTab);
    clearCacheBtn->setIcon(createSvgIcon("M3 6h18 M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6 M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2", 14, "#f87171"));
    clearCacheBtn->setStyleSheet("background-color: #2a1f1f; border: 1px solid #7f1d1d; color: #fca5a5; font-size: 12px; padding: 6px 14px;");
    connect(clearCacheBtn, &QPushButton::clicked, [cachePath, cacheInfoLabel]() {
        QDir dir(cachePath);
        if (dir.exists()) {
            dir.removeRecursively();
            cacheInfoLabel->setText(QString("Current cache location:\n%1\nCached size: 0.00 MB (Cleaned)").arg(cachePath));
        }
    });
    sysLayout->addWidget(clearCacheBtn);
    sysLayout->addStretch();
    tabs->addTab(sysTab, "Speech & Cache");

    // Tab 3: Keyboard Shortcuts
    QWidget *kbTab = new QWidget();
    QVBoxLayout *kbLayout = new QVBoxLayout(kbTab);
    QTableWidget *kbTable = new QTableWidget(7, 2, kbTab);
    kbTable->setHorizontalHeaderLabels({"Shortcut Key", "Action"});
    kbTable->horizontalHeader()->setStretchLastSection(true);
    kbTable->horizontalHeader()->setSectionResizeMode(0, QHeaderView::ResizeToContents);
    kbTable->verticalHeader()->setVisible(false);
    kbTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    kbTable->setSelectionMode(QAbstractItemView::NoSelection);
    kbTable->setStyleSheet("background: transparent; border: 1px solid #3d3835; font-size: 12px;");

    auto setRow = [kbTable](int r, const QString& k, const QString& a) {
        kbTable->setItem(r, 0, new QTableWidgetItem(k));
        kbTable->setItem(r, 1, new QTableWidgetItem(a));
    };
    setRow(0, "Esc", "Return to Library View");
    setRow(1, "Left Arrow / Page Up", "Previous Page");
    setRow(2, "Right Arrow / Space / Page Down", "Next Page");
    setRow(3, "F", "Toggle Fullscreen Mode");
    setRow(4, "F7", "Toggle Text-to-Speech (Read Aloud)");
    setRow(5, "Double Click Book", "Open book in reader");
    setRow(6, "Drag & Drop", "Import any book into library");

    kbLayout->addWidget(kbTable);
    tabs->addTab(kbTab, "Keyboard Shortcuts");

    dlgLayout->addWidget(tabs);

    // Dialog bottom buttons
    QHBoxLayout *btnLayout = new QHBoxLayout();
    btnLayout->addStretch();

    QPushButton *cancelBtn = new QPushButton("Cancel", &dialog);
    connect(cancelBtn, &QPushButton::clicked, &dialog, &QDialog::reject);
    btnLayout->addWidget(cancelBtn);

    QPushButton *saveBtn = new QPushButton("Save Preferences", &dialog);
    saveBtn->setStyleSheet(R"(
        QPushButton {
            background-color: #c2410c;
            color: #ffffff;
            border: 1px solid #ea580c;
            font-weight: 600;
            padding: 8px 18px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #ea580c;
        }
    )");
    connect(saveBtn, &QPushButton::clicked, [this, &dialog, themeCombo, layoutCombo, fontSpin, fontFamCombo, lineSpacingCombo, marginCombo]() {
        ReaderTheme chosenTheme = static_cast<ReaderTheme>(themeCombo->currentData().toInt());
        bool chosenTwoPages = layoutCombo->currentData().toBool();
        int chosenFont = fontSpin->value();

        m_fontSizePt = chosenFont;
        m_fontFamily = fontFamCombo->currentData().toString();
        m_lineHeight = lineSpacingCombo->currentData().toDouble();
        m_pageMargin = marginCombo->currentData().toInt();

        if (m_isTwoPages != chosenTwoPages) {
            m_isTwoPages = chosenTwoPages;
            updateLayoutButton();
            if (m_rightPageBrowser) {
                m_rightPageBrowser->setVisible(m_isTwoPages);
            }
        }
        applyTheme(chosenTheme);
        displayCurrentPage();
        dialog.accept();
    });
    btnLayout->addWidget(saveBtn);

    dlgLayout->addLayout(btnLayout);
    dialog.exec();
}

void ReaderWindow::dragEnterEvent(QDragEnterEvent *event) {
    if (event->mimeData()->hasUrls()) {
        event->acceptProposedAction();
    }
}

void ReaderWindow::dropEvent(QDropEvent *event) {
    for (const QUrl& url : event->mimeData()->urls()) {
        if (url.isLocalFile()) {
            openBookFile(url.toLocalFile());
        }
    }
}

void ReaderWindow::keyPressEvent(QKeyEvent *event) {
    if (event->key() == Qt::Key_Escape) {
        if (m_stackWidget->currentIndex() == 1) {
            onCloseReader();
            return;
        }
    } else if (event->key() == Qt::Key_F) {
        onToggleFullscreen();
        return;
    } else if (event->key() == Qt::Key_Right || event->key() == Qt::Key_PageDown || event->key() == Qt::Key_Space) {
        if (m_stackWidget->currentIndex() == 1) {
            onNextPage();
            return;
        }
    } else if (event->key() == Qt::Key_Left || event->key() == Qt::Key_PageUp) {
        if (m_stackWidget->currentIndex() == 1) {
            onPrevPage();
            return;
        }
    }
    QMainWindow::keyPressEvent(event);
}

void ReaderWindow::onToggleTocDrawer() {
    if (!m_tocDock) return;
    m_tocDock->setVisible(!m_tocDock->isVisible());
    updateDrawerButtons();
}

void ReaderWindow::onTocHitSelected(QListWidgetItem *item) {
    if (!item) return;
    int targetPage = item->data(Qt::UserRole).toInt();
    if (targetPage >= 0 && targetPage < m_loadedBook.pages.size()) {
        m_currentPageIndex = targetPage;
        displayCurrentPage();
    }
}

void ReaderWindow::onAddHighlightWithColor(const QString& colorCode) {
    m_selectedHighlightColor = colorCode;
    QTextCursor cursor = m_leftPageBrowser->textCursor();
    if (cursor.hasSelection() && m_activeBookRecord.id > 0) {
        QString selected = cursor.selectedText();
        int page = m_currentPageIndex + 1;
        DatabaseManager::instance().addAnnotation(m_activeBookRecord.id, selected, QString("Note (%1)").arg(colorCode), colorCode, page);
        QMessageBox::information(this, "Highlight Saved", QString("Passage saved with %1 highlight.").arg(colorCode));
        if (m_notesDock && m_notesDock->isVisible()) {
            onToggleNotesDrawer();
            onToggleNotesDrawer();
        }
    } else {
        QMessageBox::information(this, "Select Text", "Please highlight text on the reading canvas first.");
    }
}

void ReaderWindow::onAddCategoryClicked() {
    bool ok = false;
    QString catName = QInputDialog::getText(this, "New Category", "Category Name:", QLineEdit::Normal, "", &ok);
    catName = catName.trimmed();
    if (ok && !catName.isEmpty()) {
        if (!m_customCategories.contains(catName)) {
            m_customCategories.append(catName);
            QListWidgetItem *it = new QListWidgetItem(m_sidebarList);
            it->setText(catName);
            it->setData(Qt::UserRole, catName);
            it->setIcon(createSvgIcon("M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z", 16, "#d6d3d1"));
            updateSidebarBadges();
        }
    }
}

void ReaderWindow::onBookGridContextMenu(const QPoint &pos) {
    QListWidgetItem *item = m_bookGridList->itemAt(pos);
    if (!item) return;
    int bookId = item->data(Qt::UserRole).toInt();
    auto bookOpt = DatabaseManager::instance().getBookById(bookId);
    if (!bookOpt) return;
    BookRecord b = *bookOpt;

    QMenu menu(this);
    menu.setStyleSheet(R"(
        QMenu {
            background-color: #24201e;
            border: 1px solid #3d3835;
            border-radius: 6px;
            padding: 4px;
            color: #f5f5f4;
            font-size: 13px;
        }
        QMenu::item {
            padding: 6px 20px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: #c2410c;
            color: #ffffff;
        }
    )");

    QAction *openAct = menu.addAction("Read Book");
    QAction *favAct = menu.addAction(b.isFavorite ? "Remove from Favorites" : "Add to Favorites");
    QAction *exploreAct = menu.addAction("Show in File Explorer");
    menu.addSeparator();
    QAction *delAct = menu.addAction("Delete from Library");

    QAction *selected = menu.exec(m_bookGridList->viewport()->mapToGlobal(pos));
    if (selected == openAct) {
        openBookFile(b.filePath);
    } else if (selected == favAct) {
        DatabaseManager::instance().toggleFavorite(b.id, !b.isFavorite);
        refreshLibrary();
    } else if (selected == exploreAct) {
        QFileInfo fi(b.filePath);
        if (fi.exists()) {
            QDesktopServices::openUrl(QUrl::fromLocalFile(fi.absolutePath()));
        }
    } else if (selected == delAct) {
        auto res = QMessageBox::question(this, "Delete Book", QString("Remove \"%1\" from your library?").arg(b.title), QMessageBox::Yes | QMessageBox::No);
        if (res == QMessageBox::Yes) {
            DatabaseManager::instance().deleteBook(b.id);
            refreshLibrary();
        }
    }
}

void ReaderWindow::onBookTableContextMenu(const QPoint &pos) {
    int row = m_bookTableWidget->rowAt(pos.y());
    if (row < 0 || row >= m_currentBooks.size()) return;
    const BookRecord& b = m_currentBooks[row];

    QMenu menu(this);
    menu.setStyleSheet(R"(
        QMenu {
            background-color: #24201e;
            border: 1px solid #3d3835;
            border-radius: 6px;
            padding: 4px;
            color: #f5f5f4;
            font-size: 13px;
        }
        QMenu::item {
            padding: 6px 20px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: #c2410c;
            color: #ffffff;
        }
    )");

    QAction *openAct = menu.addAction("Read Book");
    QAction *favAct = menu.addAction(b.isFavorite ? "Remove from Favorites" : "Add to Favorites");
    QAction *exploreAct = menu.addAction("Show in File Explorer");
    menu.addSeparator();
    QAction *delAct = menu.addAction("Delete from Library");

    QAction *selected = menu.exec(m_bookTableWidget->viewport()->mapToGlobal(pos));
    if (selected == openAct) {
        openBookFile(b.filePath);
    } else if (selected == favAct) {
        DatabaseManager::instance().toggleFavorite(b.id, !b.isFavorite);
        refreshLibrary();
    } else if (selected == exploreAct) {
        QFileInfo fi(b.filePath);
        if (fi.exists()) {
            QDesktopServices::openUrl(QUrl::fromLocalFile(fi.absolutePath()));
        }
    } else if (selected == delAct) {
        auto res = QMessageBox::question(this, "Delete Book", QString("Remove \"%1\" from your library?").arg(b.title), QMessageBox::Yes | QMessageBox::No);
        if (res == QMessageBox::Yes) {
            DatabaseManager::instance().deleteBook(b.id);
            refreshLibrary();
        }
    }
}

void ReaderWindow::updateSidebarBadges() {
    if (!m_sidebarList) return;
    for (int i = 0; i < m_sidebarList->count(); ++i) {
        QListWidgetItem *it = m_sidebarList->item(i);
        QString key = it->data(Qt::UserRole).toString();
        if (key.isEmpty()) continue;
        int count = 0;
        if (key == "All Books") count = DatabaseManager::instance().getBooks().size();
        else if (key == "Favorites") count = DatabaseManager::instance().getBooks("", "Favorites").size();
        else if (key == "Currently Reading") count = DatabaseManager::instance().getBooks("", "Currently Reading").size();
        else if (key == "Completed") count = DatabaseManager::instance().getBooks("", "Completed").size();
        else if (key == "EPUB Documents") count = DatabaseManager::instance().getBooks("", "EPUB").size();
        else if (key == "PDF Documents") count = DatabaseManager::instance().getBooks("", "PDF").size();
        else if (key == "MOBI Ebooks") count = DatabaseManager::instance().getBooks("", "MOBI").size();
        else if (key == "TXT Files") count = DatabaseManager::instance().getBooks("", "TXT").size();
        else count = DatabaseManager::instance().getBooks("", key).size();

        it->setText(QString("%1 (%2)").arg(key).arg(count));
    }
}
