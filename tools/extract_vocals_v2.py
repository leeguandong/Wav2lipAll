import os
from glob import glob
from moviepy.editor import VideoFileClip, AudioFileClip
from spleeter.separator import Separator
from pathlib import Path

separator = Separator('spleeter:2stems')

# 提取音频文件
def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)


def separate_vocals(audio_path, vocals_path):
    separator.separate_to_file(audio_path, vocals_path)


# 去除背景音
def remove_background(video_path, no_bg_path, vocals_path):
    vocals = AudioFileClip(vocals_path)
    video = VideoFileClip(video_path)
    video = video.set_audio(vocals)
    video.write_videofile(no_bg_path)


def main():
    # 视频文件路径
    video_path = glob(os.path.join(r"E:\common_tools\wav2lip_tools\wav2lip_tools\data", '*.mp4'))
    save_path = ""
    Path(save_path).mkdir(parents=True, exist_ok=True)

    for video in video_path:
        # 音频文件路径
        audio_path = os.path.join(save_path, f"audio/{Path(video).stem}.wav")
        Path(os.path.join(save_path, "audio")).mkdir(parents=True, exist_ok=True)

        # 分离人声后的音频文件路径
        vocals_path = os.path.join(save_path, "output_vocals")
        Path(vocals_path).mkdir(parents=True, exist_ok=True)

        # 去除背景音后的音频文件路径
        no_bg_path = os.path.join(save_path, f"output_no_bg/{Path(video).stem}.mp4")
        Path(os.path.join(save_path, "output_no_bg")).mkdir(parents=True, exist_ok=True)

        # 提取音频
        extract_audio(video, audio_path)

        # 分离人声
        separate_vocals(audio_path, vocals_path)

        # 去除背景音
        vocals_path_ = os.path.join(vocals_path, f"{Path(video).stem}/vocals.wav")
        remove_background(video, no_bg_path, vocals_path_)


if __name__ == "__main__":
    main()
