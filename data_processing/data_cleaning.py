import math
from openpyxl import load_workbook
from collections import defaultdict


def remove_duplicate(li):
    """去重，保留顺序"""
    li = [i for i in li if str(i).strip() != '']
    return list(dict.fromkeys(li))


def count_work_center_order(res_work_sheet):
    """统计每个work center有多少个不同的order"""
    work_center_orders_count = {}

    for col_name, values in res_work_sheet.items():
        if col_name == 'Work center':
            work_centers = values
            orders = res_work_sheet.get('Order', [])
            min_length = min(len(work_centers), len(orders))

            temp_dict = {}
            for i in range(min_length):
                wc = work_centers[i]
                order = orders[i]
                if wc not in temp_dict:
                    temp_dict[wc] = set()
                temp_dict[wc].add(order)

            for wc, unique_orders in temp_dict.items():
                work_center_orders_count[wc] = len(unique_orders)

    return work_center_orders_count


def read_excel_to_dict_openpyxl(file_path, sheet_name=None):
    """用openpyxl读excel，返回字典：key是列名，value是列数据列表"""
    wb = load_workbook(filename=file_path, read_only=True)

    if sheet_name is None:
        ws = wb.active
    else:
        ws = wb[sheet_name]

    result = {}
    header_row = list(ws.iter_rows(min_row=1, max_row=1, values_only=True))[0]
    data_rows = list(ws.iter_rows(min_row=2, values_only=True))

    for col_idx, col_name in enumerate(header_row):
        if col_name is None or str(col_name).strip() == '':
            continue

        col_key = str(col_name).strip()
        col_values = []
        for row in data_rows:
            if col_idx < len(row):
                value = row[col_idx]
                if value is not None:
                    col_values.append(value)
        result[col_key] = col_values

    wb.close()
    return result


def get_priority_batch(file_path, sheet_name=None):
    """主函数：读取excel，计算每个work center需要多少批次"""
    res_work_sheet = read_excel_to_dict_openpyxl(file_path, sheet_name=sheet_name)

    # 统计每个work center的order数量
    work_center_order_qty = count_work_center_order(res_work_sheet)

    # 获取work center顺序（priority）
    priority = remove_duplicate(res_work_sheet['Work center'])
    print('find work center with sequence:' + str(len(priority)))

    # 读取trolley表，获取每个work center的小车容量
    res_trolley = read_excel_to_dict_openpyxl('../未来流量 模拟 setting(D+S).xlsx', sheet_name='trolley')

    trolley_capacity = {}
    for i in range(len(res_trolley['Work center'])):
        key = res_trolley['Work center'][i]
        trolley_capacity[key] = str(res_trolley['capacity'][i])

    print('-' * 40)
    print(len(trolley_capacity.keys()))

    # 按priority顺序，匹配每个work center的trolley容量
    priority_trolley_dict = {}
    for work_center in priority:
        flag = 0
        for key in trolley_capacity.keys():
            if work_center in key:
                priority_trolley_dict[work_center] = trolley_capacity[key]
                flag = 1
        if flag == 0:
            print(f'cannot find {work_center} in trolley table, capacity 20 by default')
            priority_trolley_dict[work_center] = '20'

    # 计算每个work center的批次数量：order数 / 小车容量，向上取整
    work_center_batch_qty = {}
    for i in priority:
        work_center_batch_qty[i] = str(math.ceil(work_center_order_qty[i] / int(priority_trolley_dict[i])))

    return work_center_batch_qty, priority


if __name__ == '__main__':
    get_priority_batch('../未来流量 模拟 setting(D+S).xlsx', 'D52+S49')
