import os
import librosa
import numpy as np
from moviepy.editor import VideoFileClip
import concurrent.futures
from moviepy.video.io.VideoFileClip import VideoFileClip
from pydub import AudioSegment, silence


def split_video_by_pause(input_video_path, output_prefix):
    """
    将视频按说话人语句停顿的点进行切分，并输出为多个视频文件。
    :param input_video_path: 输入视频文件路径
    :param output_prefix: 输出视频文件名前缀
    """
    # 将视频转换为音频
    clip = VideoFileClip(input_video_path)
    audio_path = f'{output_prefix}.wav'
    clip.audio.write_audiofile(audio_path, fps=16000)

    # 读取音频数据
    y, sr = librosa.load(audio_path, sr=16000)

    # 加窗
    win_length = int(sr * 0.025)  # 帧长为25ms
    hop_length = int(sr * 0.01)  # 步长为10ms
    y_frames = librosa.util.frame(y, frame_length=win_length, hop_length=hop_length)
    window = np.hamming(win_length).reshape((-1, 1))
    y_frames = y_frames * window

    # 短时傅里叶变换
    y_stfts = librosa.core.stft(y_frames, n_fft=win_length, hop_length=hop_length)
    y_mag, _ = librosa.core.magphase(y_stfts)
    y_logspec = librosa.amplitude_to_db(y_mag, ref=np.max)

    # 计算每帧第一阶段差分（delta）的平方和
    delta1 = librosa.feature.delta(y_logspec, order=1)
    delta1_sum = np.sum(delta1 ** 2, axis=0)

    # 计算每帧第二阶段差分（delta-delta）的平方和
    delta2 = librosa.feature.delta(y_logspec, order=2)
    delta2_sum = np.sum(delta2 ** 2, axis=0)

    # 计算每帧总能量
    energy = np.sum(y_mag ** 2, axis=0)

    # 计算每帧过零率
    zcr = librosa.feature.zero_crossing_rate(y_frames, hop_length=hop_length)

    # 计算语句停顿点位置
    energy_delta = np.diff(energy)
    energy_delta2 = np.diff(energy_delta)

    pause_indexes = []
    for i in range(2, len(energy_delta2)):
        if energy_delta[i - 1].all() > 0 and energy_delta2[i - 2].all() < 0:
            pause_indexes.append(i)

    # 切割视频
    start_time = 0
    for idx, pause_index in enumerate(pause_indexes):
        end_time = (pause_index + 1) * hop_length / sr
        subclip = clip.subclip(start_time, end_time)
        subclip.write_videofile(f'{output_prefix}_{idx}.mp4')
        start_time = end_time

    # 删除音频文件
    os.remove(audio_path)


def split_video_by_silence(video_file_path, output_prefix, min_silence_len=50, silence_thresh=-50, max_workers=None):
    """
    根据语音停顿位置切分视频。

    Args:
        video_file_path (str): 视频文件路径。
        min_silence_len (int): 最小静默长度，单位毫秒。默认为500毫秒。
        silence_thresh (int): 静默阈值，单位分贝。默认为-50分贝。
        max_workers (int): 最大工作线程数。默认为None，表示不限制。

    Returns:
        bool: 是否成功切分了视频。
    """
    # 从视频文件中提取音频
    video = VideoFileClip(video_file_path)
    audio = video.audio

    # 将音频转换为AudioSegment对象并保存为WAV文件
    audio_file_path = f'{video_file_path}.wav'
    audio.write_audiofile(audio_file_path, codec='pcm_s16le')

    audio_seg = AudioSegment.from_file(audio_file_path, format='wav')

    # 对音频进行预处理（如滤波、降噪等）

    # 使用silence.detect_nonsilent函数查找音频中的停顿点
    nonsilent_parts = silence.detect_nonsilent(audio_seg, min_silence_len=min_silence_len,
                                               silence_thresh=silence_thresh)

    # 根据停顿点进行音频切分和导出
    success = False
    if len(nonsilent_parts) > 0:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

        futures = []
        for i, part in enumerate(nonsilent_parts):
            start_time, end_time = part[0], part[1]

            # 使用Pydub进行音频切分
            speech_clip = audio_seg[start_time:end_time]

            # 将音频剪辑保存为WAV文件
            # clip_file_path = f'{video_file_path}_{i}.wav'
            if output_prefix is None:
                clip_file_path = f'{os.path.splitext(video_file_path)[0]}_{i}.wav'
            else:
                clip_file_path = os.path.join(output_prefix,
                                              f'{os.path.splitext(os.path.basename(video_file_path))[0]}_{i}.wav')
            futures.append(executor.submit(speech_clip.export, clip_file_path, format='wav'))

            # 将音频剪辑与原视频进行同步，得到对应的视频剪辑
            video_clip = video.subclip(start_time / 1000, end_time / 1000)

            # 将视频剪辑保存为MP4文件
            # clip_video_file_path = f'{video_file_path}_{i}.mp4'
            if output_prefix is None:
                clip_video_file_path = f'{os.path.splitext(video_file_path)[0]}_{i}.mp4'
            else:
                clip_video_file_path = os.path.join(output_prefix,
                                                    f'{os.path.splitext(os.path.basename(video_file_path))[0]}_{i}.mp4')
            futures.append(executor.submit(video_clip.write_videofile, clip_video_file_path))

            # 释放资源
            # speech_clip.close()
            video_clip.close()

        # 等待所有任务完成
        concurrent.futures.wait(futures)

        # 释放资源
        # audio_seg.close()
        audio.close()
        video.close()

        success = True

    return success


if __name__ == "__main__":
    input_video_path = r'D:\lgd\download\601112\result1.mp4'
    output_prefix = r'D:\lgd\human_videos\601112'
    # split_video_by_pause(input_video_path, output_prefix)

    split_video_by_silence(input_video_path, output_prefix)
