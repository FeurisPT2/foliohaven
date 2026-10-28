const { app, BrowserWindow } = require('electron');
const fs = require('fs');
const path = require('path');

app.whenReady().then(async () => {
  try {
    const win = new BrowserWindow({
      width: 256,
      height: 256,
      show: false,
      frame: false,
      transparent: true,
      webPreferences: { offscreen: true }
    });

    const svgPath = path.resolve(__dirname, 'app', 'favicon.svg');
    const svgContent = fs.readFileSync(svgPath, 'utf8');
    const html = `<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { width: 256px; height: 256px; overflow: hidden; background: transparent; display: flex; align-items: center; justify-content: center; }
  svg { width: 256px; height: 256px; }
</style>
</head>
<body>
  ${svgContent}
</body>
</html>`;

    await win.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
    // Wait for render
    await new Promise(r => setTimeout(r, 600));

    // Capture multiple sizes: 256, 128, 64, 48, 32, 16
    const sizes = [256, 128, 64, 48, 32, 16];
    const pngBuffers = [];

    for (const size of sizes) {
      win.setSize(size, size);
      await new Promise(r => setTimeout(r, 200));
      const image = await win.webContents.capturePage({ x: 0, y: 0, width: size, height: size });
      const pngBuf = image.toPNG();
      pngBuffers.push({ size, buffer: pngBuf });
      if (size === 256) {
        fs.writeFileSync(path.resolve(__dirname, 'app', 'icon.png'), pngBuf);
      }
    }

    // Build standard multi-resolution ICO file
    // ICO Header: 2 bytes reserved (0), 2 bytes type (1 = ICO), 2 bytes count
    const count = pngBuffers.length;
    const header = Buffer.alloc(6);
    header.writeUInt16LE(0, 0);
    header.writeUInt16LE(1, 2);
    header.writeUInt16LE(count, 4);

    let offset = 6 + count * 16;
    const directoryEntries = [];

    for (const item of pngBuffers) {
      const entry = Buffer.alloc(16);
      const s = item.size >= 256 ? 0 : item.size;
      entry.writeUInt8(s, 0); // width
      entry.writeUInt8(s, 1); // height
      entry.writeUInt8(0, 2); // colors
      entry.writeUInt8(0, 3); // reserved
      entry.writeUInt16LE(1, 4); // color planes
      entry.writeUInt16LE(32, 6); // bits per pixel
      entry.writeUInt32LE(item.buffer.length, 8); // image size in bytes
      entry.writeUInt32LE(offset, 12); // offset in file
      directoryEntries.push(entry);
      offset += item.buffer.length;
    }

    const icoBuffer = Buffer.concat([
      header,
      ...directoryEntries,
      ...pngBuffers.map(b => b.buffer)
    ]);

    fs.writeFileSync(path.resolve(__dirname, 'app', 'icon.ico'), icoBuffer);
    console.log('Successfully created app/icon.png and app/icon.ico with sizes:', sizes);
  } catch (err) {
    console.error('Error generating icons:', err);
  } finally {
    app.quit();
  }
});
