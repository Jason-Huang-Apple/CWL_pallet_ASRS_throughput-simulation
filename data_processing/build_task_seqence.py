from data_cleaning import *

task_batch,priority = get_priority_batch('../未来流量 模拟 setting(D+S).xlsx','D52+S49')

from datetime import time, timedelta


def schedule_and_sort_tasks(work_center_batches: dict, priority: list) -> list:
    """
    根据工作中心批次数量和优先级列表，生成并排序任务。

    Args:
        work_center_batches: Dict[str, str], key为work center名称，value为批次数量（字符串）
        priority: List[str], 包含所有work center的优先级列表，索引越小优先级越高

    Returns:
        List[str]: 排序后的任务列表，格式为 "workcenter-08:00"

    Raises:
        ValueError: 如果批次数量为0或work center不在priority中
    """
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

    tasks = []
    base_time = time(8, 0)  # 08:00:00
    total_seconds_per_day = 24 * 3600
    total_task_duration_hours = 8
    total_task_duration_seconds = total_task_duration_hours * 3600

    for wc, qty_str in work_center_batches.items():
        qty = int(qty_str)
        interval_seconds = total_task_duration_seconds / qty

        for i in range(qty):
            # 计算当前任务的时间偏移量
            offset_seconds = i * interval_seconds

            # 使用 timedelta 来精确计算时间
            # 从基准日期开始，加上偏移量，再提取 time
            # 注意：timedelta只能用于日期时间运算，不能直接加到time上
            # 所以我们用一个基准datetime对象来操作
            from datetime import datetime
            base_datetime = datetime.combine(datetime.today(), base_time)
            new_datetime = base_datetime + timedelta(seconds=offset_seconds)
            task_time = new_datetime.time()

            # 格式化时间为 HH:MM
            formatted_time = task_time.strftime("%H:%M")

            task_name = f"{wc}-{formatted_time}"
            # 存储任务及其排序所需的信息
            tasks.append({
                'name': task_name,
                'time': task_time,
                'priority_idx': priority_map[wc]
            })

    # 3. 排序：先按时间，再按优先级索引
    sorted_tasks = sorted(tasks, key=lambda t: (t['time'], t['priority_idx']))

    # 4. 提取排序后的任务名称列表
    return [task['name'] for task in sorted_tasks]
res = schedule_and_sort_tasks(task_batch, priority)
for i in res:
    print(i)
