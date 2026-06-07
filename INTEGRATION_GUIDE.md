# OpenClaw Memory Enhancement - 集成使用指南

## 概述

基于 MiroFish 和 Zep 改进的 OpenClaw 记忆分析系统已实施完成。本指南说明如何在实际工作中集成使用。

---

## 快速集成

### 1. 基础集成（推荐）

```python
# 在 OpenClaw 工作流中集成
import sys
from pathlib import Path

# 添加技能路径
SKILL_DIR = Path("/path/to/openclaw-memory-enhancement")
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from system_integration import create_system

# 创建记忆系统实例
memory_system = create_system("/path/to/workspace")

# 处理用户消息时自动记录和分析
result = memory_system.process_message("用户消息内容")
# 自动完成：
# - 结构化日志记录
# - 上下文组装
# - ReACT 分析
# - 状态管理
```

### 2. 轻量级集成

```python
# 仅使用需要的组件
from structured_logger import StructuredLogger
from context_assembler import ContextAssembler

# 记录操作日志
logger = StructuredLogger("memory/logs.jsonl")
logger.log("action", "stage", {"key": "value"})

# 组装上下文
assembler = ContextAssembler("memory/graph.jsonl")
context = assembler.assemble("查询关键词", max_tokens=2000)
```

---

## 使用场景

### 场景1: 用户偏好学习

```python
# 当用户表达偏好时自动记录
memory_system = create_system("/path/to/workspace")

# 用户说"我喜欢用 Python"
result = memory_system.process_message("我喜欢用 Python 编程")

# 系统自动：
# 1. 记录结构化日志
# 2. 提取偏好：Preference {subject: "编程语言", value: "Python"}
# 3. 保存到知识图谱
# 4. 更新用户画像
```

### 场景2: 复杂查询分析

```python
# 使用 ReACT 模式处理复杂查询
from analysis_react import ReACTAnalyzer

# 定义工具
weather_tool = {
    "name": "weather",
    "description": "获取天气信息",
    "parameters": {"location": "string"}
}

analyzer = ReACTAnalyzer([weather_tool])

# 分析查询
result = analyzer.analyze("广州明天天气怎么样？")
# 输出：
# {
#   "steps": [...],
#   "conclusion": "...",
#   "tool_calls": [...]
# }
```

### 场景3: 任务状态管理

```python
from state_machine import TaskWithStateMachine

# 创建任务
task = TaskWithStateMachine("task_001", "数据分析任务")

# 状态流转
task.start_preparation()   # CREATED -> PREPARING
task.mark_ready()          # PREPARING -> READY
task.start_execution()     # READY -> RUNNING

# 暂停/恢复
task.pause()               # RUNNING -> PAUSED
task.resume()              # PAUSED -> RUNNING

# 完成
task.complete()            # RUNNING -> COMPLETED

# 查看历史
print(task.get_history())
```

### 场景4: 上下文组装

```python
from context_assembler import ContextAssembler

assembler = ContextAssembler("memory/graph.jsonl")

# 组装用户相关上下文
context = assembler.assemble(
    query="用户偏好",
    max_tokens=2000,
    entity_types=["Preference", "Learning"]
)

# 用于 LLM 提示
prompt = f"""
基于以下上下文回答用户问题：

{context}

用户问题：{user_question}
"""
```

---

## 与 OpenClaw 集成

### 方法1: 作为技能调用

```bash
# 通过 OpenClaw CLI 调用
openclaw skill run openclaw-memory-enhancement \
  --action process_message \
  --message "用户消息"
```

### 方法2: 作为 Python 模块

```python
# 在 OpenClaw Agent 中导入
from openclaw_memory_enhancement.scripts.system_integration import create_system

class EnhancedAgent:
    def __init__(self):
        self.memory = create_system("/path/to/workspace")
    
    def process(self, message):
        # 自动记录和分析
        result = self.memory.process_message(message)
        
        # 获取组装好的上下文
        context = self.memory.assemble_context(message)
        
        # 使用上下文生成回复
        response = self.llm.generate(context, message)
        
        return response
```

### 方法3: 作为 Gateway 插件

```json
// 在 openclaw.json 中配置
{
  "skills": {
    "openclaw-memory-enhancement": {
      "enabled": true,
      "workspace": "/path/to/workspace",
      "auto_log": true,
      "auto_extract": true
    }
  }
}
```

---

## 配置选项

### 环境变量

```bash
# 日志级别
export MEMORY_LOG_LEVEL=info

# 日志文件路径
export MEMORY_LOG_PATH=memory/logs.jsonl

# 知识图谱路径
export MEMORY_GRAPH_PATH=memory/graph.jsonl

# 最大上下文令牌数
export MEMORY_MAX_TOKENS=2000

# 是否自动提取偏好
export MEMORY_AUTO_EXTRACT=true
```

### 配置文件

```json
// memory-config.json
{
  "logging": {
    "level": "info",
    "path": "memory/logs.jsonl",
    "max_size": "100MB"
  },
  "graph": {
    "path": "memory/graph.jsonl",
    "auto_backup": true
  },
  "context": {
    "max_tokens": 2000,
    "default_types": ["Preference", "Learning", "Decision"]
  },
  "react": {
    "max_steps": 10,
    "tools": ["weather", "search", "calendar"]
  }
}
```

---

## 最佳实践

### 1. 日志记录

