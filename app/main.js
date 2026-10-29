/**
 * FolioHaven Desktop - Electron Main Process
 * Clean-room, native Windows application entry point.
 */

const { app, BrowserWindow, Menu, dialog, ipcMain, shell, nativeTheme } = require('electron');
const path = require('path');
const fs = require('fs');

// Force dark mode titlebar and UI controls on Windows
nativeTheme.themeSource = 'dark';

let mainWindow = null;

// Support book file extensions
const BOOK_EXTENSIONS = ['.epub', '.pdf', '.mobi', '.fb2', '.cbz', '.cbr', '.txt'];

function isBookFile(filePath) {
  if (!filePath || typeof filePath !== 'string') return false;
  const ext = path.extname(filePath).toLowerCase();
  return BOOK_EXTENSIONS.includes(ext);
}

function parseBookFromFile(filePath) {
  try {
    const stats = fs.statSync(filePath);
    const fileName = path.basename(filePath);
    const ext = path.extname(filePath).replace('.', '').toUpperCase();
    const title = path.basename(filePath, path.extname(filePath));

    let snippet = '';
    if (ext === 'TXT') {
      const buffer = Buffer.alloc(1024);
      const fd = fs.openSync(filePath, 'r');
      const bytesRead = fs.readSync(fd, buffer, 0, 1024, 0);
      fs.closeSync(fd);
      snippet = buffer.toString('utf8', 0, bytesRead);
    }

    return {
      title: title || 'Untitled Book',
      author: 'Local File',
      format: ext || 'EPUB',
      file_path: filePath,
      file_size_bytes: stats.size,
      total_pages: Math.max(1, Math.round(stats.size / 2048)),
      current_page: 1,
      progress_percent: 0,
      description: snippet ? snippet.slice(0, 300) : `Imported local ${ext} document.`,
      chapters: [
        {
          id: 'c1',
          title: title || 'Chapter 1',
          content: snippet || `Loaded ${fileName} from local storage (${Math.round(stats.size / 1024)} KB).`
        }
      ]
    };
  } catch (err) {
    console.error('Failed to parse file:', filePath, err);
    return null;
  }
}

function handleCommandLineArg(argv) {
  if (!argv || !Array.isArray(argv)) return null;
  for (const arg of argv) {
    if (isBookFile(arg) && fs.existsSync(arg)) {
      return parseBookFromFile(arg);
    }
  }
  return null;
}

// Single instance lock
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', (_event, commandLine) => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();

      const book = handleCommandLineArg(commandLine);
      if (book) {
        mainWindow.webContents.send('app:open-file-path', book);
      }
    }
  });

  app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
  });
}

