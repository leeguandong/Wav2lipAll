import os
import srt
import opencc
import whisper
import logging
import datetime
import traceback
from tqdm import tqdm
import moviepy.editor as mp
from pathlib import Path
from glob import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

sampling_rate = 16000
ngpu = 2

whisper_model = [whisper.load_model("small", "cuda:{}".format(id),
                                    download_root="/home/tmp_package/image_team_docker_home/lgd/wav2lip_tools/") for id
                 in range(ngpu)]


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


def split_video_by_whisper(vfile, output_prefix, gpu_id):
    #import pdb;pdb.set_trace()
    #for mp4_ in vfile:
    audio = whisper.load_audio(vfile, sr=sampling_rate)  # sr=16000
    result = whisper_model[gpu_id].transcribe(audio, task='transcribe', language='zh')
    _save_srt_video(vfile, output_prefix, result)
    logging.info(f"Transcribed {vfile} to {output_prefix}")

def mp_handler(job):
    vfile, output_prefix, gpu_id = job
    try:
        split_video_by_whisper(vfile, output_prefix, gpu_id)
    except KeyboardInterrupt:
        exit(0)
    except:
        traceback.print_exc()


if __name__ == "__main__":
    directory_path = "/home/tmp_package/image_team_docker_home/lgd/wav2lip_tools/data/cctv_news/"
    filelist = glob(os.path.join(directory_path, '*.mp4'))
    save_path = "/home/tmp_package/image_team_docker_home/lgd/wav2lip_tools/resultsv3/"

    jobs = [(vfile, save_path, i % ngpu) for i, vfile in enumerate(filelist)]
    p = ThreadPoolExecutor(ngpu)
    futures = [p.submit(mp_handler, j) for j in jobs]
    _ = [r.result() for r in tqdm(as_completed(futures), total=len(futures))]