import os
import subprocess
from multiprocessing import Pool


def convert_video(input_file, output_folder):
    filename = os.path.basename(input_file)
    output_file = os.path.join(output_folder, "output_" + filename)

    command = f"ffmpeg -i {input_file} -ss 1 -t 3 {output_file} -y"
    subprocess.call(command, shell=True)


def main():
    input_folder = r"F:\wav2lip_tmp\sftv1"
    output_folder = r"F:\wav2lip_tmp\sftv1_crop"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    files = os.listdir(input_folder)
    pool = Pool(processes=1)  # 使用所有可用的CPU核心数量作为进程池大小

    for file in files:
        if file.endswith(".mp4"):
            input_file = os.path.join(input_folder, file)
            pool.apply_async(convert_video, args=(input_file, output_folder))

    pool.close()
    pool.join()


if __name__ == "__main__":
    main()
