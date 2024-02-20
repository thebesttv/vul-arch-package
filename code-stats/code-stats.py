import os
import re
import random

# 获取当前脚本所在文件夹的路径
current_directory = os.path.dirname(os.path.abspath(__file__))
# 获取当前文件夹的父文件夹路径
parent_directory = os.path.dirname(current_directory)
# 获取arch文件夹路径
arch_directory = os.path.join(parent_directory, 'arch')

# 统计C/C++行数的统计结果
total_files = 0
count_over_100 = 0
count_100_1000 = 0
count_1000_10000 = 0
count_10000_100000 = 0
count_100000_1000000 = 0
count_1000000_10000000 = 0
count_over_10000000 = 0
folders_over_100 = {}  #key=name，value=num
folders_100_1000 = {}
folders_1000_10000 = {}
folders_10000_100000 = {}
folders_100000_1000000 = {}
folders_1000000_10000000 = {}
folders_over_10000000 = {}

# 遍历arch文件夹下的所有文件夹
for folder_name in os.listdir(arch_directory):
    folder_path = os.path.join(arch_directory, folder_name)
    
    # 检查文件夹是否存在cloc.csv文件
    cloc_file_path = os.path.join(folder_path, 'cloc.csv')
    if os.path.isfile(cloc_file_path):
        # 读取cloc.csv文件中的内容
        with open(cloc_file_path, 'r') as file:
            lines = file.readlines()

        # 统计C/C++行数
        cloc_lines_sum = 0
        # 匹配关键行
        pattern = r'^\d+,(C|C\+\+|C/C\+\+)'
        for line in lines:
            # 检查行是否符合关注行的格式
            if re.match(pattern, line):
                # 获取第四个逗号后面的数字
                numbers = line.split(',')
                if len(numbers) == 5:
                    cloc_lines = int(numbers[4])
                    cloc_lines_sum += cloc_lines
        
        # 更新统计结果
        if cloc_lines_sum > 100:
            count_over_100 += 1
            folders_over_100[folder_name] = cloc_lines_sum
            if cloc_lines_sum > 10000000 :
                folders_over_10000000[folder_name] = cloc_lines_sum
                count_over_10000000 += 1
            elif cloc_lines_sum > 1000000:
                folders_1000000_10000000[folder_name] = cloc_lines_sum
                count_1000000_10000000 += 1
            elif cloc_lines_sum > 100000:
                folders_100000_1000000[folder_name] = cloc_lines_sum
                count_100000_1000000 += 1
            elif cloc_lines_sum > 10000:
                folders_10000_100000[folder_name] = cloc_lines_sum
                count_10000_100000 += 1
            elif cloc_lines_sum > 1000:
                folders_1000_10000[folder_name] = cloc_lines_sum
                count_1000_10000 += 1
            else :
                folders_100_1000[folder_name] = cloc_lines_sum
                count_100_1000 += 1
        total_files += 1

# 计算C/C++行数在所有文件中的比例
percentage_over_100 = count_over_100 / total_files * 100
percentage_100_1000 = count_100_1000 / total_files * 100
percentage_1000_10000 = count_1000_10000 / total_files * 100
percentage_10000_100000 = count_10000_100000 / total_files * 100
percentage_100000_1000000 = count_100000_1000000 / total_files * 100
percentage_1000000_10000000 = count_1000000_10000000 / total_files * 100
percentage_over_10000000 = count_over_10000000 / total_files * 100

# 将统计结果导出到文件中
result_file_path = os.path.join(current_directory, 'code-stats-result.txt')
with open(result_file_path, 'w') as file:
    file.write(f'可用(C/C++行数大于100)文件数量: {count_over_100}\n')
    file.write(f'可用(C/C++行数大于100)文件比例: {percentage_over_100:.2f}%\n')
    file.write(f'C/C++行数在100~1000之间的文件数量: {count_100_1000}\n')
    file.write(f'C/C++行数在100~1000之间的文件比例: {percentage_100_1000:.2f}%\n')
    selected_folders = random.sample(list(folders_100_1000.keys()), 3)
    for folder_name in selected_folders:
        file.write(f'举例: {folder_name},代码行数:{folders_100_1000[folder_name]}\n')
    file.write(f'C/C++行数在1000~10000之间的文件数量: {count_1000_10000}\n')
    file.write(f'C/C++行数在1000~10000之间的文件比例: {percentage_1000_10000:.2f}%\n')
    selected_folders = random.sample(list(folders_1000_10000.keys()), 3)
    for folder_name in selected_folders:
        file.write(f'举例: {folder_name},代码行数:{folders_1000_10000[folder_name]}\n')
    file.write(f'C/C++行数在10000~100000之间的文件数量: {count_10000_100000}\n')
    file.write(f'C/C++行数在10000~100000之间的文件比例: {percentage_10000_100000:.2f}%\n')
    selected_folders = random.sample(list(folders_10000_100000.keys()), 3)
    for folder_name in selected_folders:
        file.write(f'举例: {folder_name},代码行数:{folders_10000_100000[folder_name]}\n')
    file.write(f'C/C++行数在100000~1000000之间的文件数量: {count_100000_1000000}\n')
    file.write(f'C/C++行数在100000~1000000之间的文件比例: {percentage_100000_1000000:.2f}%\n')
    selected_folders = random.sample(list(folders_100000_1000000.keys()), 3)
    for folder_name in selected_folders:
        file.write(f'举例: {folder_name},代码行数:{folders_100000_1000000[folder_name]}\n')
    file.write(f'C/C++行数在1000000~10000000之间的文件数量: {count_1000000_10000000}\n')
    file.write(f'C/C++行数在1000000~10000000之间的文件比例: {percentage_1000000_10000000:.2f}%\n')
    selected_folders = random.sample(list(folders_1000000_10000000.keys()), 3)
    for folder_name in selected_folders:
        file.write(f'举例: {folder_name},代码行数:{folders_1000000_10000000[folder_name]}\n')
    file.write(f'C/C++行数大于10000000的文件数量: {count_over_10000000}\n')
    file.write(f'C/C++行数大于10000000的文件比例: {percentage_over_10000000:.2f}%\n')
    selected_folders = random.sample(list(folders_over_10000000.keys()), 3)
    for folder_name in selected_folders:
        file.write(f'举例: {folder_name},代码行数:{folders_over_10000000[folder_name]}\n')
result_file_path = os.path.join(current_directory, 'all-useable-package-names.txt')
with open(result_file_path, 'w') as file:
    folder_names_over_100 = list(folders_over_100.keys())
    folder_names_over_100.sort()
    for folder_name in folder_names_over_100:
        file.write(f'{folder_name}\n')