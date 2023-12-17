import os
import subprocess
from pathlib import Path


def split_videos(folder_path):
    # 遍历目录下的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp4"):
            file_path = os.path.join(folder_path, filename)

            # 构建输出文件名
            output_filename = os.path.splitext(filename)[0]
            Path(r"F:\wav2lip_tmp\segment_").mkdir(parents=True, exist_ok=True)
            output_filename = os.path.join(r"F:\wav2lip_tmp\segment_", f"{output_filename}_split")

            # 构建 FFmpeg 切分命令
            command = f"ffmpeg -i {file_path} -c copy -map 0 -segment_time 00:00:02 -f segment {output_filename}_%03d.mp4"

            # 执行命令
            subprocess.call(command, shell=True)
            print(f"Splitting {filename}")


# 指定文件夹路径
folder_path = r"F:\wav2lip_tmp\segment"
split_videos(folder_path)
