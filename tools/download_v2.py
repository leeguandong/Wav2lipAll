import os
import re
import requests
from multiprocessing import Pool
from pathlib import Path
from tqdm import tqdm

num_workers = 4  # 进程数调整为4，可以根据实际情况进行调整


def extract_links_from_file(file_path):
    with open(file_path, 'r') as f:
        txt = f.read()
    links = re.findall(r'http://[^\s]+', txt)
    formatted_links = [link.rstrip('"') for link in links]
    return formatted_links


# 下载m3u8视频的ts切片
def download_ts(ts_url, single_file_path):
    ts_content = requests.get(ts_url).content
    ts_name = os.path.basename(ts_url)
    with open(os.path.join(single_file_path, ts_name), 'wb') as f:
        f.write(ts_content)
    return ts_name


# 下载m3u8视频及其ts切片
def download_m3u8_video(url, single_file_path):
    r = requests.get(url)
    if r.status_code != 200:
        print('m3u8视频下载链接无效')
        return False

    m3u8_list = r.text.split('\n')
    m3u8_list = [i for i in m3u8_list if i and i[0] != '#']

    ts_list = [url.rsplit('/', 1)[0] + '/' + ts_url for ts_url in m3u8_list]
    if len(ts_list) > 1000:
        ts_list = ts_list[:1000]

    with open(os.path.join(single_file_path, 'urls.txt'), 'w') as f:
        for url in ts_list:
            f.write(url + '\n')

    with Pool(processes=num_workers) as pool:
        ts_files = (pool.starmap(download_ts, [(ts, single_file_path) for ts in ts_list]))
    ts_files = [os.path.join(single_file_path, ts_file) for ts_file in ts_files]
    print('m3u8视频下载完成')
    return ts_files


# 将单个ts切片转换为mp4格式
def convert(ts_file, single_file_path):
    mp4_file = Path(single_file_path, Path(ts_file).stem + ".mp4")
    os.system(f'ffmpeg -i {ts_file} -c:v libx264 -r 25  {mp4_file}')


# 将多个ts切片转换为mp4格式
def convert_ts_to_mp4(ts_file_path, single_file_path):
    with Pool(processes=num_workers) as pool:
        pool.starmap(convert, [(ts, single_file_path) for ts in ts_file_path])
    print('转成MP4，fps=25')


# 删除ts切片
def remove_ts_files(dirname):
    for filename in os.listdir(dirname):
        if filename.endswith('.ts'):
            file_path = os.path.join(dirname, filename)
            os.remove(file_path)


# 合并多个mp4片段
def merge_videos(directory_path, output_file_name='result.mp4'):
    file_list = os.listdir(directory_path)
    mp4_files = [file for file in file_list if file.endswith('.mp4')]
    mp4_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    cmd = 'ffmpeg'
    for mp4_file in mp4_files:
        input_file_path = os.path.join(directory_path, mp4_file)
        cmd += ' -i {} '.format(input_file_path)
    cmd += '-filter_complex "concat=n={}:v=1:a=1 [v] [a]" -map "[v]" -map "[a]" {}'.format(len(mp4_files),
                                                                                           output_file_name)
    os.system(cmd)


# 删除非result.mp4的mp4文件
def remove_mp4_files_except_result(dir_path):
    for file_name in os.listdir(dir_path):
        if file_name.endswith('.mp4') and file_name != 'result.mp4':
            os.remove(os.path.join(dir_path, file_name))


if __name__ == '__main__':
    url_txt = "./backlist.txt"
    file_path = 'D:/lgd/download'

    txt = extract_links_from_file(url_txt)
    for single in tqdm(txt[11:50]):
        single_file_path = Path(file_path, Path(single).stem)
        single_file_path.mkdir(parents=True, exist_ok=True)
        ts_name_lists = download_m3u8_video(single, single_file_path)

        if ts_name_lists:
            convert_ts_to_mp4(ts_name_lists, single_file_path)

        remove_ts_files(single_file_path)

        try:
            merge_videos(single_file_path, os.path.join(single_file_path, "result.mp4"))
        except:
            print("merge视频出现问题")

        # remove_mp4_files_except_result(single_file_path)
