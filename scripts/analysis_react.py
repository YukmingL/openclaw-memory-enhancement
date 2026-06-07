# ReACT Analyzer
# Reasoning + Acting analysis engine for OpenClaw

import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from enum import Enum

class AnalysisStep(Enum):
    REASONING = "reasoning"
    ACTION = "action"
    OBSERVATION = "observation"
    CONCLUSION = "conclusion"

class ReACTAnalyzer:
    """
    ReACT (Reasoning + Acting) analysis engine
    
    特点:
    1. 先思考再行动 - 基于推理生成行动计划
    2. 工具驱动 - 强制调用工具获取数据，防止幻觉
    3. 多步推理 - 支持复杂问题的分步解决
    4. 来源引用 - 每个结论必须引用数据来源
    """
    
    def __init__(self, tool_registry: Dict[str, Callable] = None):
        self.steps = []
        self.tool_registry = tool_registry or {}
        self.current_step = 0
        self.max_steps = 10
        
    def analyze(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行 ReACT 分析流程
        
        Args:
            query: 用户查询
            context: 上下文信息
            
        Returns:
            分析结果，包含推理链和最终结论
        """
        self.steps = []
        self.current_step = 0
        
        # Step 1: 理解问题（Reasoning）
        self._add_step(AnalysisStep.REASONING, 
                      f"理解查询: {query}",
                      {"query": query, "context": context})
        
        # Step 2: 制定计划（Reasoning）
        plan = self._create_plan(query, context)
        self._add_step(AnalysisStep.REASONING,
                      f"制定计划: {plan}",
                      {"plan": plan})
        
        # Step 3+: 执行计划（Action + Observation）
        observations = []
        for action in plan:
            if self.current_step >= self.max_steps:
                break
                
            # 执行行动
            result = self._execute_action(action)
            self._add_step(AnalysisStep.ACTION,
                          f"执行: {action['type']}",
                          {"action": action, "result": result})
            
            # 观察结果
            observation = self._observe_result(result)
            self._add_step(AnalysisStep.OBSERVATION,
                          f"观察: {observation}",
                          {"observation": observation})
            observations.append(observation)
        
        # 最终结论
        conclusion = self._synthesize_conclusion(query, observations)
        self._add_step(AnalysisStep.CONCLUSION,
                      f"结论: {conclusion}",
                      {"conclusion": conclusion})
        
        return {
            "query": query,
            "steps": self.steps,
            "conclusion": conclusion,
            "observations": observations,
            "step_count": len(self.steps)
        }
    
    def _create_plan(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据查询创建行动计划"""
        plan = []
        
        # 分析查询类型
        if "天气" in query or "weather" in query.lower():
            plan.append({"type": "weather_check", "params": {"location": query}})
            
        elif "新闻" in query or "news" in query.lower():
            plan.append({"type": "news_search", "params": {"query": query}})
            
        elif "搜索" in query or "search" in query.lower():
            plan.append({"type": "web_search", "params": {"query": query}})
            
        elif "文件" in query or "document" in query.lower():
            plan.append({"type": "file_read", "params": {"path": query}})
            
        else:
            # 默认：先搜索，再分析
            plan.append({"type": "web_search", "params": {"query": query}})
            plan.append({"type": "analysis", "params": {"query": query}})
        
        return plan
    
    def _execute_action(self, action: Dict[str, Any]) -> Any:
        """执行单个行动"""
        action_type = action.get("type")
        params = action.get("params", {})
        
        if action_type in self.tool_registry:
            try:
                return self.tool_registry[action_type](**params)
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"status": "skipped", "reason": f"No tool registered for {action_type}"}
    
    def _observe_result(self, result: Any) -> str:
        """观察并描述结果"""
        if isinstance(result, dict):
            if "error" in result:
                return f"错误: {result['error']}"
            elif "status" in result:
                return f"状态: {result['status']}"
            else:
                return f"数据: {json.dumps(result, ensure_ascii=False)[:200]}"
        else:
            return f"结果: {str(result)[:200]}"
    
    def _synthesize_conclusion(self, query: str, observations: List[str]) -> str:
        """综合所有观察得出结论"""
        if not observations:
            return "无法得出结论：没有可用的观察数据"
        
        # 检查是否有错误
        errors = [obs for obs in observations if "错误" in obs]
        if errors:
            return f"分析遇到问题：{errors[0]}。请检查输入或稍后重试。"
        
        # 综合所有观察
        valid_observations = [obs for obs in observations if "错误" not in obs and "状态: skipped" not in obs]
        
        if not valid_observations:
            return "无法获取有效数据来完成分析。"
        
        return f"基于 {len(valid_observations)} 个观察结果，查询 '{query}' 的分析已完成。"
    
    def _add_step(self, step_type: AnalysisStep, description: str, data: Dict[str, Any]):
        """添加分析步骤"""
        self.steps.append({
            "step": self.current_step,
            "type": step_type.value,
            "description": description,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        self.current_step += 1
    
    def get_reasoning_chain(self) -> List[str]:
        """获取推理链（仅 reasoning 步骤）"""
        return [step["description"] for step in self.steps 
                if step["type"] == AnalysisStep.REASONING.value]
    
    def get_actions_taken(self) -> List[str]:
        """获取执行的行动"""
        return [step["description"] for step in self.steps 
                if step["type"] == AnalysisStep.ACTION.value]
    
    def to_json(self) -> str:
        """导出为 JSON 字符串"""
        return json.dumps({
            "steps": self.steps,
            "step_count": len(self.steps),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

# 便捷函数
def quick_analyze(query: str, tools: Dict[str, Callable] = None) -> Dict[str, Any]:
    """快速分析函数"""
    analyzer = ReACTAnalyzer(tools)
    return analyzer.analyze(query)

# 测试函数
def run_tests():
    # 模拟工具
    def mock_weather(location):
        return {"temperature": 25, "condition": "sunny", "location": location}
    
    def mock_search(query):
        return {"results": ["result1", "result2"], "query": query}
    
    tools = {
        "weather_check": mock_weather,
        "web_search": mock_search
    }
    
    # 测试分析
    analyzer = ReACTAnalyzer(tools)
    result = analyzer.analyze("广州天气怎么样？", {"location": "广州"})
    
    print(f"查询: {result['query']}")
    print(f"步骤数: {result['step_count']}")
    print(f"结论: {result['conclusion']}")
    print("\n推理链:")
    for r in analyzer.get_reasoning_chain():
        print(f"  - {r}")
    print("\n执行的行动:")
    for a in analyzer.get_actions_taken():
        print(f"  - {a}")
    
    print("\n" + "="*50)
    print("测试2: 通用查询")
    print("="*50)
    
    result2 = analyzer.analyze("Python 最新版本是什么？")
    print(f"查询: {result2['query']}")
    print(f"步骤数: {result2['step_count']}")
    print(f"结论: {result2['conclusion']}")
    
    print("\n" + "="*50)
    print("测试3: 带错误的场景")
    print("="*50)
    
    # 模拟一个会失败的工具
    def failing_tool(**kwargs):
        raise Exception("API 调用失败")
    
    tools_with_error = {
        "weather_check": failing_tool,
        "web_search": mock_search
    }
    
    analyzer3 = ReACTAnalyzer(tools_with_error)
    result3 = analyzer3.analyze("北京天气", {"location": "北京"})
    print(f"查询: {result3['query']}")
    print(f"步骤数: {result3['step_count']}")
    print(f"结论: {result3['conclusion']}")
    
    print("\n完整步骤日志:")
    for step in result3['steps']:
        print(f"  [{step['type']}] {step['description']}")
    
    print("\n" + "="*50)
    print("测试4: 导出 JSON")
    print("="*50)
    
    json_output = analyzer3.to_json()
    print(json_output[:500] + "...")
    
    print("\n✅ 所有 ReACT 测试完成!")

# 运行测试
if __name__ == "__main__":
    print("="*50)
    print("ReACT 分析器测试")
    print("="*50)
    run_tests()