function buildMenu() {
  const isMac = process.platform === 'darwin';

  const template = [
    {
      label: '&File',
      submenu: [
        {
          label: '&Open Book...',
          accelerator: 'CmdOrCtrl+O',
          click: async () => {
            const books = await openNativeFileDialog();
            if (books && books.length > 0 && mainWindow) {
              mainWindow.webContents.send('app:menu-action', { type: 'import-books', books });
            }
          }
        },
        {
          label: 'Add &Category...',
          accelerator: 'CmdOrCtrl+Shift+N',
          click: () => {
            if (mainWindow) mainWindow.webContents.send('app:menu-action', { type: 'add-category' });
          }
        },
        { type: 'separator' },
        {
          label: '&Export Reading Statistics...',
          click: () => {
            if (mainWindow) mainWindow.webContents.send('app:menu-action', { type: 'export-stats' });
          }
        },
        { type: 'separator' },
        {
          label: 'E&xit',
          accelerator: isMac ? 'Cmd+Q' : 'Alt+F4',
          click: () => app.quit()
        }
      ]
    },
    {
      label: '&Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' }
      ]
    },
    {
      label: '&View',
      submenu: [
        {
          label: '&Library View',
          accelerator: 'Esc',
          click: () => {
            if (mainWindow) mainWindow.webContents.send('app:menu-action', { type: 'close-reader' });
          }
        },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
        { type: 'separator' },
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' }
      ]
    },
    {
      label: '&Window',
      submenu: [
        { role: 'minimize' },
        { role: 'zoom' },
        ...(isMac ? [{ type: 'separator' }, { role: 'front' }] : [{ role: 'close' }])
      ]
    },
    {
      label: '&Help',
      submenu: [
        {
          label: 'FolioHaven &Help & Shortcuts',
          accelerator: 'F1',
          click: () => {
            if (mainWindow) mainWindow.webContents.send('app:menu-action', { type: 'open-help' });
          }
        },
        {
          label: 'Visit Official &Website',
          click: async () => {
            await shell.openExternal('https://foliohaven.vercel.app');
          }
        },
        { type: 'separator' },
        {
          label: '&About FolioHaven',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About FolioHaven',
              message: 'FolioHaven — Desktop Ebook Reader',
              detail: 'Version 1.0.1 (Windows x64 Standalone)\n\nA clean-room, distraction-free desktop digital bookshelf.\nSupports EPUB, PDF, MOBI, FB2, CBZ, and TXT.\n\n© 2026 FolioHaven Team. Released under the MIT License.',
              buttons: ['OK']
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

async function openNativeFileDialog() {
  if (!mainWindow) return [];
  const result = await dialog.showOpenDialog(mainWindow, {
    title: 'Import Books into FolioHaven',
    properties: ['openFile', 'multiSelections'],
    filters: [
      { name: 'Supported Ebooks (*.epub, *.pdf, *.mobi, *.fb2, *.cbz, *.txt)', extensions: ['epub', 'pdf', 'mobi', 'fb2', 'cbz', 'cbr', 'txt'] },
      { name: 'EPUB Ebooks (*.epub)', extensions: ['epub'] },
      { name: 'PDF Documents (*.pdf)', extensions: ['pdf'] },
      { name: 'MOBI Ebooks (*.mobi)', extensions: ['mobi'] },
      { name: 'FB2 FictionBook (*.fb2)', extensions: ['fb2'] },
      { name: 'Comic Archives (*.cbz, *.cbr)', extensions: ['cbz', 'cbr'] },
      { name: 'Text Documents (*.txt)', extensions: ['txt'] },
      { name: 'All Files (*.*)', extensions: ['*'] }
    ]
  });

  if (result.canceled || !result.filePaths || result.filePaths.length === 0) {
    return [];
  }

  const books = [];
  for (const filePath of result.filePaths) {
    const book = parseBookFromFile(filePath);
    if (book) books.push(book);
  }
  return books;
}

function createWindow() {
  const iconPath = path.join(__dirname, 'icon.ico');

  mainWindow = new BrowserWindow({
    width: 1280,
    height: 850,
    minWidth: 1024,
    minHeight: 700,
    backgroundColor: '#231f1d',
    title: 'FolioHaven — Distraction-Free Digital Bookshelf',
    icon: fs.existsSync(iconPath) ? iconPath : undefined,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });

  buildMenu();

  mainWindow.loadFile(path.join(__dirname, 'index.html'));

  mainWindow.webContents.on('did-finish-load', () => {
    // Check if initial book passed via CLI args
    const initialBook = handleCommandLineArg(process.argv.slice(1));
    if (initialBook) {
      mainWindow.webContents.send('app:open-file-path', initialBook);
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// IPC Handlers
ipcMain.handle('dialog:open-files', async () => {
  return await openNativeFileDialog();
});

ipcMain.handle('dialog:save-file', async (_event, { filename, content, type }) => {
  if (!mainWindow) return { canceled: true };
  const ext = filename.split('.').pop();
  const result = await dialog.showSaveDialog(mainWindow, {
    title: 'Export File',
    defaultPath: filename,
    filters: [
      { name: type || 'File', extensions: [ext || 'txt'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });

  if (result.canceled || !result.filePath) {
    return { canceled: true };
  }

  try {
    fs.writeFileSync(result.filePath, content, 'utf8');
    return { canceled: false, filePath: result.filePath };
  } catch (err) {
    return { error: err.message };
  }
});

ipcMain.handle('file:read-content', async (_event, filePath) => {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch (err) {
    throw err;
  }
});

ipcMain.handle('app:get-info', () => {
  return {
    version: '1.0.1',
    platform: process.platform,
    arch: process.arch,
    isDesktop: true
  };
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
