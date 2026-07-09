// Log build information when the module loads
console.log(
  '%cN2S Web Components',
  'color: #4CAF50; font-weight: bold; font-size: 14px;'
);
console.log(
  `%cVersion: ${__BUILD_VERSION__}`,
  'color: #2196F3; font-weight: bold;'
);
console.log(
  `%cBuilt: ${__BUILD_TIME__}`,
  'color: #FF9800; font-weight: bold;'
);
console.log(
  '%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
  'color: #9E9E9E;'
);

export { N2sChat } from './components/n2s-chat';
export { N2sMessage } from './components/n2s-message';
export { N2sStatusBar } from './components/n2s-status-bar';
export { N2sProgressTracker } from './components/n2s-progress-tracker';
export { PlotlyChart } from './components/plotly-chart';

// Rich component system
export {
  ComponentRegistry,
  ComponentManager,
  CardComponentRenderer,
  TaskListComponentRenderer,
  ProgressBarComponentRenderer,
  NotificationComponentRenderer,
  StatusIndicatorComponentRenderer,
  TextComponentRenderer
} from './components/rich-component-system';

// Rich component styles are injected automatically by the ComponentManager
