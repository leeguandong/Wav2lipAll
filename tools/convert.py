import os
from pathlib import Path
from multiprocessing import Pool


def convert(ts_file, single_file_path):
    mp4_file = Path(single_file_path, Path(ts_file).stem + ".mp4")
    os.system(f'ffmpeg -i {ts_file} -c:v libx264 -r 25  {mp4_file}')
    os.remove(ts_file)


def convert_fps(orign_path, single_file_path):
    mp4_file = Path(single_file_path, "fandengdushu" + Path(orign_path).stem + ".mp4")
    os.system(f'ffmpeg -i {orign_path} -c:v libx264 -r 25  {mp4_file}')
    # os.remove(ts_file)


def convert_ts_to_mp4(ts_folder, mp4_folder, num_workers):
    ts_files = [str(ts) for ts in Path(ts_folder).glob("*.mp4")]
    with Pool(processes=num_workers) as pool:
        pool.starmap(convert_fps, [(ts, mp4_folder) for ts in ts_files])
    print('转成MP4，fps=25')


if __name__ == "__main__":
    # convert_ts_to_mp4(r"F:\wav2lip_tmp\604943", r"F:\wav2lip_tmp\604943", num_workers=2)
    convert_ts_to_mp4(r"F:\wav2lip_tmp\fandengdushu", r"F:\wav2lip_tmp\fandengdushu_", num_workers=1)
