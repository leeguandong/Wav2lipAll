import subprocess


# 读取txt文件
def read_requirements(file_path):
    with open(file_path, 'r') as file:
        # 读取非空行并去除首尾空格
        requirements = [line.strip() for line in file if line.strip()]
    return requirements


# 解析包名和版本号
def parse_package_info(line):
    package, version = line.split()
    return package, version


# 使用pip安装依赖库
def install_libraries(packages, index_url=None):
    # 构造pip命令
    pip_command = ['pip', 'install']

    # 添加源命令
    if index_url:
        pip_command.extend(['-i', index_url])

    # 添加要安装的包名和版本号
    pip_command.extend(packages)

    # 执行pip命令
    subprocess.check_call(pip_command)


def main():
    # txt文件路径
    requirements_file = 'requirements.txt'

    # 读取txt文件
    lines = read_requirements(requirements_file)

    # pip源可选，如清华源、阿里源等
    pip_source = 'https://pypi.tuna.tsinghua.edu.cn/simple'

    # 解析包名和版本号
    packages = [parse_package_info(line)[0] for line in lines]

    # 安装依赖库
    install_libraries(packages, index_url=pip_source)


if __name__ == "__main__":
    main()
