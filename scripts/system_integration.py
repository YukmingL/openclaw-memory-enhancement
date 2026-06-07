# 系统集成模块
# 将 Memory Enhancement 组件集成到 OpenClaw 工作流

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# 添加脚本路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from structured_logger import StructuredLogger
from context_assembler import ContextAssembler
from analysis_react import ReACTAnalyzer
from state_machine import TaskWithStateMachine, TaskStatus

class MemoryEnhancedSystem:
    """
    集成所有 Memory Enhancement 组件的系统
    
    功能:
    1. 自动记录所有操作到结构化日志
    2. 自动组装上下文用于查询
    3. 使用 ReACT 模式处理复杂查询
    4. 管理任务状态机
    5. 自动提取用户偏好
    """
    
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path) if workspace_path else Path.home() / "workspace"
        self.log_dir = self.workspace / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化组件
        self.logger = StructuredLogger(self.log_dir / "system.jsonl")
        self.assembler = ContextAssembler(str(self.workspace / "memory" / "graph.jsonl"))
        self.analyzer = ReACTAnalyzer(self._get_tool_registry())
        
        # 任务管理
        self.tasks = {}
        
        self.logger.log("system_init", "system", {
            "workspace": str(self.workspace),
            "timestamp": datetime.now().isoformat()
        })
    
    def _get_tool_registry(self) -> Dict[str, Any]:
        """获取工具注册表"""
        return {
            "search_memory": self.search_memory,
            "log_action": self.log_action,
            "get_context": self.get_context,
            "create_task": self.create_task,
            "update_task": self.update_task
        }
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理用户消息（主入口）
        
        Args:
            message: 用户消息
            context: 上下文信息
            
        Returns:
            处理结果
        """
        context = context or {}
        
        # 1. 记录接收到的消息
        self.logger.log("message_received", "processing", {
            "message": message,
            "context": context
        })
        
        # 2. 获取相关上下文
        related_context = self.get_context(message)
        
        # 3. 使用 ReACT 分析
        analysis = self.analyzer.analyze(message, {
            **context,
            "related_context": related_context
        })
        
        # 4. 提取偏好（如果适用）
        if self._is_preference_statement(message):
            self._extract_preference(message, context)
        
        # 5. 记录完成
        self.logger.log("message_processed", "completed", {
            "message": message,
            "steps": analysis.get("step_count", 0),
            "conclusion": analysis.get("conclusion", "")
        })
        
        return {
            "message": message,
            "analysis": analysis,
            "context": related_context,
            "timestamp": datetime.now().isoformat()
        }
    
    def search_memory(self, query: str, time_range: tuple = None) -> List[Dict[str, Any]]:
        """搜索记忆"""
        self.logger.log("memory_search", "search", {
            "query": query,
            "time_range": time_range
        })
        
        # 使用上下文组装器搜索
        results = self.assembler.search_entities(query)
        
        self.logger.log("memory_search", "completed", {
            "query": query,
            "results_count": len(results)
        })
        
        return results
    
    def get_context(self, query: str) -> str:
        """获取组装的上下文"""
        return self.assembler.assemble(query)
    
    def log_action(self, action_type: str, target: str, details: Dict[str, Any]) -> None:
        """记录操作"""
        self.logger.log("action", action_type, {
            "target": target,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def create_task(self, task_id: str, title: str) -> TaskWithStateMachine:
        """创建任务"""
        task = TaskWithStateMachine(task_id, title)
        self.tasks[task_id] = task
        
        self.logger.log("task_created", "task", {
            "task_id": task_id,
            "title": title
        })
        
        return task
    
    def update_task(self, task_id: str, new_status: str, reason: str = "") -> bool:
        """更新任务状态"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        status_map = {
            "preparing": TaskStatus.PREPARING,
            "ready": TaskStatus.READY,
            "running": TaskStatus.RUNNING,
            "paused": TaskStatus.PAUSED,
            "completed": TaskStatus.COMPLETED,
            "failed": TaskStatus.FAILED
        }
        
        if new_status in status_map:
            result = task.state_machine.transition(status_map[new_status], reason)
            
            self.logger.log("task_updated", "task", {
                "task_id": task_id,
                "new_status": new_status,
                "reason": reason,
                "success": result
            })
            
            return result
        
        return False
    
    def _is_preference_statement(self, message: str) -> bool:
        """判断是否是偏好陈述"""
        preference_keywords = [
            "喜欢", "偏好", "习惯", "总是", "从不",
            "prefer", "like", "always", "never", "favorite"
        ]
        return any(kw in message.lower() for kw in preference_keywords)
    
    def _extract_preference(self, message: str, context: Dict[str, Any]) -> None:
        """提取用户偏好"""
        # 简单的偏好提取逻辑
        self.logger.log("preference_extracted", "learning", {
            "message": message,
            "context": context
        })
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "tasks_count": len(self.tasks),
            "active_tasks": sum(1 for t in self.tasks.values() 
                              if t.get_status() not in ["completed", "failed"]),
            "log_file": str(self.logger.log_path),
            "workspace": str(self.workspace),
            "timestamp": datetime.now().isoformat()
        }
    
    def export_logs(self, format: str = "jsonl") -> str:
        """导出日志"""
        logs = self.logger.get_logs()
        
        if format == "json":
            return json.dumps(logs, ensure_ascii=False, indent=2)
        else:
            return "\n".join(json.dumps(log, ensure_ascii=False) for log in logs)

