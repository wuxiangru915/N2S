import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { dell1996Tokens } from '../styles/dell1996-tokens.js';

@customElement('rich-progress-bar')
export class RichProgressBar extends LitElement {
  static styles = [
    dell1996Tokens,
    css`
      :host {
        display: block;
        margin-bottom: var(--n2s-space-4);
        font-family: var(--n2s-font-family-serif);
      }

      .progress-container {
        padding: 12px 16px;
        border: 1px solid #000000;
        border-radius: 0;
        background: #ffffff;
        box-shadow: none;
      }

      .progress-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--n2s-space-3);
      }

      .progress-label {
        font-family: Helvetica, Arial, sans-serif;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        color: #000000;
      }

      .progress-percentage {
        font-size: 12px;
        color: #000000;
        font-weight: 700;
      }

      .progress-track {
        height: 12px;
        background: #ffffff;
        border: 1px solid #000000;
        overflow: hidden;
        position: relative;
      }

      .progress-fill {
        height: 100%;
        background: #000000;
        transition: width var(--n2s-duration-300) ease;
        position: relative;
        overflow: hidden;
      }

      .progress-fill.status-success {
        background: var(--dell-tint-sage);
      }

      .progress-fill.status-warning {
        background: var(--dell-tint-peach);
      }

      .progress-fill.status-error {
        background: var(--dell-tint-salmon);
      }

      .progress-fill.status-info {
        background: #000000;
      }

      .progress-fill.indeterminate {
        background: repeating-linear-gradient(
          90deg,
          #000000 0,
          #000000 25%,
          #ffffff 25%,
          #ffffff 50%,
          #000000 50%,
          #000000 75%,
          #ffffff 75%,
          #ffffff 100%
        );
        background-size: 40px 100%;
        animation: indeterminateProgress 1s linear infinite;
        width: 100% !important;
      }

      @keyframes indeterminateProgress {
        0% { background-position: 0 0; }
        100% { background-position: 40px 0; }
      }

      .progress-description {
        margin-top: var(--n2s-space-2);
        font-size: 12px;
        color: #000000;
        line-height: 1.4;
        opacity: 0.8;
      }
    `
  ];

  @property({ type: Number }) value = 0;
  @property() label = '';
  @property() description = '';
  @property({ type: Boolean }) showPercentage = true;
  @property() status: 'info' | 'success' | 'warning' | 'error' = 'info';
  @property({ type: Boolean }) animated = false;
  @property({ type: Boolean }) indeterminate = false;
  @property() theme: 'light' | 'dark' = 'dark';

  private get percentage(): number {
    if (this.indeterminate) return 100;
    return Math.round(Math.max(0, Math.min(1, this.value)) * 100);
  }

  private get progressClasses(): string {
    const classes = ['progress-fill'];

    if (this.indeterminate) {
      classes.push('indeterminate');
    }

    if (this.status) {
      classes.push(`status-${this.status}`);
    }

    return classes.join(' ');
  }

  render() {
    return html`
      <div class="progress-container">
        ${this.label || this.showPercentage ? html`
          <div class="progress-header">
            ${this.label ? html`<span class="progress-label">${this.label}</span>` : ''}
            ${this.showPercentage && !this.indeterminate ? html`
              <span class="progress-percentage">${this.percentage}%</span>
            ` : ''}
          </div>
        ` : ''}

        <div class="progress-track">
          <div
            class="${this.progressClasses}"
            style="width: ${this.indeterminate ? '100' : this.percentage}%">
          </div>
        </div>

        ${this.description ? html`
          <div class="progress-description">${this.description}</div>
        ` : ''}
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'rich-progress-bar': RichProgressBar;
  }
}
