---
name: "openclaw-memory-enhancement"
description: "基于MiroFish和Zep改进OpenClaw记忆分析系统"
---

# OpenClaw 记忆与分析系统增强提案

## 概述

基于 MiroFish（多智能体预测引擎）和 Zep（上下文工程平台）的学习成果，对 OpenClaw 现有记忆系统（ontology + memory）进行增强。

## 改进点

### 1. 引入 ReACT 分析模式（来自 MiroFish ReportAgent）

**现状**: 分析任务直接生成结果，缺乏推理过程可追溯性。
**改进**:
- 分析任务采用 Reasoning + Acting 模式
- 先规划大纲，再逐段生成
- 每段至少调用 3 次工具获取数据
- 强制引用数据来源，防止幻觉

**实现**:
```python
# 新增: scripts/analysis_react.py
class ReACTAnalyzer:
    """ReACT模式分析器"""
    
    def analyze(self, requirement: str):
        # Step 1: 规划大纲
        outline = self._plan_outline(requirement)
        
        # Step 2: 逐段生成
        for section in outline:
            content = self._generate_section_react(section)
            
        # Step 3: 整合报告
        return self._compile_report()
    
    def _generate_section_react(self, section):
        """ReACT循环生成单段"""
        for iteration in range(max_iterations):
            # Thought: 分析需求
            # Action: 调用工具（搜索/查询/计算）
            # Observation: 观察结果
            # Reflection: 反思改进
            pass
```

### 2. 状态机管理（来自 MiroFish SimulationManager）

**现状**: 任务状态管理简单，缺乏明确生命周期。
**改进**:
- 引入状态机: CREATED → PREPARING → READY → RUNNING → COMPLETED
- 每个状态转换记录日志
- 支持暂停/恢复/失败处理

**实现**:
```python
# 新增: scripts/state_machine.py
class TaskStatus(str, Enum):
    CREATED = "created"
    PREPARING = "preparing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
```

### 3. 结构化日志系统（来自 MiroFish ReportLogger）

**现状**: 日志分散，缺乏统一格式。
**改进**:
- JSONL 格式记录每步操作
- 包含: timestamp, action, stage, details
- 支持调试回放和审计

**实现**:
```python
# 新增: scripts/structured_logger.py
class StructuredLogger:
    def log(self, action: str, stage: str, details: dict):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,    # start/planning/tool_call/llm_response/complete
            "stage": stage,      # 当前阶段
            "details": details   # 完整内容
        }
        # 追加写入 JSONL
```

### 4. 时序知识图谱增强（来自 Zep Graphiti）

**现状**: ontology 记录实体关系，但缺乏时间维度。
**改进**:
- 为每个事实添加 `valid_at` / `invalid_at` 时间戳
- 支持事实过期和更新
- 理解关系随时间的演变

**实现**:
```jsonl
// 增强 graph.jsonl 格式
{"op":"create","entity":{
  "id":"pref_001","type":"Preference",
  "properties":{
    "subject":"AI模型",
    "value":"GPT-4",
    "valid_at":"2026-01-01T00:00:00Z",
    "invalid_at":"2026-03-15T00:00:00Z"
  }
}}
```

### 5. 上下文组装机制（来自 Zep get_user_context）

**现状**: memory_search 返回片段，需要手动组装。
**改进**:
- 新增 `memory_assemble_context()` 函数
- 自动组装相关记忆为预格式化上下文
- 关系感知（不仅返回事实，还返回关系）

**实现**:
```python
# 新增: scripts/context_assembler.py
class ContextAssembler:
    def assemble(self, query: str, max_tokens: int = 4000):
        # 1. 搜索相关实体
        entities = self.search_entities(query)
        
        # 2. 获取相关关系
        relations = self.get_relations(entities)
        
        # 3. 时序筛选（只返回有效的事实）
        valid_facts = self.filter_valid_at(relations)
        
        # 4. 组装为预格式化字符串
        return self.format_context(valid_facts)
```

### 6. 本体增强（来自 Zep Ontology）

**现状**: 基础类型（Person, Task, Event等）。
**改进**:
- 新增 `Preference` 类型（高优先级）
- 新增 `Learning` 类型（学习记录）
- 新增 `Decision` 类型（决策记录）
- 支持事实评级（高/中/低情感影响）

**实现**:
```yaml
# 更新 schema.yaml
 types:
   Preference:
     required: [subject, value, valid_at]
     properties:
       subject: str      # 偏好主题
       value: str        # 偏好值
       valid_at: datetime  # 生效时间
       invalid_at: datetime?  # 失效时间
       rating: enum[high, medium, low]  # 情感评级
   
   Learning:
     required: [source, lesson, date]
     properties:
       source: str       # 来源（如"2026-04-07 用户纠正"）
       lesson: str       # 教训内容
       category: str     # 类别（如"AI幻觉防护"）
       date: datetime
       
   Decision:
     required: [description, date, context]
     properties:
       description: str  # 决策描述
       context: str      # 决策背景
       rationale: str?   # 决策理由
       outcome: str?      # 结果
       date: datetime
```

## 实施计划

### Phase 1: 核心增强（1-2周）
1. 更新 ontology schema（新增类型）
2. 实现结构化日志系统
3. 增强 memory_search 为上下文组装

### Phase 2: ReACT分析（2-3周）
1. 实现 ReACTAnalyzer 类
2. 集成到 proactive-agent
3. 添加工具强制调用机制

### Phase 3: 时序图谱（3-4周）
1. 为 graph.jsonl 添加时间戳
2. 实现事实过期机制
3. 支持时序查询

## 预期收益

1. **防止幻觉**: 强制工具调用 + 引用来源
2. **可追溯性**: 结构化日志记录每步操作
3. **时间感知**: 理解用户偏好和事实的演变
4. **分析质量**: ReACT模式生成更深入的分析
5. **上下文质量**: 组装而非片段，关系感知

## 参考资源

- MiroFish: 多智能体预测引擎
- Zep: 上下文工程平台
- 现有系统: OpenClaw ontology + memory