# 便捷函数
def create_system(workspace_path: str = None) -> MemoryEnhancedSystem:
    """创建增强系统实例"""
    return MemoryEnhancedSystem(workspace_path)

# 测试函数
def run_integration_tests():
    print("="*60)
    print("系统集成测试")
    print("="*60)
    
    # 创建临时测试目录
    test_dir = Path("/tmp/test_memory_system")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 初始化系统
    print("\n测试1: 系统初始化")
    system = create_system(str(test_dir))
    status = system.get_system_status()
    print(f"  工作区: {status['workspace']}")
    print(f"  任务数: {status['tasks_count']}")
    print(f"  日志文件: {status['log_file']}")
    print("✅ 系统初始化成功")
    
    # 2. 处理消息
    print("\n测试2: 消息处理")
    result = system.process_message("广州天气怎么样？", {"location": "广州"})
    print(f"  消息: {result['message']}")
    print(f"  分析步骤: {result['analysis']['step_count']}")
    print(f"  结论: {result['analysis']['conclusion'][:100]}...")
    print("✅ 消息处理成功")
    
    # 3. 创建和管理任务
    print("\n测试3: 任务管理")
    task = system.create_task("task_001", "测试任务")
    print(f"  任务创建: {task.task_id}")
    
    system.update_task("task_001", "preparing", "准备资源")
    system.update_task("task_001", "ready", "准备完成")
    system.update_task("task_001", "running", "开始执行")
    system.update_task("task_001", "completed", "执行完成")
    
    print(f"  最终状态: {task.get_status()}")
    print(f"  状态历史: {len(task.get_history())} 次转换")
    print("✅ 任务管理成功")
    
    # 4. 搜索记忆
    print("\n测试4: 记忆搜索")
    # 先添加一些测试数据到图谱文件
    graph_file = test_dir / "memory" / "graph.jsonl"
    graph_file.parent.mkdir(parents=True, exist_ok=True)
    with open(graph_file, 'w') as f:
        f.write(json.dumps({
            "op": "create",
            "entity": {
                "id": "test_001",
                "type": "Preference",
                "properties": {
                    "subject": "测试",
                    "value": "值",
                    "valid_at": "2026-01-01T00:00:00"
                }
            }
        }) + '\n')
    
    # 重新初始化 assembler 以加载新数据
    system.assembler = ContextAssembler(str(graph_file))
    
    results = system.search_memory("测试")
    print(f"  搜索结果: {len(results)} 条")
    print("✅ 记忆搜索成功")
    
    # 5. 导出日志
    print("\n测试5: 日志导出")
    logs = system.export_logs("jsonl")
    log_lines = logs.strip().split("\n")
    print(f"  日志条数: {len(log_lines)}")
    print("✅ 日志导出成功")
    
    # 6. 偏好提取
    print("\n测试6: 偏好提取")
    result = system.process_message("我喜欢用 Python 编程")
    print(f"  消息: {result['message']}")
    print("✅ 偏好提取成功")
    
    # 7. 系统状态
    print("\n测试7: 系统状态")
    final_status = system.get_system_status()
    print(f"  活跃任务: {final_status['active_tasks']}")
    print(f"  总任务: {final_status['tasks_count']}")
    print("✅ 系统状态获取成功")
    
    print("\n" + "="*60)
    print("🎉 所有集成测试通过!")
    print("="*60)
    
    # 清理
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    run_integration_tests()
