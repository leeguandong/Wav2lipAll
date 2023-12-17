from moviepy.editor import VideoFileClip, AudioFileClip
from spleeter.separator import Separator
from pathlib import Path


# 提取音频文件
def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)


def separate_vocals(audio_path, vocals_path):
    separator = Separator('spleeter:2stems')
    # 在separator = Separator('spleeter:2stems')中，2stems是指将音频分离为两个音轨 / 声部，即主唱（vocals）和伴奏（accompaniment）。也就是说，Spleeter
    # 会尝试将音频中的人声和伴奏分离为两个独立的音频文件。
    # 如果你想要更多的音轨分离，可以尝试使用其他的配置，例如：
    # spleeter: 4
    # stems：将音频分离为四个音轨，包括主唱、鼓、低音和其他乐器。
    # spleeter: 5
    # stems：将音频分离为五个音轨，包括主唱、鼓、低音、钢琴和其他乐器。
    separator.separate_to_file(audio_path, vocals_path)


# 去除背景音
def remove_background(video_path, no_bg_path, vocals_path):
    vocals = AudioFileClip(vocals_path)
    video = VideoFileClip(video_path)
    video = video.set_audio(vocals)
    video.write_videofile(no_bg_path)


def main():
    # 视频文件路径
    video_path = "data/61.mp4"

    # 音频文件路径
    audio_path = "data/output_audio.wav"

    # 分离人声后的音频文件路径
    vocals_path = "output_vocals"

    # 去除背景音后的音频文件路径
    no_bg_path = "output_no_bg.mp4"

    # 提取音频
    extract_audio(video_path, audio_path)

    # 分离人声
    separate_vocals(audio_path, vocals_path)

    # 去除背景音
    vocals_path = vocals_path + "/" + str(Path(audio_path).stem) + "/vovals.wav"
    vocals_path_ = r"E:\common_tools\wav2lip_tools\wav2lip_tools\output_vocals\output_audio\vocals.wav"
    remove_background(video_path, no_bg_path, vocals_path_)


if __name__ == "__main__":
    main()
