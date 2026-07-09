import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { dell1996Tokens } from '../styles/dell1996-tokens.js';

export interface TaskItem {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  timestamp?: string;
}

@customElement('rich-task-list')
export class RichTaskList extends LitElement {
  static styles = [
    dell1996Tokens,
    css`
      :host {
        display: block;
        margin-bottom: var(--n2s-space-4);
        font-family: var(--n2s-font-family-serif);
      }

      .task-list {
        border: 1px solid #000000;
        border-radius: 0;
        background: #ffffff;
        box-shadow: none;
        overflow: hidden;
      }

      .task-list-header {
        padding: 6px 12px;
        background: #ffffff;
        border-bottom: 1px solid #000000;
      }

      .task-list-title {
        margin: 0 0 var(--n2s-space-2) 0;
        font-family: Helvetica, Arial, sans-serif;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        color: #000000;
      }

      .task-list-progress {
        display: flex;
        align-items: center;
        gap: var(--n2s-space-3);
      }

      .progress-text {
        font-size: 12px;
        color: #000000;
        min-width: fit-content;
      }

      .progress-bar {
        flex: 1;
        height: 6px;
        background: #ffffff;
        border: 1px solid #000000;
        overflow: hidden;
      }

      .progress-fill {
        height: 100%;
        background: #000000;
        transition: width var(--n2s-duration-300) ease;
      }

      .task-list-items {
        padding: var(--n2s-space-2);
      }

      .task-item {
        display: flex;
        align-items: flex-start;
        gap: var(--n2s-space-3);
        padding: var(--n2s-space-3);
        border-bottom: 1px solid #000000;
      }

      .task-item:last-child {
        border-bottom: none;
      }

      .task-item.status-completed {
        background: var(--dell-tint-sage);
      }

      .task-item.status-failed {
        background: var(--dell-tint-salmon);
      }

      .task-item.status-running {
        background: var(--dell-tint-sky);
      }

      .task-icon {
        font-size: 12px;
        margin-top: 2px;
        font-family: Helvetica, Arial, sans-serif;
        font-weight: 700;
        white-space: nowrap;
      }

      .task-content {
        flex: 1;
        min-width: 0;
      }

      .task-title {
        font-weight: 400;
        color: #000000;
        margin-bottom: var(--n2s-space-1);
        font-size: 14px;
      }

      .task-description {
        font-size: 12px;
        color: #000000;
        opacity: 0.8;
        margin-bottom: var(--n2s-space-2);
      }

      .task-progress {
        display: flex;
        align-items: center;
        gap: var(--n2s-space-2);
        margin-bottom: var(--n2s-space-2);
      }

      .task-progress-bar {
        flex: 1;
        height: 4px;
        background: #ffffff;
        border: 1px solid #000000;
        overflow: hidden;
      }

      .task-progress-fill {
        height: 100%;
        background: #000000;
        transition: width var(--n2s-duration-300) ease;
      }

      .task-progress-text {
        font-size: 12px;
        color: #000000;
        min-width: fit-content;
      }

      .task-timestamp {
        font-size: 11px;
        color: #000000;
        opacity: 0.7;
      }

      @media (max-width: 768px) {
        .task-list-header {
          padding-left: var(--n2s-space-3);
          padding-right: var(--n2s-space-3);
        }

        .task-list-progress {
          flex-direction: column;
          align-items: stretch;
          gap: var(--n2s-space-2);
        }
      }
    `
  ];

  @property() title = '';
  @property({ type: Array }) tasks: TaskItem[] = [];
  @property({ type: Boolean }) showProgress = true;
  @property({ type: Boolean }) showTimestamps = false;
  @property() theme: 'light' | 'dark' = 'dark';
  @property({ reflect: true }) lang: 'zh' | 'en' = 'zh';

  private get completedTasks(): number {
    return this.tasks.filter(task => task.status === 'completed').length;
  }

  private get progressPercentage(): number {
    return this.tasks.length > 0 ? (this.completedTasks / this.tasks.length) * 100 : 0;
  }

  private getStatusIcon(status: string): string {
    const labels: Record<string, string> = {
      'pending': '[待处理]',
      'running': '[进行中]',
      'completed': '[已完成]',
      'failed': '[失败]'
    };
    return labels[status] || labels['pending'];
  }

  private renderTask(task: TaskItem) {
    const statusIcon = this.getStatusIcon(task.status);

    return html`
      <div class="task-item status-${task.status}" data-task-id="${task.id}">
        <div class="task-icon">${statusIcon}</div>
        <div class="task-content">
          <div class="task-title">${task.title}</div>
          ${task.description ? html`
            <div class="task-description">${task.description}</div>
          ` : ''}
          ${task.progress !== null && task.progress !== undefined ? html`
            <div class="task-progress">
              <div class="task-progress-bar">
                <div class="task-progress-fill" style="width: ${task.progress * 100}%"></div>
              </div>
              <span class="task-progress-text">${Math.round(task.progress * 100)}%</span>
            </div>
          ` : ''}
          ${this.showTimestamps && task.timestamp ? html`
            <div class="task-timestamp">${task.timestamp}</div>
          ` : ''}
        </div>
      </div>
    `;
  }

  render() {
    const t = {
      zh: { completed: '已完成', title: '任务列表' },
      en: { completed: 'completed', title: 'Tasks' }
    }[this.lang];

    return html`
      <div class="task-list">
        <div class="task-list-header">
          <h3 class="task-list-title">${this.title || t.title}</h3>
          ${this.showProgress ? html`
            <div class="task-list-progress">
              <span class="progress-text">${this.completedTasks}/${this.tasks.length} ${t.completed}</span>
              <div class="progress-bar">
                <div class="progress-fill" style="width: ${this.progressPercentage}%"></div>
              </div>
            </div>
          ` : ''}
        </div>
        <div class="task-list-items">
          ${this.tasks.map(task => this.renderTask(task))}
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'rich-task-list': RichTaskList;
  }
}
