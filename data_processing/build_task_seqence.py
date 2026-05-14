from datetime import time, timedelta, datetime
from data_cleaning import get_priority_batch


def schedule_and_sort_tasks(work_center_batches, priority):
    """
    根据work center的批次数量和优先级，生成任务列表并排序。
    返回格式：["workcenter-08:00", ...]
    """
    # 检查数据合法性
    priority_set = set(priority)
    for wc in work_center_batches:
        if wc not in priority_set:
            raise ValueError(f"Work center '{wc}' not found in priority list.")
        qty = int(work_center_batches[wc])
        if qty <= 0:
            raise ValueError(f"Batch quantity for '{wc}' must be positive, got {qty}.")

    # 建立优先级索引，数字越小优先级越高
    priority_map = {wc: idx for idx, wc in enumerate(priority)}

    tasks = []
    base_time = time(8, 0)  # 从08:00开始
    total_seconds = 8 * 3600  # 8小时的总秒数

    for wc, qty_str in work_center_batches.items():
        qty = int(qty_str)
        interval_seconds = total_seconds / qty

        for i in range(qty):
            offset_seconds = i * interval_seconds

            # 计算当前任务的时间点
            base_datetime = datetime.combine(datetime.today(), base_time)
            new_datetime = base_datetime + timedelta(seconds=offset_seconds)
            task_time = new_datetime.time()
            formatted_time = task_time.strftime("%H:%M")

            task_name = f"{wc}-{formatted_time}"
            tasks.append({
                'name': task_name,
                'time': task_time,
                'priority_idx': priority_map[wc]
            })

    # 排序：先按时间，再按优先级
    sorted_tasks = sorted(tasks, key=lambda t: (t['time'], t['priority_idx']))

    return [task['name'] for task in sorted_tasks]


if __name__ == '__main__':
    task_batch, priority = get_priority_batch('../未来流量 模拟 setting(D+S).xlsx', 'D52+S49')
    res = schedule_and_sort_tasks(task_batch, priority)
    for i in res:
        print(i)
