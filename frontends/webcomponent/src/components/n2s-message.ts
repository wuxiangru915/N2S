import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { dell1996Tokens } from '../styles/dell1996-tokens.js';

@customElement('n2s-message')
export class N2sMessage extends LitElement {
  static styles = [
    dell1996Tokens,
    css`
      :host {
        display: block;
        padding: 0;
        margin-bottom: var(--n2s-space-4);
        font-family: var(--n2s-font-family-serif);
      }

      :host(:last-of-type) {
        margin-bottom: 0;
      }

      .message {
        border: 1px solid #000000;
        background: #ffffff;
        overflow: hidden;
        max-width: min(85%, 580px);
        line-height: 1.4;
      }

      .message.assistant {
        margin-right: auto;
      }

      .message.user {
        margin-left: auto;
      }

      .message-header {
        background: #ffffff;
        border-bottom: 1px solid #000000;
        padding: 4px 8px;
        font-family: Helvetica, Arial, sans-serif;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
      }

      .message-body {
        padding: 8px 12px;
      }

      .message.assistant .message-body {
        background: var(--dell-tint-sage);
      }

      .message.user .message-body {
        background: var(--dell-tint-peach);
      }

      .message-content {
        margin: 0;
        font-size: 14px;
        white-space: pre-wrap;
        overflow-wrap: break-word;
        word-break: break-word;
      }

      .message-content a {
        color: var(--dell-link);
        text-decoration: underline;
      }

      .message-content code {
        font-family: var(--n2s-font-family-mono);
        background: #ffffff;
        padding: 2px 4px;
        border: 1px solid #000000;
        font-size: 12px;
        display: inline-block;
        max-width: 100%;
        overflow-x: auto;
      }

      .message-timestamp {
        display: block;
        margin-top: 8px;
        font-family: Helvetica, Arial, sans-serif;
        font-size: 11px;
        color: #000000;
        opacity: 0.8;
      }

      @media (max-width: 600px) {
        .message {
          max-width: 100%;
        }
      }
    `
  ];

  @property() content = '';
  @property() type: 'user' | 'assistant' = 'user';
  @property({ type: Number }) timestamp = Date.now();
  @property({ reflect: true }) theme = 'light';
  @property({ reflect: true }) lang: 'zh' | 'en' = 'zh';

  private formatTimestamp(timestamp: number): string {
    return new Date(timestamp).toLocaleTimeString(this.lang === 'zh' ? 'zh-CN' : 'en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  render() {
    const labels = {
      zh: { user: '你', assistant: 'N2S 助手' },
      en: { user: 'You', assistant: 'N2S Agent' }
    };
    const label = labels[this.lang][this.type];
    return html`
      <div class="message ${this.type}">
        <div class="message-header">${label}</div>
        <div class="message-body">
          <div class="message-content">${this.content}</div>
          <div class="message-timestamp">
            ${this.formatTimestamp(this.timestamp)}
          </div>
        </div>
      </div>
    `;
  }
}
