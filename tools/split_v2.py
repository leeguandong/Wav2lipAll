import os
import srt
import opencc
import whisper
import logging
import datetime
from tqdm import tqdm
import moviepy.editor as mp
from pathlib import Path

sampling_rate = 16000

whisper_model = whisper.load_model("small", "cuda",
                                   download_root="/home/tmp_package/image_team_docker_home/lgd/wav2lip_tools/")


def _save_video_clip(original_file_path, output_prefix, start_time, end_time):
    clip_file_path = Path(output_prefix, f"{Path(original_file_path).stem}_{start_time:.4f}-{end_time:.4f}.mp4")
    original_clip = mp.VideoFileClip(original_file_path)
    clip = original_clip.subclip(start_time, end_time)
    clip.write_videofile(str(clip_file_path))
    logging.info(f"Clipped {original_file_path} to {clip_file_path}")


def _save_srt_video(video_file_path, output_prefix, transcribe_results):
    subs = []
    # whisper sometimes generate traditional chinese, explicitly convert
    cc = opencc.OpenCC("t2s")

    def _add_sub(start, end, text):
        subs.append(
            srt.Subtitle(
                index=0,
                start=datetime.timedelta(seconds=start),
                end=datetime.timedelta(seconds=end),
                content=cc.convert(text.strip()),
            )
        )

    prev_end = 0
    for s in transcribe_results["segments"]:
        start = s['start']
        end = s['end']
        if start > end:
            continue
        # mark any empty segment that is not very short
        if start > prev_end + 1.0:
            _add_sub(prev_end, start, "< No Speech >")
        _add_sub(start, end, s["text"])
        _save_video_clip(video_file_path, output_prefix, start, end)
        prev_end = end

    output_prefix = Path(output_prefix, Path(video_file_path).stem + ".srt")
    with open(output_prefix, "wb") as f:
        f.write(srt.compose(subs).encode("utf-8", "replace"))


def split_video_by_whisper(video_file_path, output_prefix):
    file_list = os.listdir(video_file_path)
    mp4_files = [os.path.join(directory_path+name,file) for file in file_list if file.endswith('.mp4')]

    for mp4_ in mp4_files:
        audio = whisper.load_audio(mp4_, sr=sampling_rate)  # sr=16000
        result = whisper_model.transcribe(audio, task='transcribe', language='zh')
        _save_srt_video(mp4_, output_prefix, result)
        logging.info(f"Transcribed {video_file_path} to {output_prefix}")


if __name__ == "__main__":
    directory_path = "/home/tmp_package/image_team_docker_home/lgd/wav2lip_tools/data/"
    file_list = os.listdir(directory_path)
    # 过滤出所有文件夹
    folder_list = [folder for folder in file_list if
                   os.path.isdir(os.path.join(directory_path, folder)) and 'ipynb_checkpoints' not in folder]
    # folder_list = [
    #     #         '601642', '603011', '604500', '605903',
    #     '606075', '606805', '607175', '605805', '604645', '607272', '608815', '610047', '601426', '601543', '601609',
    #     '601652', '601814', '601866', '601894', '601984', '602057', '602475', '602089', '602709', '602848', '602880',
    #     '603436'
    # ]

    for folder in tqdm(folder_list):
        video = os.path.join(directory_path, folder)
        name = os.path.basename(video)
        save_path = "/home/tmp_package/image_team_docker_home/lgd/wav2lip_tools/results/" + name
        Path(save_path).mkdir(parents=True, exist_ok=True)
        try:
            split_video_by_whisper(video, save_path)
        except:
            continue

    # split_video_by_whisper(r"F:\wav2lip_tmp\601112\1672544583_2.mp4", r"F:\wav2lip_tmp\601112")

    # pip install openai-whisper
