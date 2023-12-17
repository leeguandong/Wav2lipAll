import os

def rename_files(folder_path):
    file_list = os.listdir(folder_path)
    file_count = len(file_list)

    for i in range(file_count):
        old_name = os.path.join(folder_path, file_list[i])
        new_name = os.path.join(folder_path, str(i+1) + os.path.splitext(file_list[i])[1])
        os.rename(old_name, new_name)
        print(f"Renaming {old_name} to {new_name}")

# 指定文件夹路径
folder_path = r"F:\wav2lip_tmp\kaoyan"
rename_files(folder_path)


