import pandas as pd
from create_task_matrix import generate_scheduled_tasks_as_objects


def populate_task_data_from_table(task_li, excel_path, sheet_name='calculated_table'):
    """
    根据task_li中的信息，从excel中读取数据并填充到TaskMaterial对象中。
    """
    # 读取excel
    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    # 检查必要的列是否存在
    required_columns = ['Order', 'Material', 'Work center']
    if not all(col in df.columns for col in required_columns):
        available_cols = list(df.columns)
        raise ValueError(f"Required columns {required_columns} not found in table. Available columns: {available_cols}")

    # 遍历每个任务对象
    for task in task_li:
        # 按work center筛选数据
        wc_filtered_df = df[df['Work center'] == task.work_center]

        # 提取去重后的order列表
        unique_orders_series = wc_filtered_df['Order'].drop_duplicates(keep='first')
        order_pool_list = unique_orders_series.tolist()

        # 按order_seq切片
        start_str, end_str = task.order_seq.split('-')
        start_idx = int(start_str)
        end_idx = int(end_str)
        task_order_list = order_pool_list[start_idx:end_idx]

        # 填充order_list
        task.order_list = task_order_list

        # 根据order_list提取物料
        if task_order_list:
            material_filtered_df = wc_filtered_df[wc_filtered_df['Order'].isin(task.order_list)]
            unique_materials_series = material_filtered_df['Material'].drop_duplicates(keep='first')
            task.material_unique_li = unique_materials_series.tolist()
        else:
            task.material_unique_li = []

    return task_li


if __name__ == "__main__":
    task_li = generate_scheduled_tasks_as_objects('../未来流量 模拟 setting(D+S).xlsx', 'D52+S49')
    sheet_name = 'D47+S43'
    populate_task_data_from_table(task_li, '../未来流量 模拟 setting(D+S).xlsx', sheet_name)
    for i in task_li:
        print(i.task_name)
        print(i.material_unique_li)
        print(i.task_ddl)
