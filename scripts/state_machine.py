# 状态机管理模块
# 为 OpenClaw 任务提供状态流转控制

from enum import Enum, auto
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
import json

class TaskStatus(Enum):
    """任务状态枚举"""
    CREATED = "created"           # 刚创建
    PREPARING = "preparing"       # 准备中
    READY = "ready"               # 准备就绪
    RUNNING = "running"           # 运行中
    PAUSED = "paused"             # 已暂停
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 已失败

class StateMachine:
    """
    状态机管理器
    
    特点:
    1. 定义清晰的状态转换规则
    2. 支持转换回调
    3. 记录状态历史
    4. 防止非法状态转换
    """
    
    # 定义合法的状态转换
    VALID_TRANSITIONS = {
        TaskStatus.CREATED: [TaskStatus.PREPARING, TaskStatus.FAILED],
        TaskStatus.PREPARING: [TaskStatus.READY, TaskStatus.FAILED],
        TaskStatus.READY: [TaskStatus.RUNNING, TaskStatus.FAILED],
        TaskStatus.RUNNING: [TaskStatus.PAUSED, TaskStatus.COMPLETED, TaskStatus.FAILED],
        TaskStatus.PAUSED: [TaskStatus.RUNNING, TaskStatus.FAILED],
        TaskStatus.COMPLETED: [],  # 终态
        TaskStatus.FAILED: [TaskStatus.CREATED]  # 可以重启
    }
    
    def __init__(self, initial_status: TaskStatus = TaskStatus.CREATED):
        self.status = initial_status
        self.history = []
        self.callbacks = {}
        self._record_transition(None, initial_status, "初始化")
        
    def transition(self, new_status: TaskStatus, reason: str = "") -> bool:
        """
        状态转换
        
        Args:
            new_status: 目标状态
            reason: 转换原因
            
        Returns:
            是否转换成功
        """
        if not self.can_transition_to(new_status):
            return False
        
        old_status = self.status
        self.status = new_status
        self._record_transition(old_status, new_status, reason)
        
        # 触发回调
        self._trigger_callbacks(old_status, new_status, reason)
        
        return True
    
    def can_transition_to(self, new_status: TaskStatus) -> bool:
        """检查是否可以转换到目标状态"""
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])
    
    def get_available_transitions(self) -> List[TaskStatus]:
        """获取当前可用的转换目标"""
        return self.VALID_TRANSITIONS.get(self.status, [])
    
    def on_transition(self, from_status: TaskStatus, to_status: TaskStatus, 
                     callback: Callable):
        """注册状态转换回调"""
        key = (from_status, to_status)
        if key not in self.callbacks:
            self.callbacks[key] = []
        self.callbacks[key].append(callback)
    
    def _trigger_callbacks(self, from_status: TaskStatus, to_status: TaskStatus, 
                            reason: str):
        """触发回调函数"""
        key = (from_status, to_status)
        if key in self.callbacks:
            for callback in self.callbacks[key]:
                try:
                    callback(from_status, to_status, reason)
                except Exception as e:
                    print(f"回调执行错误: {e}")
    
    def _record_transition(self, from_status: Optional[TaskStatus], 
                          to_status: TaskStatus, reason: str):
        """记录状态转换历史"""
        self.history.append({
            "from": from_status.value if from_status else None,
            "to": to_status.value,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取状态历史"""
        return self.history
    
    def get_current_status(self) -> TaskStatus:
        """获取当前状态"""
        return self.status
    
    def is_terminal(self) -> bool:
        """检查是否为终态"""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
    
    def to_dict(self) -> Dict[str, Any]:
        """导出为字典"""
        return {
            "current_status": self.status.value,
            "history": self.history,
            "is_terminal": self.is_terminal(),
            "available_transitions": [s.value for s in self.get_available_transitions()]
        }
    
    def to_json(self) -> str:
        """导出为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

class TaskWithStateMachine:
    """带状态机的任务类"""
    
    def __init__(self, task_id: str, title: str):
        self.task_id = task_id
        self.title = title
        self.state_machine = StateMachine(TaskStatus.CREATED)
        self.created_at = datetime.now().isoformat()
        self.metadata = {}
        
    def start_preparation(self, reason: str = "开始准备"):
        """开始准备"""
        return self.state_machine.transition(TaskStatus.PREPARING, reason)
    
    def mark_ready(self, reason: str = "准备完成"):
        """标记为就绪"""
        return self.state_machine.transition(TaskStatus.READY, reason)
    
    def start_execution(self, reason: str = "开始执行"):
        """开始执行"""
        return self.state_machine.transition(TaskStatus.RUNNING, reason)
    
    def pause(self, reason: str = "暂停"):
        """暂停"""
        return self.state_machine.transition(TaskStatus.PAUSED, reason)
    
    def resume(self, reason: str = "恢复"):
        """恢复"""
        return self.state_machine.transition(TaskStatus.RUNNING, reason)
    
    def complete(self, reason: str = "完成"):
        """完成"""
        return self.state_machine.transition(TaskStatus.COMPLETED, reason)
    
    def fail(self, reason: str = "失败"):
        """失败"""
        return self.state_machine.transition(TaskStatus.FAILED, reason)
    
    def restart(self, reason: str = "重启"):
        """重启"""
        return self.state_machine.transition(TaskStatus.CREATED, reason)
    
    def get_status(self) -> str:
        """获取当前状态"""
        return self.state_machine.get_current_status().value
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取状态历史"""
        return self.state_machine.get_history()
    
    def to_dict(self) -> Dict[str, Any]:
        """导出为字典"""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "status": self.get_status(),
            "created_at": self.created_at,
            "state": self.state_machine.to_dict(),
            "metadata": self.metadata
        }

# 便捷函数
def create_task(task_id: str, title: str) -> TaskWithStateMachine:
    """创建带状态机的任务"""
    return TaskWithStateMachine(task_id, title)

# 测试函数
def run_tests():
    print("="*60)
    print("状态机管理测试")
    print("="*60)
    
    # 测试1: 正常流程
    print("\n测试1: 正常任务流程")
    task = create_task("task_001", "测试任务")
    print(f"初始状态: {task.get_status()}")
    
    task.start_preparation("初始化资源")
    print(f"准备中: {task.get_status()}")
    
    task.mark_ready("资源准备完成")
    print(f"就绪: {task.get_status()}")
    
    task.start_execution("开始处理")
    print(f"运行中: {task.get_status()}")
    
    task.pause("临时暂停")
    print(f"暂停: {task.get_status()}")
    
    task.resume("继续处理")
    print(f"恢复运行: {task.get_status()}")
    
    task.complete("处理完成")
    print(f"完成: {task.get_status()}")
    
    print(f"\n状态历史:")
    for h in task.get_history():
        print(f"  {h['timestamp']}: {h['from']} -> {h['to']} ({h['reason']})")
    
    # 测试2: 非法转换
    print("\n" + "="*60)
    print("测试2: 非法状态转换")
    task2 = create_task("task_002", "非法转换测试")
    
    result = task2.complete()  # 从 CREATED 直接到 COMPLETED
    print(f"尝试直接完成: {'成功' if result else '失败'}")
    print(f"当前状态: {task2.get_status()}")
    
    # 测试3: 失败和重启
    print("\n" + "="*60)
    print("测试3: 失败和重启")
    task3 = create_task("task_003", "失败测试")
    
    task3.start_preparation()
    task3.mark_ready()
    task3.start_execution()
    task3.fail("遇到错误")
    print(f"失败后状态: {task3.get_status()}")
    
    task3.restart("重新尝试")
    print(f"重启后状态: {task3.get_status()}")
    
    # 测试4: 回调
    print("\n" + "="*60)
    print("测试4: 状态转换回调")
    task4 = create_task("task_004", "回调测试")
    
    def on_start(from_s, to_s, reason):
        print(f"  [回调] 任务开始执行: {reason}")
    
    task4.state_machine.on_transition(TaskStatus.READY, TaskStatus.RUNNING, on_start)
    
    task4.start_preparation()
    task4.mark_ready()
    task4.start_execution("执行回调测试")
    
    # 测试5: 导出
    print("\n" + "="*60)
    print("测试5: 导出 JSON")
    print(task4.state_machine.to_json()[:300] + "...")
    
    print("\n✅ 所有状态机测试完成!")

# 运行测试
if __name__ == "__main__":
    run_tests()
