from datetime import time, timedelta, datetime
from data_cleaning import get_priority_batch


class TaskMaterial:
    """任务对象，包含任务的基本信息"""

    def __init__(self, task_name, work_center, task_ddl, batch_qty, current_batch):
        self.task_name = str(task_name) if task_name is not None else ""
        self.work_center = str(work_center) if work_center is not None else ""
        self.task_ddl = str(task_ddl) if task_ddl is not None else ""
        self.batch_qty = int(batch_qty) if batch_qty is not None else 0
        self.current_batch = int(current_batch) if current_batch is not None else 0

        self.material_li = []
        self.material_unique_li = []
        self.order_list = []

        # order_seq格式：0-20, 20-40, ...
        start_seq = (self.current_batch - 1) * 20
        end_seq = self.current_batch * 20
        self.order_seq = f"{start_seq}-{end_seq}"

    def __str__(self):
        return (f"TaskMaterial(task_name='{self.task_name}', work_center='{self.work_center}', "
                f"task_ddl='{self.task_ddl}', batch_qty={self.batch_qty}, "
                f"current_batch={self.current_batch}, order_seq='{self.order_seq}')")

    def to_dict(self):
        return {
            'task_name': self.task_name,
            'work_center': self.work_center,
            'task_ddl': self.task_ddl,
            'batch_qty': self.batch_qty,
            'current_batch': self.current_batch,
            'order_seq': self.order_seq
        }


def generate_scheduled_tasks_as_objects(file_path, sheet_name):
    """
    读取excel，生成任务对象列表。
    每个work center按批次生成任务，按时间和优先级排序。
    """
    work_center_batches, priority = get_priority_batch(file_path, sheet_name)

    # 检查数据合法性
    priority_set = set(priority)
    for wc in work_center_batches:
        if wc not in priority_set:
            raise ValueError(f"Work center '{wc}' not found in priority list.")
        qty = int(work_center_batches[wc])
        if qty <= 0:
            raise ValueError(f"Batch quantity for '{wc}' must be positive, got {qty}.")

    # 建立优先级索引
    priority_map = {wc: idx for idx, wc in enumerate(priority)}

    # 生成所有任务
    tasks_with_info = []
    base_time = time(8, 0)
    total_seconds = 8 * 3600

    for wc, qty_str in work_center_batches.items():
        qty = int(qty_str)
        interval_seconds = total_seconds / qty

        # 先计算这个work center的所有时间点
        wc_time_points = []
        for i in range(qty):
            offset_seconds = i * interval_seconds
            base_datetime = datetime.combine(datetime.today(), base_time)
            new_datetime = base_datetime + timedelta(seconds=offset_seconds)
            task_time = new_datetime.time()
            formatted_time = task_time.strftime("%H:%M")
            wc_time_points.append(formatted_time)

        # 生成任务
        for i in range(qty):
            task_time_formatted = wc_time_points[i]
            task_name = f"{wc}-{task_time_formatted}"

            tasks_with_info.append({
                'name': task_name,
                'time': wc_time_points[i],
                'work_center': wc,
                'batch_qty': qty,
                'time_points': wc_time_points,
                'priority_idx': priority_map[wc]
            })

    # 排序：先按时间，再按优先级
    sorted_tasks_info = sorted(tasks_with_info, key=lambda t: (t['time'], t['priority_idx']))

    # 构建TaskMaterial对象
    result_objects = []
    for task_info in sorted_tasks_info:
        task_name = task_info['name']
        work_center = task_info['work_center']
        task_ddl = task_info['time']
        batch_qty = task_info['batch_qty']
        time_points_list = task_info['time_points']

        # 计算current_batch：在时间点列表中的位置（从1开始）
        current_batch_index = time_points_list.index(task_ddl)
        current_batch = current_batch_index + 1

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
    obc_li = generate_scheduled_tasks_as_objects('../未来流量 模拟 setting(D+S).xlsx', 'D52+S49')
    for i in obc_li:
        print(i.task_name)
        print(i.work_center)
        print(i.task_ddl)
        print(i.batch_qty)
        print(i.current_batch)
        print(i.order_seq)
