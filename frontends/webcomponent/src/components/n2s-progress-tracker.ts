import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { dell1996Tokens } from '../styles/dell1996-tokens.js';

interface ProgressItem {
  id: string;
  text: string;
  status: 'pending' | 'in_progress' | 'completed' | 'error';
  detail?: string;
}

@customElement('n2s-progress-tracker')
export class N2sProgressTracker extends LitElement {
  static styles = [
    dell1996Tokens,
    css`
      :host {
        display: block;
        background: #ffffff;
        border-left: 1px solid #000000;
        border-right: 1px solid #000000;
        border-bottom: 1px solid #000000;
        overflow: hidden;
        font-family: var(--n2s-font-family-serif);
      }

      .progress-label {
        padding: 8px 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #000000;
        background: #ffffff;
      }

      .progress-label-text {
        font-family: Helvetica, Arial, sans-serif;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        margin: 0;
      }

      .progress-summary {
        font-size: 12px;
        color: #000000;
      }

      .progress-list {
        max-height: 300px;
        overflow-y: auto;
      }

      .progress-item {
        padding: 8px 12px;
        border-bottom: 1px solid #000000;
        display: flex;
        align-items: flex-start;
        gap: var(--n2s-space-3);
      }

      .progress-item:last-child {
        border-bottom: none;
      }

      .progress-item.in_progress {
        background: var(--dell-tint-sky);
      }

      .progress-item.completed {
        background: var(--dell-tint-sage);
      }

      .progress-item.error {
        background: var(--dell-tint-salmon);
      }

      .progress-icon {
        width: 16px;
        height: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        margin-top: 1px;
      }

      .progress-icon.pending {
        background: #ffffff;
        border: 1px solid #000000;
      }

      .progress-icon.in_progress {
        background: #000000;
      }

      .progress-icon.completed {
        background: #000000;
        color: #ffffff;
      }

      .progress-icon.error {
        background: var(--dell-primary);
        color: #ffffff;
      }

      .progress-icon svg {
        width: 10px;
        height: 10px;
        color: white;
      }

      .spinner-mini {
        width: 10px;
        height: 10px;
        border: 1.5px solid #ffffff;
        border-top-color: transparent;
        animation: spin 1s linear infinite;
      }

      .progress-content {
        flex: 1;
        min-width: 0;
      }

      .progress-text {
        font-size: 14px;
        color: #000000;
        margin: 0 0 4px 0;
        line-height: 1.3;
      }

      .progress-detail {
        font-size: 12px;
        color: #000000;
        margin: 0;
        line-height: 1.3;
        opacity: 0.8;
      }

      .empty-state {
        padding: var(--n2s-space-6) var(--n2s-space-4);
        text-align: center;
        color: #000000;
        font-size: 12px;
      }

      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    `
  ];

  @property() title = 'Progress';
  @property() theme = 'light';
  @property({ reflect: true }) lang: 'zh' | 'en' = 'zh';
  @state() private items: ProgressItem[] = [];

  addItem(text: string, detail?: string, id?: string): string {
    const itemId = id || Date.now().toString();
    this.items = [...this.items, {
      id: itemId,
      text,
      status: 'pending',
      detail
    }];
    return itemId;
  }

  updateItem(id: string, status: ProgressItem['status'], detail?: string) {
    this.items = this.items.map(item =>
      item.id === id ? { ...item, status, detail } : item
    );
  }

  clearItems() {
    this.items = [];
  }

  private getStatusIcon(status: ProgressItem['status']) {
    switch (status) {
      case 'pending':
        return html``;
      case 'in_progress':
        return html`<div class="spinner-mini"></div>`;
      case 'completed':
        return html`
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
        `;
      case 'error':
        return html`
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        `;
    }
  }

  private getProgressSummary(completedLabel: string = 'completed') {
    const completed = this.items.filter(item => item.status === 'completed').length;
    const total = this.items.length;
    const inProgress = this.items.filter(item => item.status === 'in_progress').length;

    if (inProgress > 0) {
      return `${completed}/${total} ${completedLabel}`;
    }
    return total > 0 ? `${completed}/${total} ${completedLabel}` : '';
  }

  render() {
    const labels = {
      zh: { tasks: '任务', completed: '已完成', noTasks: '暂无任务' },
      en: { tasks: 'Tasks', completed: 'completed', noTasks: 'No tasks yet' }
    };
    const t = labels[this.lang];

    return html`
      ${this.items.length > 0 ? html`
        <div class="progress-label">
          <span class="progress-label-text">${this.title === 'Progress' ? t.tasks : this.title}</span>
          <span class="progress-summary">${this.getProgressSummary(t.completed)}</span>
        </div>
      ` : ''}

      <div class="progress-list">
        ${this.items.length === 0
          ? html`<div class="empty-state">${t.noTasks}</div>`
          : this.items.map(item => html`
              <div class="progress-item ${item.status}">
                <div class="progress-icon ${item.status}">
                  ${this.getStatusIcon(item.status)}
                </div>
                <div class="progress-content">
                  <p class="progress-text">${item.text}</p>
                  ${item.detail ? html`<p class="progress-detail">${item.detail}</p>` : ''}
                </div>
              </div>
            `)
        }
      </div>
    `;
  }
}
