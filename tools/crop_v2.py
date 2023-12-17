import os
import subprocess
from multiprocessing import Pool
from pathlib import Path


def convert_video(input_file, output_folder):
    filename = os.path.basename(input_file)
    output_folder = os.path.join(output_folder, Path(input_file).parent.stem)
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    output_file = os.path.join(output_folder, "output_" + filename)

    command = f"ffmpeg -i {input_file} -ss 1 -t 3 {output_file} -y"
    subprocess.call(command, shell=True)


def process_folder(input_folder, output_folder, pool):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".mp4"):
                input_file = os.path.join(root, file)
                pool.apply_async(convert_video, args=(input_file, output_folder))


def main():
    input_folder = r"F:\wav2lip_tmp\sftv1"
    output_folder = r"F:\wav2lip_tmp\sftv1_crop"

    pool = Pool(processes=1)  # 使用所有可用的CPU核心数量作为进程池大小

    process_folder(input_folder, output_folder, pool)

    pool.close()
    pool.join()


if __name__ == "__main__":
    main()
