/**
 * ModeSwitch Component
 * Toggle between teaching mode and practice mode
 */

import type { ChatMode } from '../types';

interface ModeSwitchProps {
  currentMode: ChatMode;
  onSwitch: (mode: ChatMode) => void;
}

// Mode descriptions
const MODE_INFO: Record<ChatMode, { label: string; description: string }> = {
  teaching: {
    label: '📚 教学模式',
    description: '系统讲解编程概念，循序渐进引导学习',
  },
  practice: {
    label: '🔧 实用模式',
    description: '解决实际问题，边练边学',
  },
  creation: {
    label: '💡 创作模式',
    description: '协助你完成编程项目创作',
  },
};

function ModeSwitch({ currentMode, onSwitch }: ModeSwitchProps) {
  const modes: ChatMode[] = ['teaching', 'practice', 'creation'];

  return (
    <div className="mode-switch">
      <div className="mode-switch-buttons">
        {modes.map((mode) => (
          <button
            key={mode}
            type="button"
            className={`mode-switch-button ${currentMode === mode ? 'active' : ''}`}
            onClick={() => onSwitch(mode)}
          >
            {MODE_INFO[mode].label}
          </button>
        ))}
      </div>
      <p className="mode-switch-description">
        {MODE_INFO[currentMode].description}
      </p>
    </div>
  );
}

export default ModeSwitch;