```python
# 记录所有关键操作
logger = StructuredLogger("logs.jsonl")

# 用户交互
logger.log("user_interaction", "receive", {
    "user_id": "user_001",
    "message": "...",
    "channel": "wechat"
})

# 工具调用
logger.log("tool_call", "execute", {
    "tool": "weather",
    "parameters": {"location": "广州"},
    "result": "..."
})

# 错误处理
logger.log("error", "handle", {
    "error": "...",
    "context": "..."
})
```

### 2. 上下文组装

```python
# 组装时指定类型过滤
context = assembler.assemble(
    query="用户偏好",
    entity_types=["Preference"],  # 只获取偏好
    max_tokens=1000
)

# 组装时指定时间范围
from datetime import datetime, timedelta
context = assembler.assemble(
    query="最近学习",
    after=datetime.now() - timedelta(days=7)  # 最近7天
)
```

### 3. 状态管理

```python
# 使用状态机管理长任务
task = TaskWithStateMachine("long_task", "数据分析")

# 添加状态转换回调
task.on_transition("running", "completed", lambda: print("任务完成！"))

# 安全状态转换
try:
    task.start_execution()  # 必须在 ready 状态后调用
except ValueError as e:
    print(f"状态转换错误: {e}")
```

---

## 故障排除

### 常见问题

#### 1. 日志文件过大

```python
# 定期清理旧日志
import os
from datetime import datetime

log_file = "logs.jsonl"
if os.path.getsize(log_file) > 100 * 1024 * 1024:  # 100MB
    # 归档旧日志
    os.rename(log_file, f"logs_{datetime.now().strftime('%Y%m%d')}.jsonl")
```

#### 2. 知识图谱损坏

```python
# 备份和恢复
import shutil

# 备份
shutil.copy("graph.jsonl", "graph.jsonl.bak")

# 恢复
shutil.copy("graph.jsonl.bak", "graph.jsonl")
```

#### 3. 内存不足

```python
# 限制上下文大小
context = assembler.assemble(
    query="...",
    max_tokens=1000  # 减少令牌数
)

# 分页加载
for batch in assembler.assemble_batch(query="...", batch_size=100):
    process(batch)
```

---

## 示例工作流

### 完整示例: 智能客服集成

```python
from system_integration import create_system
from context_assembler import ContextAssembler

class SmartCustomerService:
    def __init__(self):
        self.memory = create_system("/workspace")
        self.assembler = ContextAssembler("/workspace/memory/graph.jsonl")
    
    def handle_message(self, user_id, message):
        # 1. 记录用户消息
        self.memory.log("user_message", "receive", {
            "user_id": user_id,
            "message": message
        })
        
        # 2. 组装用户上下文
        context = self.assembler.assemble(
            query=f"user:{user_id}",
            entity_types=["Preference", "History"]
        )
        
        # 3. 分析意图
        result = self.memory.process_message(message)
        intent = result["analysis"]["conclusion"]
        
        # 4. 生成回复
        if "天气" in intent:
            response = self.get_weather(message)
        elif "偏好" in intent:
            response = self.update_preference(user_id, message)
        else:
            response = self.general_response(context, message)
        
        # 5. 记录回复
        self.memory.log("agent_response", "send", {
            "user_id": user_id,
            "response": response
        })
        
        return response
    
    def get_weather(self, message):
        # 调用天气工具
        pass
    
    def update_preference(self, user_id, message):
        # 更新用户偏好
        self.memory.extract_preferences(user_id, message)
        return "已记录您的偏好"
    
    def general_response(self, context, message):
        # 使用上下文生成回复
        prompt = f"""
        用户历史：
        {context}
        
        用户问题：{message}
        """
        return self.llm.generate(prompt)

# 使用
service = SmartCustomerService()
response = service.handle_message("user_001", "我喜欢用 Python")
```

---

## 性能优化

### 1. 异步处理

```python
import asyncio

async def process_batch(messages):
    tasks = []
    for msg in messages:
        task = asyncio.create_task(memory.process_message_async(msg))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

### 2. 缓存

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_context(query):
    return assembler.assemble(query)
```

### 3. 批量写入

```python
# 批量写入日志
logger = StructuredLogger("logs.jsonl", batch_size=100)

for message in messages:
    logger.log("action", "stage", {"message": message})

logger.flush()  # 批量写入
```

---

## 监控和指标

### 关键指标

```python
# 统计日志
from structured_logger import LogAnalyzer

analyzer = LogAnalyzer("logs.jsonl")

# 查询统计
stats = analyzer.get_stats()
print(f"总记录数: {stats['total']}")
print(f"错误率: {stats['error_rate']}")
print(f"平均响应时间: {stats['avg_response_time']}")

# 用户偏好统计
preferences = analyzer.get_preferences()
print(f"偏好数量: {len(preferences)}")
```

---

## 更新和维护

### 定期维护任务

```bash
# 1. 备份知识图谱
cp memory/graph.jsonl memory/graph.jsonl.bak

# 2. 清理过期日志
python -c "
from structured_logger import LogCleaner
cleaner = LogCleaner('logs.jsonl')
cleaner.clean_before(days=30)
"

# 3. 优化图谱
python -c "
from context_assembler import GraphOptimizer
optimizer = GraphOptimizer('graph.jsonl')
optimizer.compact()
"
```

---

## 支持和反馈

如有问题或建议，请：

1. 查看日志文件 `memory/logs.jsonl`
2. 检查配置文件 `memory-config.json`
3. 提交 Issue 到项目仓库

---

**版本**: 1.0.0
**更新日期**: 2026-06-07
**状态**: ✅ 已集成可用
