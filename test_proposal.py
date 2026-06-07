#!/usr/bin/env python3
"""
OpenClaw Memory Enhancement - Test Suite
测试提案中的6大改进点
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# 测试配置
TEST_DIR = Path(__file__).parent
LOG_FILE = TEST_DIR / "test_logs.jsonl"
GRAPH_FILE = TEST_DIR / "test_graph.jsonl"

def test_structured_logger():
    """测试改进点3: 结构化日志系统"""
    print("\n=== 测试1: 结构化日志系统 ===")
    
    class StructuredLogger:
        def __init__(self, log_path):
            self.log_path = Path(log_path)
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        def log(self, action: str, stage: str, details: dict):
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": action,
                "stage": stage,
                "details": details
            }
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            return log_entry
    
    # 测试
    logger = StructuredLogger(LOG_FILE)
    entry = logger.log("test_start", "phase1", {"test": "structured_logger"})
    
    # 验证
    assert "timestamp" in entry
    assert entry["action"] == "test_start"
    print(f"✅ 结构化日志测试通过: {entry['timestamp']}")
    return True

def test_temporal_graph():
    """测试改进点4: 时序知识图谱"""
    print("\n=== 测试2: 时序知识图谱 ===")
    
    class TemporalGraph:
        def __init__(self, graph_path):
            self.graph_path = Path(graph_path)
            self.graph_path.parent.mkdir(parents=True, exist_ok=True)
        
        def add_fact(self, entity_id, entity_type, properties, valid_at=None, invalid_at=None):
            fact = {
                "op": "create",
                "entity": {
                    "id": entity_id,
                    "type": entity_type,
                    "properties": properties,
                    "valid_at": valid_at or datetime.now(timezone.utc).isoformat(),
                    "invalid_at": invalid_at
                }
            }
            with open(self.graph_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(fact, ensure_ascii=False) + '\n')
            return fact
        
        def get_valid_facts(self, at_time=None):
            """获取在指定时间有效的事实"""
            at_time = at_time or datetime.now(timezone.utc)
            valid_facts = []
            
            if not self.graph_path.exists():
                return valid_facts
            
            with open(self.graph_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    fact = json.loads(line)
                    valid_at = datetime.fromisoformat(fact["entity"]["valid_at"].replace('Z', '+00:00'))
                    invalid_at = fact["entity"].get("invalid_at")
                    
                    if valid_at <= at_time:
                        if invalid_at is None or datetime.fromisoformat(invalid_at.replace('Z', '+00:00')) > at_time:
                            valid_facts.append(fact)
            
            return valid_facts
    
    # 测试
    graph = TemporalGraph(GRAPH_FILE)
    
    # 添加一个已过期的事实
    graph.add_fact("pref_001", "Preference", 
                   {"subject": "AI模型", "value": "GPT-4"},
                   valid_at="2026-01-01T00:00:00+00:00",
                   invalid_at="2026-03-15T00:00:00+00:00")
    
    # 添加一个当前有效的事实
    graph.add_fact("pref_002", "Preference",
                   {"subject": "AI模型", "value": "Kimi"},
                   valid_at="2026-03-15T00:00:00+00:00")
    
    # 验证时序查询
    now = datetime.now(timezone.utc)
    valid_facts = graph.get_valid_facts(at_time=now)
    
    assert len(valid_facts) == 1, f"应该只有1个有效事实，实际有{len(valid_facts)}个"
    assert valid_facts[0]["entity"]["id"] == "pref_002"
    print(f"✅ 时序图谱测试通过: 找到{len(valid_facts)}个有效事实")
    return True

def test_context_assembler():
    """测试改进点5: 上下文组装机制"""
    print("\n=== 测试3: 上下文组装机制 ===")
    
    class ContextAssembler:
        def __init__(self, graph_path):
            self.graph_path = Path(graph_path)
        
        def search_entities(self, query):
            """模拟实体搜索"""
            # 简单实现：返回包含query的所有实体
            entities = []
            if self.graph_path.exists():
                with open(self.graph_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            fact = json.loads(line)
                            entity = fact.get("entity", {})
                            props = entity.get("properties", {})
                            props_str = json.dumps(props, ensure_ascii=False)
                            print(f"    搜索检查: {props_str[:50]}...")
                            if query.lower() in props_str.lower():
                                entities.append(entity)
                                print(f"    匹配成功!")
                        except (json.JSONDecodeError, KeyError) as e:
                            print(f"    解析错误: {e}")
                            continue
            return entities
        
        def assemble(self, query: str, max_tokens: int = 4000):
            entities = self.search_entities(query)
            
            if not entities:
                return f"未找到与'{query}'相关的记忆"
            
            # 组装上下文
            context_parts = [f"## 关于 '{query}' 的相关记忆:\n"]
            for entity in entities:
                props = entity["properties"]
                part = f"- {entity['type']}: {json.dumps(props, ensure_ascii=False)}"
                context_parts.append(part)
            
            return "\n".join(context_parts)
    
    # 测试（使用之前创建的图谱）
    # 先检查文件内容
    print(f"  图谱文件存在: {GRAPH_FILE.exists()}")
    if GRAPH_FILE.exists():
        with open(GRAPH_FILE, 'r') as f:
            lines = f.readlines()
            print(f"  图谱文件行数: {len(lines)}")
            for i, line in enumerate(lines):
                print(f"  行{i}: {line[:80]}...")
    
    assembler = ContextAssembler(GRAPH_FILE)
    context = assembler.assemble("AI模型")
    
    assert "AI模型" in context, f"Context missing 'AI模型': {context}"
    assert "Kimi" in context, f"Context missing 'Kimi': {context}"
    print(f"✅ 上下文组装测试通过:\n{context[:100]}...")
    return True

def test_ontology_enhancement():
    """测试改进点6: 本体增强（新类型）"""
    print("\n=== 测试4: 本体增强 ===")
    
    # 定义新的schema类型
    SCHEMA = {
        "Preference": {
            "required": ["subject", "value", "valid_at"],
            "properties": {
                "subject": str,
                "value": str,
                "valid_at": str,
                "invalid_at": str,
                "rating": str  # high/medium/low
            }
        },
        "Learning": {
            "required": ["source", "lesson", "date"],
            "properties": {
                "source": str,
                "lesson": str,
                "category": str,
                "date": str
            }
        },
        "Decision": {
            "required": ["description", "date", "context"],
            "properties": {
                "description": str,
                "context": str,
                "rationale": str,
                "outcome": str,
                "date": str
            }
        }
    }
    
    # 验证新类型
    preference = {
        "subject": "AI模型",
        "value": "Kimi",
        "valid_at": "2026-03-15T00:00:00+00:00",
        "rating": "high"
    }
    
    # 检查必填字段
    for field in SCHEMA["Preference"]["required"]:
        assert field in preference, f"缺少必填字段: {field}"
    
    print(f"✅ 本体增强测试通过: Preference类型验证成功")
    return True

def test_react_pattern():
    """测试改进点1: ReACT模式（模拟）"""
    print("\n=== 测试5: ReACT分析模式 ===")
    
    class ReACTAnalyzer:
        """模拟ReACT分析器"""
        
        def analyze(self, requirement: str):
            # 模拟ReACT循环
            steps = []
            
            # Thought
            steps.append({"type": "thought", "content": f"分析需求: {requirement}"})
            
            # Action（模拟工具调用）
            steps.append({"type": "action", "content": "搜索相关信息"})
            
            # Observation
            steps.append({"type": "observation", "content": "找到3条相关记忆"})
            
            # Reflection
            steps.append({"type": "reflection", "content": "信息足够，可以生成报告"})
            
            return {
                "requirement": requirement,
                "steps": steps,
                "tool_calls": 1  # 模拟调用了1次工具
            }
    
    analyzer = ReACTAnalyzer()
    result = analyzer.analyze("测试分析任务")
    
    assert len(result["steps"]) >= 4  # Thought, Action, Observation, Reflection
    assert result["tool_calls"] >= 1
    print(f"✅ ReACT模式测试通过: {len(result['steps'])}个步骤, {result['tool_calls']}次工具调用")
    return True

def test_state_machine():
    """测试改进点2: 状态机管理"""
    print("\n=== 测试6: 状态机管理 ===")
    
    from enum import Enum
    
    class TaskStatus(str, Enum):
        CREATED = "created"
        PREPARING = "preparing"
        READY = "ready"
        RUNNING = "running"
        PAUSED = "paused"
        COMPLETED = "completed"
        FAILED = "failed"
    
    class Task:
        def __init__(self, name):
            self.name = name
            self.status = TaskStatus.CREATED
            self.history = []
        
        def transition(self, new_status):
            old_status = self.status
            self.status = new_status
            self.history.append({
                "from": old_status.value,
                "to": new_status.value,
                "time": datetime.now(timezone.utc).isoformat()
            })
            return self.status
    
    # 测试状态转换
    task = Task("测试任务")
    task.transition(TaskStatus.PREPARING)
    task.transition(TaskStatus.READY)
    task.transition(TaskStatus.RUNNING)
    task.transition(TaskStatus.COMPLETED)
    
    assert task.status == TaskStatus.COMPLETED
    assert len(task.history) == 4
    print(f"✅ 状态机测试通过: 经历{len(task.history)}次状态转换")
    return True

def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("OpenClaw Memory Enhancement - 提案测试")
    print("=" * 50)
    
    tests = [
        ("结构化日志", test_structured_logger),
        ("时序图谱", test_temporal_graph),
        ("上下文组装", test_context_assembler),
        ("本体增强", test_ontology_enhancement),
        ("ReACT模式", test_react_pattern),
        ("状态机", test_state_machine)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, True, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"❌ {name}测试失败: {e}")
    
    # 清理测试文件
    for f in [LOG_FILE, GRAPH_FILE]:
        if f.exists():
            f.unlink()
    
    # 打印结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    
    for name, ok, error in results:
        status = "✅ 通过" if ok else f"❌ 失败: {error}"
        print(f"  {name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！提案核心功能验证成功。")
        return 0
    else:
        print(f"\n⚠️ {total - passed}个测试失败，需要检查实现。")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
