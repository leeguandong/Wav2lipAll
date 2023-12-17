import re


def extract_m3u8_links(original_file, output_file):
    # 读取原文本文件
    with open(original_file, 'r', encoding="utf-8") as f:
        text = f.read()

    # 提取第三列和所有的.m3u8链接
    lines = []
    columns = text.split('\n')
    for column in columns:
        fields = column.split()
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', column)
        m3u8_urls = [url for url in urls if url.endswith('.m3u8')]

        if len(fields) >= 3 and m3u8_urls:
            line = fields[2] + ' ' + ' '.join(m3u8_urls)
            lines.append(line)

    # 将链接写入新文件
    with open(output_file, 'w',encoding="utf-8") as f:
        for url in lines:
            f.write(url + '\n')


if __name__ == "__main__":
    extract_m3u8_links("./data/b.txt", './data/b_new_backlist.txt')
