import { css } from 'lit';

// N2S design tokens - Data-First Agents branding
export const n2sDesignTokens = css`
  :host {
    /* N2S Brand Colors */
    --n2s-navy: rgb(26, 26, 46);
    --n2s-cream: rgb(240, 240, 245);
    --n2s-teal: rgb(0, 212, 255);
    --n2s-orange: rgb(255, 107, 107);
    --n2s-magenta: rgb(123, 44, 191);

    /* Color Palette - Light mode (default) */
    --n2s-background-root: rgb(255, 255, 255);
    --n2s-background-default: rgb(240, 240, 245);
    --n2s-background-higher: rgb(244, 246, 248);
    --n2s-background-highest: rgb(229, 231, 235);
    --n2s-background-subtle: rgb(248, 250, 252);
    --n2s-background-lower: rgb(239, 242, 245);

    --n2s-foreground-default: rgb(26, 26, 46);
    --n2s-foreground-dimmer: rgb(71, 85, 105);
    --n2s-foreground-dimmest: rgb(100, 116, 139);

    --n2s-accent-primary-default: rgb(0, 212, 255);
    --n2s-accent-primary-stronger: rgb(26, 26, 46);
    --n2s-accent-primary-strongest: rgb(26, 26, 46);
    --n2s-accent-primary-subtle: rgba(21, 168, 168, 0.1);
    --n2s-accent-primary-hover: rgb(0, 212, 255);

    --n2s-accent-positive-default: rgb(0, 212, 255);
    --n2s-accent-positive-stronger: rgb(26, 26, 46);
    --n2s-accent-positive-subtle: rgba(21, 168, 168, 0.1);

    --n2s-accent-negative-default: rgb(239, 68, 68);
    --n2s-accent-negative-stronger: rgb(220, 38, 38);
    --n2s-accent-negative-subtle: rgba(239, 68, 68, 0.1);

    --n2s-accent-warning-default: rgb(255, 107, 107);
    --n2s-accent-warning-stronger: rgb(255, 107, 107);
    --n2s-accent-warning-subtle: rgba(254, 93, 38, 0.1);

    /* Outline/Border colors */
    --n2s-outline-default: rgba(21, 168, 168, 0.3);
    --n2s-outline-dimmer: rgb(241, 245, 249);
    --n2s-outline-dimmest: rgb(248, 250, 252);
    --n2s-outline-hover: rgb(0, 212, 255);

    /* Typography */
    --n2s-font-family-default: "Space Grotesk", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
    --n2s-font-family-serif: "Roboto Slab", ui-serif, Georgia, serif;
    --n2s-font-family-mono: "Space Mono", ui-monospace, SFMono-Regular, "SF Mono", Monaco, Inconsolata, "Roboto Mono", "Ubuntu Mono", monospace;

    /* Spacing scale */
    --n2s-space-0: 0px;
    --n2s-space-1: 4px;
    --n2s-space-2: 8px;
    --n2s-space-3: 12px;
    --n2s-space-4: 16px;
    --n2s-space-5: 20px;
    --n2s-space-6: 24px;
    --n2s-space-7: 28px;
    --n2s-space-8: 32px;
    --n2s-space-10: 40px;
    --n2s-space-12: 48px;
    --n2s-space-16: 64px;

    /* Border radius */
    --n2s-border-radius-sm: 6px;
    --n2s-border-radius-md: 10px;
    --n2s-border-radius-lg: 14px;
    --n2s-border-radius-xl: 20px;
    --n2s-border-radius-2xl: 24px;
    --n2s-border-radius-full: 9999px;

    /* Shadows - Preline-inspired */
    --n2s-shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --n2s-shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
    --n2s-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
    --n2s-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
    --n2s-shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    --n2s-shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

    /* Animation durations */
    --n2s-duration-75: 75ms;
    --n2s-duration-100: 100ms;
    --n2s-duration-150: 150ms;
    --n2s-duration-200: 200ms;
    --n2s-duration-300: 300ms;
    --n2s-duration-500: 500ms;
    --n2s-duration-700: 700ms;

    /* Z-index scale */
    --n2s-z-dropdown: 1000;
    --n2s-z-sticky: 1020;
    --n2s-z-fixed: 1030;
    --n2s-z-modal: 1040;
    --n2s-z-popover: 1050;
    --n2s-z-tooltip: 1060;

    /* Chat-specific tokens */
    --n2s-chat-bubble-radius: 18px;
    --n2s-chat-bubble-radius-sm: 12px;
    --n2s-chat-spacing: 16px;
    --n2s-chat-avatar-size: 40px;
  }

  /* Dark theme overrides */
  :host([theme="dark"]) {
    --n2s-background-root: rgb(9, 11, 17);
    --n2s-background-default: rgb(15, 18, 25);
    --n2s-background-higher: rgb(24, 29, 39);
    --n2s-background-highest: rgb(31, 39, 51);
    --n2s-background-subtle: rgb(17, 21, 28);
    --n2s-background-lower: rgb(6, 8, 12);

    --n2s-foreground-default: rgb(248, 250, 252);
    --n2s-foreground-dimmer: rgb(203, 213, 225);
    --n2s-foreground-dimmest: rgb(148, 163, 184);

    --n2s-accent-primary-default: rgb(0, 212, 255);
    --n2s-accent-primary-stronger: rgb(0, 212, 255);
    --n2s-accent-primary-strongest: rgb(26, 26, 46);
    --n2s-accent-primary-subtle: rgba(21, 168, 168, 0.15);
    --n2s-accent-primary-hover: rgb(0, 212, 255);

    --n2s-accent-positive-default: rgb(0, 212, 255);
    --n2s-accent-positive-stronger: rgb(0, 212, 255);
    --n2s-accent-positive-subtle: rgba(21, 168, 168, 0.15);

    --n2s-accent-negative-default: rgb(248, 113, 113);
    --n2s-accent-negative-stronger: rgb(239, 68, 68);
    --n2s-accent-negative-subtle: rgba(248, 113, 113, 0.15);

    --n2s-accent-warning-default: rgb(255, 107, 107);
    --n2s-accent-warning-stronger: rgb(255, 107, 107);
    --n2s-accent-warning-subtle: rgba(254, 93, 38, 0.15);

    --n2s-outline-default: rgba(21, 168, 168, 0.3);
    --n2s-outline-dimmer: rgb(31, 41, 55);
    --n2s-outline-dimmest: rgb(17, 24, 39);
    --n2s-outline-hover: rgb(0, 212, 255);

    --n2s-shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.6);
    --n2s-shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.5), 0 1px 2px -1px rgba(0, 0, 0, 0.5);
    --n2s-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -2px rgba(0, 0, 0, 0.4);
    --n2s-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -4px rgba(0, 0, 0, 0.4);
    --n2s-shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
    --n2s-shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
  }
`;
