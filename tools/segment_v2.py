from moviepy.editor import VideoFileClip
import os
from pathlib import Path

def split_videos(folder_path):
    # 遍历目录下的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp4"):
            file_path = os.path.join(folder_path, filename)
            output_filename = os.path.splitext(filename)[0]
            Path(r"F:\wav2lip_tmp\segment_").mkdir(parents=True,exist_ok=True)
            output_filename = os.path.join(r"F:\wav2lip_tmp\segment_",f"{output_filename}_split")

            # 使用MoviePy加载视频
            video_clip = VideoFileClip(file_path)

            # 计算每个切割片段的起始和结束时间
            start_time = 0
            end_time = 2

            # 切割视频并保存每个片段
            segment_index = 1
            while end_time <= video_clip.duration:
                # 提取指定时间段的视频片段
                segment_clip = video_clip.subclip(start_time, end_time)

                # 构建输出文件名
                segment_name = f"{output_filename}_{segment_index:03}.mp4"

                # 保存切割片段
                segment_clip.write_videofile(segment_name, codec="libx264")

                # 更新时间段和索引
                start_time += 2  # 增加2秒作为下一个片段的起始时间
                end_time += 2  # 增加2秒作为下一个片段的结束时间
                segment_index += 1

                print(f"Splitting {filename} - Segment {segment_index}")

            # 释放资源
            video_clip.close()

# 指定文件夹路径
folder_path = r"F:\wav2lip_tmp\segment"
split_videos(folder_path)
