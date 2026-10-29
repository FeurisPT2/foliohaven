#ifndef READER_WINDOW_H
#define READER_WINDOW_H

#include <QMainWindow>
#include <QStackedWidget>
#include <QListWidget>
#include <QTableWidget>
#include <QLineEdit>
#include <QTextBrowser>
#include <QSlider>
#include <QLabel>
#include <QPushButton>
#include <QComboBox>
#include <QSplitter>
#include <QDockWidget>

#include "../storage/DatabaseManager.h"
#include "../engine/DocumentEngine.h"

enum class ReaderTheme {
    Day,
    Sepia,
    Night,
    DarkSepia
};

class ReaderWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit ReaderWindow(QWidget *parent = nullptr);
    ~ReaderWindow() override;

    void openBookFile(const QString& filePath);

protected:
    void dragEnterEvent(QDragEnterEvent *event) override;
    void dropEvent(QDropEvent *event) override;
    void keyPressEvent(QKeyEvent *event) override;

private slots:
    void onAddBookClicked();
    void onSearchLibraryChanged(const QString& text);
    void onCategorySelected(QListWidgetItem *item);
    void onBookDoubleClicked(QListWidgetItem *item);
    void onBookTableRowDoubleClicked(int row, int column);
    void onViewModeToggled(int modeIndex); // 0 = Grid, 1 = Table

    void onCloseReader();
    void onPrevPage();
    void onNextPage();
    void onSliderPageChanged(int value);
    void onThemeChanged(ReaderTheme theme);
    void onToggleTwoPages();
    void onZoomIn();
    void onZoomOut();
    void onToggleFullscreen();

    void onAddBookmark();
    void onToggleSearchDrawer();
    void onExecuteSearch();
    void onSearchHitSelected(QListWidgetItem *item);
    void onToggleNotesDrawer();
    void onAddHighlight();
    void onExportNotesHtml();
    void onToggleReadAloud();
    void onOpenSettingsDialog();

private:
    void setupUi();
    void setupLibraryView();
    void setupReaderView();
    void setupDrawers();
    void applyTheme(ReaderTheme theme);
    void refreshLibrary();
    void displayCurrentPage();
    void updateProgressDisplay();
    void saveCurrentProgress();

    // Data
    QVector<BookRecord> m_currentBooks;
    BookRecord m_activeBookRecord;
    LoadedBook m_loadedBook;
    int m_currentPageIndex{0};
    int m_fontSizePt{15};
    bool m_isTwoPages{false};
    ReaderTheme m_currentTheme{ReaderTheme::Sepia};
    QString m_activeCategory{"All Books"};
    bool m_isSpeaking{false};

    // UI Widgets - General
    QStackedWidget *m_stackWidget{nullptr};

    // UI Widgets - Library
    QWidget *m_libraryWidget{nullptr};
    QListWidget *m_sidebarList{nullptr};
    QLineEdit *m_searchLibraryEdit{nullptr};
    QListWidget *m_bookGridList{nullptr};
    QTableWidget *m_bookTableWidget{nullptr};
    QStackedWidget *m_viewModeStack{nullptr};
    QLabel *m_statusLabel{nullptr};

    // UI Widgets - Reader
    QWidget *m_readerViewWidget{nullptr};
    QLabel *m_readerTitleLabel{nullptr};
    QLabel *m_readerFormatBadge{nullptr};
    QPushButton *m_backBtn{nullptr};
    QTextBrowser *m_leftPageBrowser{nullptr};
    QTextBrowser *m_rightPageBrowser{nullptr};
    QSlider *m_pageSlider{nullptr};
    QLabel *m_pageIndicatorLabel{nullptr};
    QPushButton *m_prevBtn{nullptr};
    QPushButton *m_nextBtn{nullptr};
    QPushButton *m_themeDayBtn{nullptr};
    QPushButton *m_themeSepiaBtn{nullptr};
    QPushButton *m_themeNightBtn{nullptr};
    QPushButton *m_themeDarkSepiaBtn{nullptr};
    QPushButton *m_twoPagesBtn{nullptr};
    QPushButton *m_zoomOutBtn{nullptr};
    QPushButton *m_zoomInBtn{nullptr};
    QPushButton *m_searchBtn{nullptr};
    QPushButton *m_bookmarkBtn{nullptr};
    QPushButton *m_notesBtn{nullptr};
    QPushButton *m_speakBtn{nullptr};
    QPushButton *m_fsBtn{nullptr};
    QPushButton *m_readerSettingsBtn{nullptr};

    // UI Widgets - Library Controls
    QPushButton *m_addBookBtn{nullptr};
    QPushButton *m_viewGridBtn{nullptr};
    QPushButton *m_viewTableBtn{nullptr};
    QPushButton *m_settingsBtn{nullptr};

    // Helper functions
    void updateThemeButtons();
    void updateLayoutButton();
    void updateViewModeButtons(int modeIndex);
    void updateDrawerButtons();

    // Drawers
    QDockWidget *m_searchDock{nullptr};
    QLineEdit *m_inBookSearchEdit{nullptr};
    QListWidget *m_searchResultsList{nullptr};

    QDockWidget *m_notesDock{nullptr};
    QListWidget *m_bookmarksList{nullptr};
    QListWidget *m_annotationsList{nullptr};
};

#endif // READER_WINDOW_H
