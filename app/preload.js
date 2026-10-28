/**
 * FolioHaven Desktop - Electron Preload Script
 * Exposes secure bridge between main process and renderer.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  isDesktop: true,
  platform: 'win32',
  version: '1.0.0',

  // Open native file dialog
  openFileDialog: () => ipcRenderer.invoke('dialog:open-files'),

  // Save exported data to disk
  saveFileDialog: (filename, content, type) => 
    ipcRenderer.invoke('dialog:save-file', { filename, content, type }),

  // Read file from disk
  readFile: (filePath) => ipcRenderer.invoke('file:read-content', filePath),

  // Get application info
  getAppInfo: () => ipcRenderer.invoke('app:get-info'),

  // Listen to file opened via CLI / double click / second instance
  onOpenFile: (callback) => {
    ipcRenderer.on('app:open-file-path', (_event, fileData) => callback(fileData));
  },

  // Listen to application menu shortcuts
  onMenuAction: (callback) => {
    ipcRenderer.on('app:menu-action', (_event, action) => callback(action));
  }
});
