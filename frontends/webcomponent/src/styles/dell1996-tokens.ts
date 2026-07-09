import { css } from 'lit';

// Dell 1996 catalog-era design tokens for N2S.
// These reuse the --n2s-* CSS custom property names from n2s-design-tokens.ts
// so components can be reskinned by simply importing this token set instead.
export const dell1996Tokens = css`
  :host {
    /* 1996 Brand Colors */
    --n2s-navy: rgb(0, 0, 0);
    --n2s-cream: rgb(255, 255, 255);
    --n2s-teal: rgb(0, 0, 0);
    --n2s-orange: rgb(233, 29, 42);
    --n2s-magenta: rgb(106, 38, 164);

    /* Surface / background */
    --n2s-background-root: rgb(255, 255, 255);
    --n2s-background-default: rgb(255, 255, 255);
    --n2s-background-higher: rgb(255, 255, 255);
    --n2s-background-highest: rgb(255, 255, 255);
    --n2s-background-subtle: rgb(255, 255, 255);
    --n2s-background-lower: rgb(255, 255, 255);

    /* Text */
    --n2s-foreground-default: rgb(0, 0, 0);
    --n2s-foreground-dimmer: rgb(0, 0, 0);
    --n2s-foreground-dimmest: rgb(0, 0, 0);

    /* Accents mapped to 1996 tints */
    --n2s-accent-primary-default: rgb(0, 0, 0);
    --n2s-accent-primary-stronger: rgb(0, 0, 0);
    --n2s-accent-primary-strongest: rgb(0, 0, 0);
    --n2s-accent-primary-subtle: rgb(255, 255, 255);
    --n2s-accent-primary-hover: rgb(0, 0, 0);

    --n2s-accent-positive-default: rgb(179, 189, 149);
    --n2s-accent-positive-stronger: rgb(142, 154, 108);
    --n2s-accent-positive-subtle: rgb(179, 189, 149);

    --n2s-accent-negative-default: rgb(215, 122, 122);
    --n2s-accent-negative-stronger: rgb(0, 0, 0);
    --n2s-accent-negative-subtle: rgb(215, 122, 122);

    --n2s-accent-warning-default: rgb(230, 145, 93);
    --n2s-accent-warning-stronger: rgb(0, 0, 0);
    --n2s-accent-warning-subtle: rgb(230, 145, 93);

    /* Borders */
    --n2s-outline-default: rgb(0, 0, 0);
    --n2s-outline-dimmer: rgb(0, 0, 0);
    --n2s-outline-dimmest: rgb(0, 0, 0);
    --n2s-outline-hover: rgb(0, 0, 0);

    /* Typography */
    --n2s-font-family-default: Helvetica, Arial, sans-serif;
    --n2s-font-family-serif: "Times New Roman", Times, serif;
    --n2s-font-family-mono: "Courier New", Courier, monospace;

    /* Spacing (4px base) */
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

    /* Border radius: everything square in 1996 */
    --n2s-border-radius-sm: 0px;
    --n2s-border-radius-md: 0px;
    --n2s-border-radius-lg: 0px;
    --n2s-border-radius-xl: 0px;
    --n2s-border-radius-2xl: 0px;
    --n2s-border-radius-full: 9999px;

    /* Shadows: none */
    --n2s-shadow-xs: none;
    --n2s-shadow-sm: none;
    --n2s-shadow-md: none;
    --n2s-shadow-lg: none;
    --n2s-shadow-xl: none;
    --n2s-shadow-2xl: none;

    /* Animation durations kept for functional transitions */
    --n2s-duration-75: 75ms;
    --n2s-duration-100: 100ms;
    --n2s-duration-150: 150ms;
    --n2s-duration-200: 200ms;
    --n2s-duration-300: 300ms;
    --n2s-duration-500: 500ms;
    --n2s-duration-700: 700ms;

    /* Z-index scale unchanged */
    --n2s-z-dropdown: 1000;
    --n2s-z-sticky: 1020;
    --n2s-z-fixed: 1030;
    --n2s-z-modal: 1040;
    --n2s-z-popover: 1050;
    --n2s-z-tooltip: 1060;

    /* Chat-specific tokens */
    --n2s-chat-bubble-radius: 0px;
    --n2s-chat-bubble-radius-sm: 0px;
    --n2s-chat-spacing: 16px;
    --n2s-chat-avatar-size: 40px;

    /* 1996-specific extra variables (not in original tokens) */
    --dell-primary: rgb(233, 29, 42);
    --dell-yellow: rgb(252, 194, 15);
    --dell-purple: rgb(106, 38, 164);
    --dell-link: rgb(0, 0, 238);
    --dell-tint-sage: rgb(179, 189, 149);
    --dell-tint-salmon: rgb(215, 122, 122);
    --dell-tint-peach: rgb(230, 145, 93);
    --dell-tint-lime: rgb(192, 212, 167);
    --dell-tint-sky: rgb(154, 182, 200);
    --dell-tint-steel: rgb(165, 184, 192);
    --dell-tint-periwinkle: rgb(140, 154, 224);
    --dell-tint-olive: rgb(142, 138, 37);
  }
`;
