# FolioHaven (Web Portal & Web Reader)

<p align="center">
  <img src="app/assets/branding/app_logo_512.png" alt="FolioHaven Master Logo" width="108" height="108" style="border-radius: 24px;" />
</p>

<p align="center">
  <strong>Serene Digital Bookshelf & Distraction-Free Ebook Reader — Web Platform</strong><br>
  Official marketing portal, web reading application, and central home for the FolioHaven literary ecosystem.
</p>

<p align="center">
  <a href="https://foliohaven.vercel.app"><img src="https://img.shields.io/badge/Live%20Deploy-Vercel-black?style=flat-square&logo=vercel" alt="Vercel Deployment" /></a>
  <a href="https://github.com/FeurisPT2/Foliohaven-pc"><img src="https://img.shields.io/badge/PC%20Client-Flutter-blue?style=flat-square&logo=flutter" alt="PC Client" /></a>
  <a href="https://github.com/FeurisPT2/foliohaven-mobile"><img src="https://img.shields.io/badge/Mobile%20App-Android%20Compose-green?style=flat-square&logo=android" alt="Mobile App" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-orange?style=flat-square" alt="MIT License" /></a>
</p>

---

## 🏛️ FolioHaven Ecosystem Overview

The FolioHaven project is organized across three dedicated, platform-optimized repositories:

| Project | Platform / Technology | Purpose | Repository Link |
| :--- | :--- | :--- | :--- |
| **🌐 FolioHaven Web (This Repo)** | HTML5, Canvas &amp; Vanilla Web APIs | Official marketing portal &amp; instant zero-install browser reader deployed to Vercel | [FeurisPT2/foliohaven](https://github.com/FeurisPT2/foliohaven) |
| **💻 FolioHaven PC** | Dart &amp; Flutter | High-performance native desktop client for Windows, Linux, and macOS | [FeurisPT2/Foliohaven-pc](https://github.com/FeurisPT2/Foliohaven-pc) |
| **📱 FolioHaven Mobile** | Kotlin &amp; Jetpack Compose | Native Android application with edge-to-edge Material 3 design and offline reader | [FeurisPT2/foliohaven-mobile](https://github.com/FeurisPT2/foliohaven-mobile) |

---

## 🌟 What is FolioHaven?

**FolioHaven** is a privacy-first, distraction-free ebook sanctuary designed for bibliophiles, students, and researchers who value quiet study and typographic craftsmanship.

Unlike mainstream reading apps that push invasive subscriptions, artificial library limits, or telemetry trackers, FolioHaven runs 100% offline and stores your library locally:

- 🔒 **100% Local & Private:** No user accounts, zero trackers, and zero cloud lock-ins. All books, bookmarks, and study notes remain strictly on your device.
- 📖 **Universal Format Support:** Reflowable **EPUB**, fixed-layout **PDF**, **MOBI**, **FB2**, **CBZ** comic archives, and plain **TXT**.
- 🎨 **Master 2D Identity:** Unified design tokens, rich terracotta palette (`#C2410C`), archival embossed book covers, and WCAG AAA-compliant reading modes.
- ⚡ **Zero-Install Web Reader:** Drag and drop books directly into the browser canvas for instant reading without installing software.

---

## 🚀 Live Access & Deployment

| Resource | URL | Description |
| :--- | :--- | :--- |
| **Marketing Landing Portal** | [foliohaven.vercel.app](https://foliohaven.vercel.app/) | Interactive feature showcase, design philosophy, and platform downloads |
| **In-Browser Web Reader** | [foliohaven.vercel.app/reader](https://foliohaven.vercel.app/reader) | Full client-side IndexedDB ebook reader running in any modern browser |
| **PC Desktop Releases** | [github.com/FeurisPT2/Foliohaven-pc](https://github.com/FeurisPT2/Foliohaven-pc) | Flutter Windows installer, portable zip, and desktop binaries |
| **Mobile Android Releases** | [github.com/FeurisPT2/foliohaven-mobile](https://github.com/FeurisPT2/foliohaven-mobile) | Android Compose APK and mobile updates |

---

## 🏗️ Web Architecture & Deployment to Vercel

The web application is pure static Web Standards with zero server-side build steps:

```
foliohaven/
├── app/
│   ├── assets/
│   │   ├── branding/         # Master 2D FH monogram logos (SVG & PNG)
│   │   └── credits.json      # Fine art attribution records (CC0)
│   ├── app.js                # Web UI controller, library views & keyboard shortcuts
│   ├── db.js                 # IndexedDB client-side local database
│   ├── engine.js             # Client-side ebook parser (EPUB/PDF/TXT/etc.)
│   ├── favicon.svg           # Master FH monogram browser favicon
│   ├── icon.png              # App icon
│   ├── index.html            # Web reading application interface (/reader)
│   ├── landing.html          # Main landing portal page (/)
│   ├── styles.css            # Component styles & typography
│   └── vercel.json           # Vercel route rewrites & headers
├── vercel.json               # Platform root routing configuration
└── README.md
```

### Deploying to Vercel

Deploy instantly with the Vercel CLI:

```bash
# Deploy to preview
vercel

# Deploy directly to production
vercel --prod
```

Or connect the repository to your Vercel Dashboard with Root Directory set to `./` or `app`. The provided `vercel.json` configurations automatically route:
- `/` $\rightarrow$ `landing.html`
- `/reader` or `/app` $\rightarrow$ `index.html`

---

## 🎨 Asset & Artwork Attribution

The archival aesthetic of FolioHaven incorporates public domain fine art courtesy of the **Art Institute of Chicago** (CC0 Public Domain Designation):
- *Interrupted Reading* (c. 1870) — Jean-Baptiste-Camille Corot
- *French Library of the Louis XV Period* (c. 1937) — Mrs. James Ward Thorne

Formal provenance and licensing records are documented in [`app/assets/credits.json`](app/assets/credits.json).

---

## 📄 License

Distributed under the terms of the **[MIT License](LICENSE)**.
