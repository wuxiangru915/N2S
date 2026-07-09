import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { dell1996Tokens } from '../styles/dell1996-tokens.js';

@customElement('n2s-status-bar')
export class N2sStatusBar extends LitElement {
  static styles = [
    dell1996Tokens,
    css`
      :host {
        display: block;
        background: #ffffff;
        border: 1px solid #000000;
        border-radius: 0;
        padding: var(--n2s-space-3) var(--n2s-space-4);
        margin-bottom: var(--n2s-space-3);
        font-family: var(--n2s-font-family-serif);
        font-size: 14px;
        color: #000000;
      }

      :host(.no-content) {
        display: none;
      }

      :host([status="working"]) {
        background: #ffffff;
        border: 1px solid #000000;
      }

      :host([status="error"]) {
        background: var(--dell-tint-salmon);
        border: 1px solid #000000;
      }

      :host([status="success"]) {
        background: var(--dell-tint-lime);
        border: 1px solid #000000;
      }

      .status-content {
        display: flex;
        align-items: center;
        gap: var(--n2s-space-3);
      }

      .status-indicator {
        width: 12px;
        height: 12px;
        background: #000000;
        flex-shrink: 0;
      }

      .status-indicator.working {
        background: #000000;
        animation: none;
      }

      .status-indicator.error {
        background: var(--dell-primary);
      }

      .status-indicator.success {
        background: var(--dell-tint-sage);
      }

      .spinner {
        width: 12px;
        height: 12px;
        border: 2px solid #000000;
        border-top-color: transparent;
        animation: spin 1s linear infinite;
        flex-shrink: 0;
      }

      .status-text {
        flex: 1;
        font-weight: 400;
        line-height: 1.4;
      }

      .status-detail {
        font-size: 12px;
        margin-left: var(--n2s-space-4);
        color: #000000;
        opacity: 0.8;
      }

      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    `
  ];

  @property() status: 'idle' | 'working' | 'error' | 'success' = 'idle';
  @property() message = '';
  @property() detail = '';
  @property() theme = 'light';

  private _previousHasContent = false;
  private _enterTimeout: number | null = null;
  private _exitTimeout: number | null = null;
  private _lastUpdateTime = 0;

  disconnectedCallback() {
    super.disconnectedCallback();

    if (this._enterTimeout !== null) {
      clearTimeout(this._enterTimeout);
      this._enterTimeout = null;
    }
    if (this._exitTimeout !== null) {
      clearTimeout(this._exitTimeout);
      this._exitTimeout = null;
    }
  }

  updated(_changedProperties: Map<string | number | symbol, unknown>) {
    const hasContent = Boolean(this.message && this.message.trim());

    if (this._enterTimeout !== null) {
      clearTimeout(this._enterTimeout);
      this._enterTimeout = null;
    }
    if (this._exitTimeout !== null) {
      clearTimeout(this._exitTimeout);
      this._exitTimeout = null;
    }

    const now = Date.now();
    const timeSinceLastUpdate = now - this._lastUpdateTime;
    const shouldDebounce = timeSinceLastUpdate < 100;

    if (hasContent !== this._previousHasContent) {
      if (hasContent) {
        this.classList.remove('no-content', 'exiting');
        if (!shouldDebounce) {
          this.classList.add('entering');
          this._enterTimeout = window.setTimeout(() => {
            this.classList.remove('entering');
            this._enterTimeout = null;
          }, 300);
        }
      } else {
        this.classList.remove('entering');
        if (!shouldDebounce) {
          this.classList.add('exiting');
          this._exitTimeout = window.setTimeout(() => {
            this.classList.remove('exiting');
            this.classList.add('no-content');
            this._exitTimeout = null;
          }, 300);
        } else {
          this.classList.add('no-content');
        }
      }
    } else if (!hasContent) {
      this.classList.add('no-content');
    }

    this._previousHasContent = hasContent;
    this._lastUpdateTime = now;
  }

  render() {
    if (!this.message || !this.message.trim()) {
      return html``;
    }

    return html`
      <div class="status-content">
        ${this.status === 'working'
          ? html`<div class="spinner"></div>`
          : html`<div class="status-indicator ${this.status}"></div>`
        }
        <span class="status-text">${this.message}</span>
        ${this.detail ? html`<span class="status-detail">${this.detail}</span>` : ''}
      </div>
    `;
  }
}
