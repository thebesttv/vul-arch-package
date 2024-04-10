import matplotlib.pyplot as plt
import os
import csv

def main():

    #所有项目列表
    all_list_path = 'E:\\仲瑞泉\\Desktop\\homwork\\科研实践\\统计-项目分析完成度\\04-10-5-cppcheck.txt'

    #统计完成的项目列表
    finished_list_path = 'E:\\仲瑞泉\\Desktop\\homwork\\科研实践\\统计-项目分析完成度\\04-10-infer-npe.txt'

    #查询项目代码量的文件夹
    code_volume_folder_path = 'E:\\仲瑞泉\\Desktop\\homwork\\科研实践\\统计-项目分析完成度\\test'

    # 要进行统计的区间划分
    partitions = [0, 1000, 1000000]
    reverse_partitions = partitions[::-1]

    # 生成 result
    result = {}
    for lower_bound in partitions:
        # 在 result 中为当前区间的下限值创建一个新的字典
        result[lower_bound] = {
            'unfinished': 0,
            'finished': 0
        }

    #开始统计所有项目代码量分布，并置为未完成
    with open(all_list_path, 'r') as all_list:
        for line in all_list:
            # 提取项目名称
            project_name = line.split('/')[-1].split(':')[0]
            # 构建项目代码量文件的路径
            project_cloc_path = os.path.join(code_volume_folder_path, project_name, 'cloc.csv')
            # 检查文件是否存在
            if os.path.exists(project_cloc_path):
                 # 读取cloc.csv文件中的内容
                with open(project_cloc_path, 'r') as file:
                    csv_reader = csv.reader(file)
                    # 统计C/C++行数
                    cloc_lines_sum = 0
                    # 匹配关键行
                    for row in csv_reader:
                        if row[1] in ('C', 'C++', 'C/C++ Header'):
                            cloc_lines_sum += int(row[4])
                    # 判断区间，写入result
                    for pivot in reverse_partitions:
                        if cloc_lines_sum >= pivot:
                            result[pivot]['unfinished'] += 1
                            break       
            else:
                print(f"cloc.csv not found for project: {project_name}")
                return 
            
    #开始统计完成分析的项目
    with open(finished_list_path, 'r') as finished_list:
        for line in finished_list:
            # 提取项目名称
            project_name = line.split('/')[-1].split(':')[0]
            # 构建项目代码量文件的路径
            project_cloc_path = os.path.join(code_volume_folder_path, project_name, 'cloc.csv')
            # 检查文件是否存在
            if os.path.exists(project_cloc_path):
                 # 读取cloc.csv文件中的内容
                with open(project_cloc_path, 'r') as file:
                    csv_reader = csv.reader(file)
                    # 统计C/C++行数
                    cloc_lines_sum = 0
                    # 匹配关键行
                    for row in csv_reader:
                        if row[1] in ('C', 'C++', 'C/C++ Header'):
                            cloc_lines_sum += int(row[4])
                    # 判断区间，写入result
                    for pivot in reverse_partitions:
                        if cloc_lines_sum >= pivot:
                            result[pivot]['unfinished'] -= 1
                            result[pivot]['finished'] += 1
                            break       
            else:
                print(f"cloc.csv not found for project: {project_name}")
                return 

    # 两种情形的样本数据
    data_finished = [] 
    for pivot in partitions:
        data_finished.append(result[pivot]['finished'])
    data_unfinished = []
    for pivot in partitions:
        data_unfinished.append(result[pivot]['unfinished'])
    
    # 绘制直方图
    plt.figure(figsize=(10, 6))

    # 绘制情形1的直方图
    bars1 = plt.bar(range(len(data_finished)), data_finished, color='b', alpha=0.7, label='finished')

    # 绘制情形2的直方图
    bars2 = plt.bar(range(len(data_unfinished)), data_unfinished, color='r', alpha=0.7, bottom=data_unfinished, label='unfinished')

    # 添加数字显示和下半部分的比例显示
    for bar1, bar2 in zip(bars1, bars2):
        height1 = bar1.get_height()
        height2 = bar2.get_height()
        total_height = height1 + height2
        proportion1 = 0
        if total_height != 0:
            proportion1 = height1 / total_height * 100
            proportion2 = height2 / total_height * 100
        if height1 != 0:
            plt.text(bar1.get_x() + bar1.get_width() / 2., height1 / 2, f'{height1}, {proportion1:.2f}%', ha='center', va='bottom')
        if height2 != 0:
            plt.text(bar2.get_x() + bar2.get_width() / 2., height1 + height2 / 2, f'{height2}, {(proportion2):.2f}%', ha='center', va='bottom')

    # 设置横坐标刻度和标签
    plt.xticks(range(len(partitions)), partitions)

    # 添加图例
    plt.legend()

    # 添加标题和标签
    plt.xlabel('code volume')
    plt.ylabel('amount of project')

    # 显示图形
    plt.show()

if __name__ == "__main__":
    main()