from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd


def visualized_res(task_li, unique=True, save_name=None):
    """
    可视化任务与物料吞吐量。
    unique=True: 存储-缓存（物料去重）
    unique=False: 缓存-拣选（物料不去重）
    """
    if unique:
        save_name = '../' + save_name + "存储-缓存"
    else:
        save_name = '../' + save_name + '缓存-拣选'

    if not task_li:
        print("Warning: task_li is empty. Cannot generate visualization.")
        return

    # 按时间点统计物料和任务数
    task_zone = defaultdict(list)
    task_sum = defaultdict(int)

    for task in task_li:
        for material in task.material_unique_li:
            task_zone[task.task_ddl].append(material)
        task_sum[task.task_ddl] += 1

    # 是否去重
    for key, value in task_zone.items():
        if unique:
            task_zone[key] = list(set(value))

    # 准备绘图数据
    ddl_list = list(task_zone.keys())
    task_counts = [task_sum[ddl] for ddl in ddl_list]
    material_counts = [len(task_zone[ddl]) for ddl in ddl_list]

    df_plot = pd.DataFrame({
        'ddl': ddl_list,
        'task_count': task_counts,
        'material_count': material_counts
    })

    # 计算总数
    total_tasks = df_plot['task_count'].sum()
    all_material_global = 0
    for k, v in task_zone.items():
        all_material_global += len(v)

    # 绘图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    fig.patch.set_facecolor('#666666')

    font_title = {'fontsize': 16, 'weight': 'bold', 'color': 'white'}
    font_label = {'fontsize': 14, 'weight': 'bold', 'color': 'white'}
    tick_params_style = {'labelsize': 12, 'colors': 'white'}
    grid_kwargs = {'axis': 'y', 'linestyle': '--', 'alpha': 0.7, 'color': '#AAAAAA'}

    # 子图1：任务数
    bars1 = ax1.bar(df_plot['ddl'], df_plot['task_count'],
                    color='#EDB52F', edgecolor='none', linewidth=0)
    ax1.set_ylabel('Number of Tasks', **font_label)
    ax1.set_title('Pallet ASRS Throughput Simulation - Task Count', **font_title)
    ax1.grid(**grid_kwargs)
    ax1.tick_params(axis='x', rotation=45, **tick_params_style)
    ax1.tick_params(axis='y', **tick_params_style)
    ax1.set_facecolor('#666666')

    for bar in bars1:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, h + 1,
                 f'{int(h)}', ha='center', va='bottom',
                 fontsize=11, color='black', weight='bold')

    # 子图2：物料数
    bars2 = ax2.bar(df_plot['ddl'], df_plot['material_count'],
                    color='black', edgecolor='none', linewidth=0)
    ax2.set_xlabel('Time Zone (DDL)', **font_label)
    ax2.set_ylabel('Number of Materials', **font_label)
    ax2.set_title('Pallet ASRS Throughput Simulation - Material Quantity', **font_title)
    ax2.grid(**grid_kwargs)
    ax2.tick_params(axis='x', rotation=45, **tick_params_style)
    ax2.tick_params(axis='y', **tick_params_style)
    ax2.set_facecolor('#666666')

    for bar in bars2:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, h + 5,
                 f'{int(h)}', ha='center', va='bottom',
                 fontsize=11, color='white', weight='bold')

    # 右上角总数标签
    summary_text = f'Total Tasks: {total_tasks}, Total Materials: {all_material_global}'
    fig.text(0.98, 0.98, summary_text,
             ha='right', va='top',
             fontsize=13, color='white', weight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#333333', alpha=0.9))

    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.savefig(save_name, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
