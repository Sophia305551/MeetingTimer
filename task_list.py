from typing import List, Optional
from task import Task

class TaskList:
    def __init__(self):
        self._tasks: List[Task] = []

    def add(self, task: Task):
        self._tasks.append(task)

    def get_all(self) -> List[Task]:
        return self._tasks.copy()  # 返回副本避免外部修改

    def delete(self, index: int):
        """删除指定索引的任务"""
        if 0 <= index < len(self._tasks):
            self._tasks.pop(index)

    def clear(self):
        """清空所有任务"""
        self._tasks.clear()

    def update(self, index: int, updated_task: Task):
        """更新指定索引的任务"""
        if 0 <= index < len(self._tasks):
            self._tasks[index] = updated_task

    def get_total_time(self) -> int:
        """获取总时长"""
        return sum(task.minutes for task in self._tasks)

    def get_task_count(self) -> int:
        """获取任务数量"""
        return len(self._tasks)

    def export_to_list(self) -> List[dict]:
        """导出为字典列表（用于CSV导出）"""
        return [{"name": task.name, "minutes": task.minutes} for task in self._tasks]

    def import_from_list(self, data: List[dict]):
        """从字典列表导入"""
        self._tasks = [Task(name=item["name"], minutes=item["minutes"]) for item in data]