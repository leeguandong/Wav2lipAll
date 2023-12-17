import os
import re
import requests
from multiprocessing.dummy import Pool  # dummy表示使用线程池
from pathlib import Path
from tqdm import tqdm

num_workers = 2


def extract_links_from_file(file_path):
    with open(file_path, 'r') as f:
        txt = f.read()
    links = re.findall(r'http://[^\s]+', txt)
    formatted_links = [link.rstrip('"') for link in links]
    return formatted_links


def download_ts(ts_url):
    ts_content = requests.get(ts_url).content
    ts_name = os.path.basename(ts_url)
    with open(os.path.join(single_file_path, ts_name), 'wb') as f:
        f.write(ts_content)
    return ts_name


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
    # ts_list = ts_list[:int(len(ts_list) / 4)] # 下个1/4
    # ts_list = ts_list[:3]

    # 可以将链接保存下来
    with open(os.path.join(single_file_path, 'urls.txt'), 'w') as f:
        for url in ts_list:
            f.write(url + '\n')

    pool = Pool(processes=num_workers)
    ts_files = (pool.map(download_ts, ts_list))
    pool.close()
    pool.join()

    # ts_files = []
    # for ts in ts_list:
    #     ts_files.append(download_ts(ts))

    ts_name_lists = [os.path.join(single_file_path, ts_file) for ts_file in ts_files]

    print('m3u8视频下载完成')
    return ts_name_lists


def convert_ts_to_mp4(ts_file_path):
    def convert(ts_file):
        mp4_file = Path(single_file_path, Path(ts_file).stem + ".mp4")
        os.system(f'ffmpeg -i {ts_file} -c:v libx264 -r 25  {mp4_file}')

    pool = Pool(processes=num_workers)
    pool.map(convert, ts_file_path)
    pool.close()
    pool.join()
    print('转成MP4，fps=25')


def remove_ts_files(dirname):
    for filename in os.listdir(dirname):
        if filename.endswith('.ts'):
            file_path = os.path.join(dirname, filename)
            os.remove(file_path)


def merge_videos(directory_path, output_file_name='result.mp4'):
    """
    合并指定目录下所有后缀为MP4的视频文件。

    Args:
        directory_path (str): 指定的目录路径。
        output_file_name (str): 要输出的合并后视频文件名。默认为'result.mp4'。
    """
    # 获取目录下的所有符合条件的文件
    file_list = os.listdir(directory_path)
    mp4_files = [file for file in file_list if file.endswith('.mp4')]
    mp4_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))  # 按照文件编号排序

    # 生成FFmpeg命令行并执行
    # cmd = 'ffmpeg -i concat:'
    # for mp4_file in mp4_files:
    #     input_file_path = os.path.join(directory_path, mp4_file)
    #     cmd += ' -i {} '.format(input_file_path)
    # cmd += '-filter_complex "concat=n={}:v=1:a=1" -c:v copy -c:a copy {}'.format(len(mp4_files), output_file_name)

    cmd = 'ffmpeg'
    for mp4_file in mp4_files:
        input_file_path = os.path.join(directory_path, mp4_file)
        cmd += ' -i {} '.format(input_file_path)
    cmd += '-filter_complex "concat=n={}:v=1:a=1 [v] [a]" -map "[v]" -map "[a]" {}'.format(len(mp4_files),
                                                                                           output_file_name)
    os.system(cmd)


def remove_mp4_files_except_result(dir_path):
    """
    删除目录下所有后缀为 MP4 的视频文件，但是保留名称为 result.mp4 的文件。
    :param dir_path: 目标目录路径
    """
    for file_name in os.listdir(dir_path):
        if file_name.endswith('.mp4') and file_name != 'result.mp4':
            os.remove(os.path.join(dir_path, file_name))


if __name__ == '__main__':
    url_txt = "./backlist.txt"
    file_path = r'F:\wav2lip_tmp'

    txt = extract_links_from_file(url_txt)
    for single in tqdm(txt[74:]):
        try:
            single_file_path = Path(file_path, Path(single).stem)
            single_file_path.mkdir(parents=True, exist_ok=True)
            ts_name_lists = download_m3u8_video(single, single_file_path)

            if ts_name_lists:
                convert_ts_to_mp4(ts_name_lists)

            # 删除目录所有后缀为ts的文件
            remove_ts_files(single_file_path)

            # 将目录下所有mp4视频拼接成一个片段
            try:
                merge_videos(single_file_path, os.path.join(single_file_path, "result.mp4"))
            except:
                print("merge视频出现问题")

            # 删除目录下除result.mp4结尾的
            # remove_mp4_files_except_result(single_file_path)
        except:
            continue
