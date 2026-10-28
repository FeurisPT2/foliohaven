/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class', '[data-theme="dark"]'],
  content: [
    './src/**/*.{html,js,ts,jsx,tsx,qml}',
    './replica/**/*.{html,md}'
  ],
  theme: {
    extend: {
      colors: {
        bg: 'var(--color-bg)',
        surface: {
          DEFAULT: 'var(--color-surface)',
          hover: 'var(--color-surface-hover)',
          active: 'var(--color-surface-active)'
        },
        border: {
          DEFAULT: 'var(--color-border)',
          input: 'var(--color-border-input)'
        },
        text: {
          DEFAULT: 'var(--color-text)',
          muted: 'var(--color-text-muted)'
        },
        accent: {
          DEFAULT: 'var(--color-accent)',
          hover: 'var(--color-accent-hover)'
        },
        'on-accent': 'var(--color-on-accent)',
        danger: 'var(--color-danger)',
        success: 'var(--color-success)',
        warning: 'var(--color-warning)',

        sidebar: {
          bg: 'var(--color-sidebar-bg)',
          surface: 'var(--color-sidebar-surface)',
          text: 'var(--color-sidebar-text)',
          'text-muted': 'var(--color-sidebar-text-muted)',
          border: 'var(--color-sidebar-border)'
        },

        highlight: {
          yellow: 'var(--color-highlight-yellow)',
          green: 'var(--color-highlight-green)',
          cyan: 'var(--color-highlight-cyan)',
          pink: 'var(--color-highlight-pink)'
        },

        reader: {
          bg: 'var(--reader-bg)',
          text: 'var(--reader-text)',
          surface: 'var(--reader-surface)',
          border: 'var(--reader-border)',
          gutter: 'var(--reader-gutter)'
        }
      },
      fontFamily: {
        sans: ['"Segoe UI"', '-apple-system', 'BlinkMacSystemFont', '"Inter"', '"Roboto"', 'sans-serif'],
        serif: ['"Georgia"', '"Charter"', '"Source Serif Pro"', '"Times New Roman"', 'serif'],
        mono: ['"Consolas"', '"ui-monospace"', '"SFMono-Regular"', '"Menlo"', 'monospace']
      },
      fontSize: {
        xs: ['12px', { lineHeight: '16px', fontWeight: '500' }],
        sm: ['13px', { lineHeight: '18px', fontWeight: '400' }],
        base: ['14px', { lineHeight: '20px', fontWeight: '400' }],
        md: ['16px', { lineHeight: '24px', fontWeight: '400' }],
        lg: ['18px', { lineHeight: '26px', fontWeight: '600' }],
        xl: ['22px', { lineHeight: '28px', fontWeight: '700' }],
        display: ['28px', { lineHeight: '34px', fontWeight: '700' }]
      },
      spacing: {
        '0.5': '2px',
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px',
        '10': '40px',
        '12': '48px',
        '16': '64px',
        'sidebar': '220px',
        'action-bar': '56px',
        'footer': '48px',
        'drawer': '340px'
      },
      borderRadius: {
        xs: '3px',
        sm: '5px',
        md: '8px',
        lg: '12px',
        pill: '9999px'
      },
      boxShadow: {
        card: '0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04)',
        'card-hover': '0 4px 12px rgba(0, 0, 0, 0.12), 0 2px 4px rgba(0, 0, 0, 0.06)',
        popover: '0 8px 24px rgba(0, 0, 0, 0.15), 0 2px 6px rgba(0, 0, 0, 0.08)',
        dialog: '0 16px 40px rgba(0, 0, 0, 0.22)'
      },
      transitionDuration: {
        fast: '120ms',
        base: '200ms',
        drawer: '260ms'
      },
      transitionTimingFunction: {
        base: 'cubic-bezier(0.2, 0.8, 0.2, 1)',
        drawer: 'cubic-bezier(0.16, 1, 0.3, 1)'
      }
    }
  },
  plugins: []
};
