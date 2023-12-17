import os
from moviepy.editor import VideoFileClip, concatenate_videoclips


def merge_videos(directory_path, output_file_name='result.mp4'):
    """
    合并指定目录下所有后缀为MP4的视频文件。

    Args:
        directory_path (str): 指定的目录路径。
        output_file_name (str): 要输出的合并后视频文件名。默认为'result.mp4'。
    """
    # 获取目录下的所有符合条件的文件
    file_list = os.listdir(directory_path)
    mp4_files = [file for file in file_list if file.endswith('.mp4')]
    mp4_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))  # 按照文件编号排序

    # 生成FFmpeg命令行并执行
    # cmd = 'ffmpeg -i concat:'
    # for mp4_file in mp4_files:
    #     input_file_path = os.path.join(directory_path, mp4_file)
    #     cmd += ' -i {} '.format(input_file_path)
    # cmd += '-filter_complex "concat=n={}:v=1:a=1" -c:v copy -c:a copy {}'.format(len(mp4_files), output_file_name)

    cmd = 'ffmpeg'
    for mp4_file in mp4_files:
        input_file_path = os.path.join(directory_path, mp4_file)
        cmd += ' -i {} '.format(input_file_path)
    cmd += '-filter_complex "concat=n={}:v=1:a=1 [v] [a]" -map "[v]" -map "[a]" {}'.format(len(mp4_files), output_file_name)
    os.system(cmd)



def mp4_file_to_video_clip(file_path):
    try:
        return VideoFileClip(file_path)
    except:
        print(f"Cannot read file {file_path}, skip.")
        return None


def merge_videos_moviepy_v2(directory_path, output_file_name='result.mp4', clip_func=mp4_file_to_video_clip, num_clips_per_group=300):
    """
    分批合并指定目录下所有后缀为MP4的视频文件。

    Args:
        directory_path (str): 指定的目录路径。
        output_file_name (str): 要输出的合并后视频文件名。默认为'result.mp4'。
        clip_func (function): 将mp4文件路径转换为视频剪辑的函数，默认为mp4_file_to_video_clip。
        num_clips_per_group (int): 每组合并多少个视频，为避免内存占用过多，默认为300个。
    """
    # 获取目录下的所有符合条件的文件
    file_list = os.listdir(directory_path)
    mp4_files = [file for file in file_list if file.endswith('.mp4')]
    mp4_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))  # 按照文件编号排序

    # 将所有视频进行拼接
    video_clips = []
    for i in range(0, len(mp4_files), num_clips_per_group):
        clips_group = [clip_func(os.path.join(directory_path, mp4_file)) for mp4_file in mp4_files[i:i+num_clips_per_group]]
        clips_group = [clip for clip in clips_group if clip is not None]
        if len(clips_group) > 0:
            video_clips.append(concatenate_videoclips(clips_group))
            for clip in clips_group:
                clip.close()

    if len(video_clips) > 0:
        final_video_clip = concatenate_videoclips(video_clips)

        # 保存合成的视频
        final_video_clip.write_videofile(output_file_name)

        # 关闭视频文件
        final_video_clip.close()
        for video_clip in video_clips:
            video_clip.close()
    else:
        print("No valid video clips found.")



def merge_videos_moviepy_v1(directory_path, output_file_name='result.mp4', clip_func=mp4_file_to_video_clip, num_clips_per_group=200):
    """
    合并指定目录下所有后缀为MP4的视频文件。

    Args:
        directory_path (str): 指定的目录路径。
        output_file_name (str): 要输出的合并后视频文件名。默认为'result.mp4'。
        clip_func (function): 将mp4文件路径转换为视频剪辑的函数，默认为mp4_file_to_video_clip。
    """
    # 获取目录下的所有符合条件的文件
    file_list = os.listdir(directory_path)
    mp4_files = [file for file in file_list if file.endswith('.mp4')]
    mp4_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))  # 按照文件编号排序

    # 将所有视频进行拼接
    for i in range(200, len(mp4_files), num_clips_per_group):
        clips_group = [clip_func(os.path.join(directory_path, mp4_file)) for mp4_file in
                       mp4_files[i:i + num_clips_per_group]]
        video_clips = [clip for clip in clips_group if clip is not None]
        final_video_clip = concatenate_videoclips(video_clips)

        # 保存合成的视频
        final_video_clip.write_videofile(output_file_name.format(str(i)))

        # 关闭视频文件
        final_video_clip.close()
        for video_clip in video_clips:
            video_clip.close()



if __name__ == "__main__":
    # merge_videos(r"D:\lgd\download\601112",r"D:\lgd\download\601112\result2.mp4")
    merge_videos_moviepy_v1(r"D:\lgd\download\601112",r"D:\lgd\download\601112\result_{}.mp4")