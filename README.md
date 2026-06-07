# OpenClaw Memory Enhancement

基于 MiroFish 和 Zep 改进的 OpenClaw 记忆分析系统。

## 功能特性

- **ReACT 分析模式** - Reasoning + Acting 推理分析，防止幻觉
- **结构化日志系统** - JSONL 格式记录每步操作
- **上下文组装机制** - 自动组装相关记忆为预格式化上下文
- **时序知识图谱** - 支持事实过期和更新
- **状态机管理** - 任务生命周期管理
- **本体增强** - 新增 Preference、Learning、Decision 等类型

## 快速开始

```python
from scripts.system_integration import create_system

# 创建系统
system = create_system("/path/to/workspace")

# 处理消息
result = system.process_message("用户消息")
print(result['analysis']['conclusion'])
```

## 文件结构

```
openclaw-memory-enhancement/
├── SKILL.md                    # 提案文档
├── IMPLEMENTATION_COMPLETE.md  # 实施报告
├── INTEGRATION_GUIDE.md        # 集成指南
├── package.json                # 包配置
├── test_proposal.py            # 测试脚本
└── scripts/
    ├── structured_logger.py    # 结构化日志系统
    ├── context_assembler.py    # 上下文组装机制
    ├── analysis_react.py       # ReACT 分析器
    ├── state_machine.py        # 状态机管理
    └── system_integration.py   # 系统集成
```

## 测试

```bash
python3 test_proposal.py
```

## 许可证

MIT
MIT License

Copyright (c) 2026 YukmingL

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
