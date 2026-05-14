from data_processing.create_task_matrix import *

obc_li = generate_scheduled_tasks_as_objects('未来流量 模拟 setting(D+S).xlsx','D52+S49')
for i in obc_li:
    print(i.task_name)
    print(i.work_center)
    print(i.task_ddl)
    print(i.batch_qty)
    print(i.current_batch)