import os
import subprocess
from pathlib import Path

def split_videos(folder_path):
    # 遍历目录下的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp4"):
            file_path = os.path.join(folder_path, filename)

            # 获取视频总时长
            command_duration = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {file_path}"
            output_duration = subprocess.check_output(command_duration, shell=True)
            total_duration = float(output_duration)

            # 计算切割片段的个数
            num_segments = int(total_duration / 2)

            # 构建输出文件名
            output_filename = os.path.splitext(filename)[0]
            Path(r"F:\wav2lip_tmp\segment_").mkdir(parents=True,exist_ok=True)
            output_filename = os.path.join(r"F:\wav2lip_tmp\segment_",f"{output_filename}_split")
            # output_filename = f"{output_filename}_split"

            # 逐个切割片段
            for i in range(num_segments):
                start_time = i * 2
                segment_name = f"{output_filename}_{i:03}.mp4"
                command_split = f"ffmpeg -ss {start_time} -i {file_path} -t 2 -c copy {segment_name}"
                subprocess.call(command_split, shell=True)

                print(f"Splitting {filename} - Segment {i+1}/{num_segments}")

# 指定文件夹路径
folder_path = r"F:\wav2lip_tmp\segment"
split_videos(folder_path)
