import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { dell1996Tokens } from '../styles/dell1996-tokens.js';

export interface CardAction {
  label: string;
  action: string;
  variant?: 'primary' | 'secondary';
}

@customElement('rich-card')
export class RichCard extends LitElement {
  static styles = [
    dell1996Tokens,
    css`
      :host {
        display: block;
        margin-bottom: var(--n2s-space-4);
        font-family: var(--n2s-font-family-serif);
      }

      .card {
        border: 1px solid #000000;
        border-radius: 0;
        background: #ffffff;
        box-shadow: none;
        overflow: hidden;
      }

      .card-header {
        display: flex;
        align-items: center;
        padding: 6px 12px;
        background: #ffffff;
        border-bottom: 1px solid #000000;
        gap: var(--n2s-space-3);
      }

      .card-header.collapsible {
        cursor: pointer;
      }

      .card-icon {
        font-size: 1.25rem;
        display: flex;
        align-items: center;
      }

      .card-title-section {
        flex: 1;
      }

      .card-title {
        margin: 0;
        font-family: Helvetica, Arial, sans-serif;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        color: #000000;
      }

      .card-subtitle {
        margin: 4px 0 0 0;
        font-size: 12px;
        color: #000000;
        opacity: 0.8;
      }

      .card-status {
        padding: 2px 6px;
        border: 1px solid #000000;
        font-family: Helvetica, Arial, sans-serif;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        background: #ffffff;
        color: #000000;
      }

      .card-status.status-success {
        background: var(--dell-tint-sage);
      }

      .card-status.status-warning {
        background: var(--dell-tint-peach);
      }

      .card-status.status-error {
        background: var(--dell-tint-salmon);
      }

      .card-status.status-info {
        background: var(--dell-tint-sky);
      }

      .card-toggle {
        background: none;
        border: 1px solid #000000;
        cursor: pointer;
        font-size: 12px;
        color: #000000;
        padding: 2px 6px;
      }

      .card-content {
        padding: 12px 16px;
        line-height: 1.4;
        color: #000000;
        background: #ffffff;
      }

      .card-content.collapsed {
        display: none;
      }

      .card-content h1,
      .card-content h2,
      .card-content h3 {
        margin: 8px 0;
        font-family: Helvetica, Arial, sans-serif;
        font-weight: 700;
        text-transform: uppercase;
      }

      .card-content h1 { font-size: 18px; }
      .card-content h2 { font-size: 16px; }
      .card-content h3 { font-size: 14px; }

      .card-content p {
        margin: 8px 0;
      }

      .card-content ul {
        margin: 8px 0;
        padding-left: 20px;
      }

      .card-content li {
        margin: 4px 0;
      }

      .card-content code {
        background: #ffffff;
        padding: 2px 4px;
        border: 1px solid #000000;
        font-family: var(--n2s-font-family-mono);
        font-size: 12px;
      }

      .card-content strong {
        font-weight: 700;
      }

      .card-actions {
        padding: 8px 12px;
        background: #ffffff;
        border-top: 1px solid #000000;
        display: flex;
        gap: var(--n2s-space-2);
      }

      .card-action {
        padding: 4px 12px;
        border: 1px solid #000000;
        background: #ffffff;
        color: #000000;
        cursor: pointer;
        font-family: Helvetica, Arial, sans-serif;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
      }

      .card-action:hover {
        background: #000000;
        color: #ffffff;
      }

      .card-action.primary {
        background: #000000;
        color: #ffffff;
      }

      .card-action.primary:hover {
        background: #ffffff;
        color: #000000;
      }
    `
  ];

  @property() title = '';
  @property() subtitle = '';
  @property() content = '';
  @property() icon = '';
  @property() status: 'info' | 'success' | 'warning' | 'error' = 'info';
  @property({ type: Array }) actions: CardAction[] = [];
  @property({ type: Boolean }) collapsible = false;
  @property({ type: Boolean }) collapsed = false;
  @property({ type: Boolean }) markdown = false;
  @property() theme: 'light' | 'dark' = 'dark';

  private _toggleCollapsed() {
    if (this.collapsible) {
      this.collapsed = !this.collapsed;
    }
  }

  private _renderMarkdown(text: string): string {
    return text
      .replace(/^### (.*$)/gm, '<h3>$1</h3>')
      .replace(/^## (.*$)/gm, '<h2>$1</h2>')
      .replace(/^# (.*$)/gm, '<h1>$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/^- (.*$)/gm, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/^(?!<[h|u|l|p])(.+)$/gm, '<p>$1</p>');
  }

  render() {
    const contentHtml = this.markdown
      ? html`<div class="card-content ${this.collapsed ? 'collapsed' : ''}" .innerHTML=${this._renderMarkdown(this.content)}></div>`
      : html`<div class="card-content ${this.collapsed ? 'collapsed' : ''}">${this.content}</div>`;

    return html`
      <div class="card">
        <div class="card-header ${this.collapsible ? 'collapsible' : ''}"
             @click=${this._toggleCollapsed}>
          ${this.icon ? html`<span class="card-icon">${this.icon}</span>` : ''}
          <div class="card-title-section">
            <h3 class="card-title">${this.title}</h3>
            ${this.subtitle ? html`<p class="card-subtitle">${this.subtitle}</p>` : ''}
          </div>
          ${this.status ? html`<span class="card-status status-${this.status}">${this.status}</span>` : ''}
          ${this.collapsible ? html`
            <button class="card-toggle">${this.collapsed ? '▶' : '▼'}</button>
          ` : ''}
        </div>
        ${contentHtml}
        ${this.actions.length > 0 ? html`
          <div class="card-actions">
            ${this.actions.map(action => html`
              <button class="card-action ${action.variant || 'secondary'}"
                      @click=${() => this._handleAction(action.action)}>
                ${action.label}
              </button>
            `)}
          </div>
        ` : ''}
      </div>
    `;
  }

  private async _handleAction(action: string) {
    console.log('🔘 Card action button clicked (rich-card)');
    console.log('   Action:', action);

    this.dispatchEvent(new CustomEvent('card-action', {
      detail: { action },
      bubbles: true,
      composed: true
    }));

    const n2sChat = document.querySelector('n2s-chat') as any;
    if (n2sChat && typeof n2sChat.sendMessage === 'function') {
      console.log('   Found n2s-chat, sending message...');
      try {
        const success = await n2sChat.sendMessage(action);
        if (success) {
          console.log('   ✅ Action sent successfully');
        } else {
          console.error('   ❌ Failed to send action');
        }
      } catch (error) {
        console.error('   ❌ Error sending action:', error);
      }
    } else {
      console.warn('   ⚠️ n2s-chat component not found or sendMessage not available');
    }
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'rich-card': RichCard;
  }
}
