import os
import srt
import opencc
import logging
import datetime
from tqdm import tqdm
import moviepy.editor as mp
from pathlib import Path
import torch
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, Dataset
import whisper

os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
sampling_rate = 16000

whisper_model = whisper.load_model("small", "cuda",
                                   download_root="/home/tmp_package/image_team_docker_home/lgd/wav2lip_tools/")


class VideoDataset(Dataset):
    def __init__(self, video_files):
        self.video_files = video_files

    def __len__(self):
        return len(self.video_files)

    def __getitem__(self, idx):
        return self.video_files[idx]


def _save_video_clip(original_file_path, output_prefix, start_time, end_time):
    clip_file_path = Path(output_prefix, f"{Path(original_file_path).stem}_{start_time:.4f}-{end_time:.4f}.mp4")
    original_clip = mp.VideoFileClip(original_file_path)
    clip = original_clip.subclip(start_time, end_time)
    clip.write_videofile(str(clip_file_path))
    logging.info(f"Clipped {original_file_path} to {clip_file_path}")


def _save_srt_video(video_file_path, output_prefix, transcribe_results):
    subs = []
    cc = opencc.OpenCC("t2s")  # convert traditional Chinese to simplified Chinese

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
        if start > prev_end + 1.0:
            _add_sub(prev_end, start, "< No Speech >")
        _add_sub(start, end, s["text"])
        _save_video_clip(video_file_path, output_prefix, start, end)
        prev_end = end

    output_prefix = Path(output_prefix, Path(video_file_path).stem + ".srt")
    with open(output_prefix, "wb") as f:
        f.write(srt.compose(subs).encode("utf-8", "replace"))


def split_video_by_whisper(video_files, output_prefix, device):
    for video_file in video_files:
        audio = whisper.load_audio(video_file, sr=sampling_rate)
        result = whisper_model.transcribe(audio, task='transcribe', language='zh')
        _save_srt_video(video_file, output_prefix, result)
        logging.info(f"Transcribed {video_file} to {output_prefix}")


def main():
    directory_path = "/home/tmp_package/image_team_docker_home/lgd/wav2lip_tools/data/human_videosv1/human_videosv1/"
    file_list = os.listdir(directory_path)
    import pdb;pdb.set_trace()
    folder_list = ["602547", "601716", "601557", "602956"]

    # Initialize distributed training
    dist.init_process_group(backend='nccl', init_method='tcp://localhost:12345', world_size=torch.cuda.device_count(),
                            rank=0)

    # Create model and move it to GPU
    model = whisper.load_model("small", "cuda")
    model = model.to(torch.device("cuda"))
    model = DDP(model, device_ids=[0, 1])
    model.eval()

    # Create video dataset
    video_files = [os.path.join(directory_path, folder) for folder in folder_list]
    dataset = VideoDataset(video_files)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

    for video_batch in tqdm(dataloader):
        video_batch = video_batch[0]
        video_batch = [video.replace("\\", "/") for video in video_batch]  # Use forward slash to handle paths
        split_video_by_whisper(video_batch, output_prefix, device=torch.device("cuda"))

    dist.destroy_process_group()


if __name__ == "__main__":
    output_prefix = "/home/tmp_package/image_team_docker_home/lgd/wav2lip_tools/resultsv1/"
    Path(output_prefix).mkdir(parents=True, exist_ok=True)
    main()