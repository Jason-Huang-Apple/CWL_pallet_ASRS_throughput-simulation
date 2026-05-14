
from datetime import time, timedelta
import math
from data_cleaning import *

task_batch,priority = get_priority_batch('../未来流量 模拟 setting(D+S).xlsx','D52+S49')

class TaskMaterial:
    def __init__(self, task_name, work_center, task_ddl, batch_qty, current_batch):
        self.task_name = str(task_name) if task_name is not None else ""
        self.work_center = str(work_center) if work_center is not None else ""
        self.task_ddl = str(task_ddl) if task_ddl is not None else ""
        self.batch_qty = int(batch_qty) if batch_qty is not None else 0
        self.current_batch = int(current_batch) if current_batch is not None else 0

        self.material_li = []
        self.material_unique_li = []
        self.order_list = []

        # 计算order_seq: (current_batch-1)*20 到 current_batch*20
        start_seq = (self.current_batch - 1) * 20
        end_seq = self.current_batch * 20
        self.order_seq = f"{start_seq}-{end_seq}"

    def __str__(self):
        return f"TaskMaterial(task_name='{self.task_name}', work_center='{self.work_center}', " \
               f"task_ddl='{self.task_ddl}', batch_qty={self.batch_qty}, current_batch={self.current_batch}, order_seq='{self.order_seq}')"

    def to_dict(self):
        return {
            'task_name': self.task_name,
            'work_center': self.work_center,
            'task_ddl': self.task_ddl,
            'batch_qty': self.batch_qty,
            'current_batch': self.current_batch,
            'order_seq': self.order_seq
        }


def generate_scheduled_tasks_as_objects(file_path: str, sheet_name: str) -> list:
    """
    根据工作中心批次数量和优先级列表，生成并排序任务，并返回 TaskMaterial 对象列表。

    Args:
        work_center_batches: Dict[str, str], key为work center名称，value为批次数量（字符串）
        priority: List[str], 包含所有work center的优先级列表，索引越小优先级越高

    Returns:
        List[TaskMaterial]: 排序后的 TaskMaterial 对象列表

    Raises:
        ValueError: 如果批次数量为0或work center不在priority中
    """
    work_center_batches, priority = get_priority_batch(file_path, sheet_name)

    # 1. 验证输入
    priority_set = set(priority)
    for wc in work_center_batches:
        if wc not in priority_set:
            raise ValueError(f"Work center '{wc}' not found in priority list.")
        qty = int(work_center_batches[wc])
        if qty <= 0:
            raise ValueError(f"Batch quantity for '{wc}' must be positive, got {qty}.")

    # 2. 创建优先级索引映射以加速查找
    priority_map = {wc: idx for idx, wc in enumerate(priority)}

    # 3. 生成所有任务及其排序信息
    tasks_with_info = []
    base_time = time(8, 0)  # 08:00:00
    total_task_duration_hours = 8
    total_task_duration_seconds = total_task_duration_hours * 3600

    for wc, qty_str in work_center_batches.items():
        qty = int(qty_str)
        interval_seconds = total_task_duration_seconds / qty

        # 计算该work_center的所有时间点
        wc_time_points = []
        for i in range(qty):
            offset_seconds = i * interval_seconds
            from datetime import datetime
            base_datetime = datetime.combine(datetime.today(), base_time)
            new_datetime = base_datetime + timedelta(seconds=offset_seconds)
            task_time = new_datetime.time()
            formatted_time = task_time.strftime("%H:%M")
            wc_time_points.append(formatted_time)
        # print(wc_time_points)

        # 生成任务
        for i in range(qty):
            task_time_formatted = wc_time_points[i]
            task_name = f"{wc}-{task_time_formatted}"

            tasks_with_info.append({
                'name': task_name,
                'time': wc_time_points[i],  # 存储字符串时间便于后续匹配
                'work_center': wc,
                'batch_qty': qty,
                'time_points': wc_time_points,  # 存储整个时间点列表用于查找current_batch
                'priority_idx': priority_map[wc]
            })

    # 4. 排序：先按时间字符串（HH:MM格式可以按字符串排序），再按优先级索引
    sorted_tasks_info = sorted(tasks_with_info, key=lambda t: (t['time'], t['priority_idx']))

    # 5. 构建 TaskMaterial 对象列表
    result_objects = []
    for task_info in sorted_tasks_info:
        task_name = task_info['name']
        work_center = task_info['work_center']
        task_ddl = task_info['time']
        batch_qty = task_info['batch_qty']
        time_points_list = task_info['time_points']

        # 计算 current_batch: 在 time_points_list 中找到 task_ddl 的位置
        try:
            current_batch_index = time_points_list.index(task_ddl)  # 找到索引 (0-based)
            current_batch = current_batch_index + 1  # 转换为 1-based
        except ValueError:
            # 理论上不应该发生，因为 task_ddl 就是从 time_points_list 生成的
            raise RuntimeError(
                f"Could not find time '{task_ddl}' in generated time points for work center '{work_center}'. This should not happen.")

        obj = TaskMaterial(
            task_name=task_name,
            work_center=work_center,
            task_ddl=task_ddl,
            batch_qty=batch_qty,
            current_batch=current_batch
        )
        result_objects.append(obj)

    return result_objects
if __name__ == '__main__':

    obc_li = generate_scheduled_tasks_as_objects('../未来流量 模拟 setting(D+S).xlsx','D52+S49')
    for i in obc_li:
        print(i.task_name)
        print(i.work_center)
        print(i.task_ddl)
        print(i.batch_qty)
        print(i.current_batch)

        print(i.order_seq)
    # --- 使用示例 ---
    # work_center_batches = {
    #     "ATPHUC12": "2",
    #     "ATPHOL01": "3"
    # }
    # priority = ["ATPHOL01", "ATPHUC12"]
    # result_objects = generate_scheduled_tasks_as_objects(work_center_batches, priority)
    # for obj in result_objects:
    #     print(obj)