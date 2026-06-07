#!/usr/bin/env python3
"""
Context Assembler - 上下文组装机制
基于 Zep get_user_context 改进

功能:
- 自动组装相关记忆为预格式化上下文
- 关系感知（不仅返回事实，还返回关系）
- 时序筛选（只返回有效的事实）
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

class ContextAssembler:
    """
    上下文组装器
    
    使用示例:
        assembler = ContextAssembler("memory/ontology/graph.jsonl")
        context = assembler.assemble("AI模型偏好", max_tokens=2000)
        print(context)
    """
    
    def __init__(self, graph_path: str):
        """
        初始化上下文组装器
        
        Args:
            graph_path: 知识图谱文件路径 (JSONL格式)
        """
        self.graph_path = Path(graph_path)
    
    def search_entities(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索相关实体
        
        Args:
            query: 查询关键词
        
        Returns:
            匹配的实体列表
        """
        entities = []
        
        if not self.graph_path.exists():
            return entities
        
        with open(self.graph_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    fact = json.loads(line)
                    entity = fact.get("entity", {})
                    props = entity.get("properties", {})
                    
                    # 检查所有属性值是否包含查询词
                    props_str = json.dumps(props, ensure_ascii=False)
                    if query.lower() in props_str.lower():
                        entities.append(entity)
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return entities
    
    def get_relations(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        获取实体的相关关系
        
        Args:
            entities: 实体列表
        
        Returns:
            关系列表
        """
        # 简化实现：返回实体的基本关系信息
        relations = []
        for entity in entities:
            relations.append({
                "type": entity.get("type", "unknown"),
                "id": entity.get("id", "unknown"),
                "properties": entity.get("properties", {})
            })
        return relations
    
    def filter_valid_at(self, facts: List[Dict[str, Any]], 
                        at_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        时序筛选：只返回在指定时间有效的事实
        
        Args:
            facts: 事实列表
            at_time: 指定时间（默认当前时间）
        
        Returns:
            有效事实列表
        """
        at_time = at_time or datetime.now(timezone.utc)
        valid_facts = []
        
        for fact in facts:
            valid_at = fact.get("properties", {}).get("valid_at")
            invalid_at = fact.get("properties", {}).get("invalid_at")
            
            if valid_at:
                valid_dt = datetime.fromisoformat(valid_at.replace('Z', '+00:00'))
                if valid_dt > at_time:
                    continue
            
            if invalid_at:
                invalid_dt = datetime.fromisoformat(invalid_at.replace('Z', '+00:00'))
                if invalid_dt <= at_time:
                    continue
            
            valid_facts.append(fact)
        
        return valid_facts
    
    def format_context(self, facts: List[Dict[str, Any]], 
                       include_metadata: bool = True) -> str:
        """
        将事实格式化为上下文字符串
        
        Args:
            facts: 事实列表
            include_metadata: 是否包含元数据
        
        Returns:
            格式化的上下文字符串
        """
        if not facts:
            return ""
        
        lines = []
        
        # 按类型分组
        by_type = {}
        for fact in facts:
            fact_type = fact.get("type", "Unknown")
            if fact_type not in by_type:
                by_type[fact_type] = []
            by_type[fact_type].append(fact)
        
        # 生成上下文
        for fact_type, type_facts in by_type.items():
            lines.append(f"\n### {fact_type}")
            
            for fact in type_facts:
                props = fact.get("properties", {})
                
                # 格式化属性
                prop_lines = []
                for key, value in props.items():
                    if key in ["valid_at", "invalid_at"] and not include_metadata:
                        continue
                    prop_lines.append(f"  - {key}: {value}")
                
                if prop_lines:
                    lines.append(f"- {fact.get('id', 'unknown')}:")
                    lines.extend(prop_lines)
        
        return "\n".join(lines)
    
    def assemble(self, query: str, max_tokens: int = 4000,
                 include_metadata: bool = True) -> str:
        """
        组装上下文
        
        Args:
            query: 查询关键词
            max_tokens: 最大token数（近似字符数）
            include_metadata: 是否包含时间元数据
        
        Returns:
            组装好的上下文字符串
        """
        # 1. 搜索相关实体
        entities = self.search_entities(query)
        
        if not entities:
            return f"未找到与'{query}'相关的记忆。"
        
        # 2. 获取相关关系
        relations = self.get_relations(entities)
        
        # 3. 时序筛选
        valid_facts = self.filter_valid_at(relations)
        
        # 4. 组装上下文
        context = self.format_context(valid_facts, include_metadata)
        
        # 5. 截断到最大长度
        if len(context) > max_tokens * 4:  # 粗略估计：1 token ≈ 4字符
            context = context[:max_tokens * 4] + "\n\n... (上下文已截断)"
        
        # 添加标题
        header = f"## 关于 '{query}' 的相关记忆\n"
        header += f"找到 {len(valid_facts)} 条有效记录\n"
        
        return header + context
    
    def assemble_multi_query(self, queries: List[str], 
                            max_tokens: int = 4000) -> str:
        """
        多查询组装
        
        Args:
            queries: 查询关键词列表
            max_tokens: 最大token数
        
        Returns:
            组装好的上下文字符串
        """
        all_contexts = []
        
        for query in queries:
            context = self.assemble(query, max_tokens=max_tokens // len(queries))
            if not context.startswith("未找到"):
                all_contexts.append(context)
        
        if not all_contexts:
            return "未找到相关记忆。"
        
        return "\n\n---\n\n".join(all_contexts)


if __name__ == "__main__":
    # 测试
    print("=== 上下文组装机制测试 ===\n")
    
    # 创建测试图谱
    test_graph = Path("test_graph.jsonl")
    with open(test_graph, 'w', encoding='utf-8') as f:
        # 添加一些测试数据
        f.write(json.dumps({
            "op": "create",
            "entity": {
                "id": "pref_001",
                "type": "Preference",
                "properties": {
                    "subject": "AI模型",
                    "value": "Kimi",
                    "valid_at": "2026-03-15T00:00:00+00:00",
                    "rating": "high"
                }
            }
        }, ensure_ascii=False) + '\n')
        
        f.write(json.dumps({
            "op": "create",
            "entity": {
                "id": "learn_001",
                "type": "Learning",
                "properties": {
                    "source": "2026-04-07 用户纠正",
                    "lesson": "AI幻觉防护",
                    "category": "安全",
                    "date": "2026-04-07T00:00:00+00:00"
                }
            }
        }, ensure_ascii=False) + '\n')
    
    # 测试组装器
    assembler = ContextAssembler(str(test_graph))
    
    # 单查询测试
    print("测试1: 单查询")
    context = assembler.assemble("AI模型")
    print(context[:200] + "...\n")
    
    # 多查询测试
    print("测试2: 多查询")
    multi_context = assembler.assemble_multi_query(["AI模型", "幻觉防护"])
    print(multi_context[:200] + "...\n")
    
    # 清理
    test_graph.unlink()
    
    print("✅ 测试完成!")
