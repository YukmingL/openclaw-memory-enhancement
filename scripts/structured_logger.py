#!/usr/bin/env python3
"""
Structured Logger - 结构化日志系统
基于 MiroFish ReportLogger 改进

功能:
- JSONL 格式记录每步操作
- 包含: timestamp, action, stage, details
- 支持调试回放和审计
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

class StructuredLogger:
    """
    结构化日志记录器
    
    使用示例:
        logger = StructuredLogger("logs/analysis.jsonl")
        logger.log("start", "planning", {"task": "分析需求"})
        logger.log("tool_call", "research", {"tool": "web_search", "query": "AI趋势"})
        logger.log("complete", "report", {"sections": 5})
    """
    
    def __init__(self, log_path: str, task_name: str = "default"):
        """
        初始化日志记录器
        
        Args:
            log_path: 日志文件路径
            task_name: 任务名称，用于标识不同任务
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.task_name = task_name
        self.session_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        # 记录会话开始
        self.log("session_start", "init", {
            "task_name": task_name,
            "session_id": self.session_id,
            "log_path": str(self.log_path)
        })
    
    def log(self, action: str, stage: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        记录一条日志
        
        Args:
            action: 操作类型 (start/planning/tool_call/llm_response/complete/error)
            stage: 当前阶段 (init/planning/research/analysis/report)
            details: 详细信息字典
        
        Returns:
            完整的日志条目
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "task_name": self.task_name,
            "action": action,
            "stage": stage,
            "details": details
        }
        
        # 追加写入 JSONL
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        return log_entry
    
    def log_tool_call(self, tool_name: str, tool_input: Dict[str, Any], 
                      tool_output: Any, stage: str = "research") -> Dict[str, Any]:
        """记录工具调用"""
        return self.log("tool_call", stage, {
            "tool": tool_name,
            "input": tool_input,
            "output": tool_output,
            "output_type": type(tool_output).__name__
        })
    
    def log_llm_response(self, prompt: str, response: str, 
                        stage: str = "analysis") -> Dict[str, Any]:
        """记录 LLM 响应"""
        return self.log("llm_response", stage, {
            "prompt_length": len(prompt),
            "response_length": len(response),
            "response_preview": response[:200] + "..." if len(response) > 200 else response
        })
    
    def log_error(self, error: Exception, stage: str = "execution") -> Dict[str, Any]:
        """记录错误"""
        return self.log("error", stage, {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stage": stage
        })
    
    def get_logs(self, action: Optional[str] = None, 
                 stage: Optional[str] = None,
                 since: Optional[str] = None) -> list:
        """
        查询日志
        
        Args:
            action: 过滤操作类型
            stage: 过滤阶段
            since: 过滤时间 (ISO格式)
        
        Returns:
            匹配的日志条目列表
        """
        logs = []
        
        if not self.log_path.exists():
            return logs
        
        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    
                    # 过滤条件
                    if action and entry.get("action") != action:
                        continue
                    if stage and entry.get("stage") != stage:
                        continue
                    if since and entry.get("timestamp", "") < since:
                        continue
                    
                    logs.append(entry)
                except json.JSONDecodeError:
                    continue
        
        return logs
    
    def get_session_summary(self) -> Dict[str, Any]:
        """获取会话摘要"""
        logs = self.get_logs()
        
        actions = {}
        stages = set()
        errors = []
        
        for log in logs:
            action = log.get("action", "unknown")
            actions[action] = actions.get(action, 0) + 1
            stages.add(log.get("stage", "unknown"))
            
            if action == "error":
                errors.append(log.get("details", {}))
        
        return {
            "session_id": self.session_id,
            "task_name": self.task_name,
            "total_logs": len(logs),
            "actions": actions,
            "stages": list(stages),
            "errors": errors,
            "log_path": str(self.log_path)
        }
    
    def replay(self, action_filter: Optional[str] = None) -> str:
        """
        回放日志（用于调试）
        
        Args:
            action_filter: 只回放特定类型的操作
        
        Returns:
            格式化的回放文本
        """
        logs = self.get_logs(action=action_filter)
        
        lines = [f"=== 日志回放: {self.task_name} ({self.session_id}) ===\n"]
        
        for log in logs:
            ts = log.get("timestamp", "")[11:19]  # 只取时间部分
            action = log.get("action", "unknown")
            stage = log.get("stage", "unknown")
            details = log.get("details", {})
            
            lines.append(f"[{ts}] {action:12} | {stage:10} | {json.dumps(details, ensure_ascii=False)[:60]}...")
        
        return "\n".join(lines)


# 便捷函数
def create_logger(task_name: str, log_dir: str = "logs") -> StructuredLogger:
    """快速创建日志记录器"""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    log_path = f"{log_dir}/{task_name}_{timestamp}.jsonl"
    return StructuredLogger(log_path, task_name)


if __name__ == "__main__":
    # 测试
    print("=== 结构化日志系统测试 ===\n")
    
    # 创建日志记录器
    logger = create_logger("test_analysis", "test_logs")
    
    # 模拟分析任务
    logger.log("start", "planning", {"requirement": "分析AI趋势"})
    logger.log("planning", "planning", {"outline": ["背景", "现状", "趋势", "结论"]})
    
    # 模拟工具调用
    logger.log_tool_call("web_search", 
                        {"query": "AI trends 2026"},
                        {"results": 5, "sources": ["techcrunch", "wired"]})
    
    logger.log_tool_call("memory_search",
                        {"query": "AI偏好"},
                        {"entities": ["pref_001", "pref_002"]})
    
    # 模拟LLM响应
    logger.log_llm_response("分析AI趋势", "AI技术正在快速发展...", "analysis")
    
    # 模拟完成
    logger.log("complete", "report", {"sections": 4, "word_count": 1200})
    
    # 打印摘要
    summary = logger.get_session_summary()
    print("会话摘要:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    print("\n日志回放:")
    print(logger.replay())
    
    # 清理测试文件
    import shutil
    if os.path.exists("test_logs"):
        shutil.rmtree("test_logs")
    
    print("\n✅ 测试完成!")
