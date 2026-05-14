from create_task_matrix import *
from visualized import *
task_li = generate_scheduled_tasks_as_objects('../未来流量 模拟 setting(D+S).xlsx','D52+S49')

import pandas as pd
from create_task_matrix import generate_scheduled_tasks_as_objects


def populate_task_data_from_table(task_li, excel_path, sheet_name='calculated_table'):
    """
    根据 task_li 中的信息，从指定 Excel 表中读取数据并填充到 TaskMaterial 对象中。

    Args:
        task_li: List[TaskMaterial], 由 generate_scheduled_tasks_as_objects 返回的任务列表。
        excel_path: str, Excel 文件路径。
        sheet_name: str, 要读取的工作表名称。默认为 'calculated_table'。
    """
    # 1. 读取 Excel 表格
    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    # 2. 确保列名正确（根据你的描述）
    # 假设列名为 'Order', 'Material', 'Work Center'
    required_columns = ['Order', 'Material', 'Work center']
    if not all(col in df.columns for col in required_columns):
        available_cols = list(df.columns)
        raise ValueError(f"Required columns {required_columns} not found in table. Available columns: {available_cols}")

    # 3. 遍历每个任务对象
    for task in task_li:
        # 3.1 根据 work_center 筛选 DataFrame
        wc_filtered_df = df[df['Work center'] == task.work_center]

        # 3.2 提取 'Order' 列并去重（保持首次出现顺序）
        unique_orders_series = wc_filtered_df['Order'].drop_duplicates(keep='first')
        order_pool_list = unique_orders_series.tolist()  # 转换为列表

        # 3.3 解析 task.order_seq ("X-Y") 并切片 order_pool_list
        start_str, end_str = task.order_seq.split('-')
        start_idx = int(start_str)
        end_idx = int(end_str)

        # 切片 [start_idx:end_idx]，如果超出范围会自动截断到列表末尾
        task_order_list = order_pool_list[start_idx:end_idx]

        # 3.4 填充 task.order_list
        task.order_list = task_order_list

        # 3.5 根据 task.order_list 和 task.work_center 筛选 DataFrame，提取 Material 并去重
        if task_order_list:  # 如果 order_list 不为空
            material_filtered_df = wc_filtered_df[wc_filtered_df['Order'].isin(task.order_list)]
            unique_materials_series = material_filtered_df['Material'].drop_duplicates(keep='first')
            task.material_unique_li = unique_materials_series.tolist()
        else:  # 如果 order_list 为空，则 material_unique_li 也应为空列表
            task.material_unique_li = []

    return task_li

# populate_task_data_from_table(task_li, '../未来流量 模拟 setting(D+S).xlsx',
#                                   'D52+S49')


# --- 使用示例 ---
if __name__ == "__main__":
    sheet_name = 'D47+S43'
    populate_task_data_from_table(task_li, '../未来流量 模拟 setting(D+S).xlsx',
                                  sheet_name)
    for i in task_li:
        print(i.task_name)
        print(i.material_unique_li)
        print(i.task_ddl)
    visualized_res(task_li,True,sheet_name)