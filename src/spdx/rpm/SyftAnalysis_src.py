#调用syft分析路径下的src.rpm包文件
import os
import re
import subprocess
import json
from collections import defaultdict

import numpy as np
import requests
import json

from Utils.convertSbom import convertSpdx
from Utils.extract import decompress
from Utils.java.mavenAnalysis import AnalysisVariabele

# 定义路径
base_path = '/home/jiliqiang/SCA_Code/RPM_package_src'
syft_path = '/home/jiliqiang/SCA_Tools/Syft/./syft'
extract_dir = "/home/jiliqiang/Rpm_Deb/RPM/RPM_exact_src"
def get_file(filepath):
  """
  获取路径中的文件并用 file 类型装载。

  Args:
    filepath: 文件路径。

  Returns:
    file 对象。
  """

  filename = os.path.basename(filepath)
  with open(filepath, 'rb') as f:
    file_obj = f.read()

  return filename, file_obj
def Analysis_RPM_src(filepath):
    filename,file=get_file(filepath)
    if filename.endswith('.rpm'):
        #filepath = /home/jiliqiang/SCA_Code/RPM_package_src/glassfish-jaxb-2.2.11-1.oe2309.src.rpm
        #filename =glassfish-jaxb-2.2.11-1.oe2309.src.rpm
        dpkg_command = f'rpm2archive {filepath}'
        os.system(dpkg_command)

        tgzFilepath=filepath+'.tgz'
        unpack_dir = re.sub(r'\.rpm$', '', filepath)

        mkdir_command=f'mkdir {unpack_dir}'
        os.system(mkdir_command)
        unpack_command = f'tar -zxvf {tgzFilepath} -C {unpack_dir}'
        os.system(unpack_command)

        for root, dirs, files in os.walk(unpack_dir):
            for file in files:
                if file.endswith('.zip') or file.endswith('.rar'):
                    # 执行处理文件夹的命令
                    analysisi_path = os.path.join(root,file)
                    command = f"{syft_path} scan  {analysisi_path} -o json"
                    output = subprocess.check_output(command, shell=True)
                    print(output.decode())
                    # 生成json
                    output_json = json.loads(output.decode())
                    for art in output_json['artifacts']:
                        print(art['version'])
                        # purl_spec = generate_purl_spec(art)
                        # request_OSS(purl_spec)
                        if art['version'] == "":
                            # 进行其他分析
                            print("版本号为空")
                        else:
                            # 生成purl-spec组件坐标
                            purl_spec = generate_purl_spec(art)
                            request_data = request_OSS(purl_spec)


def Analysis_RPM_src_json(filepath):
    filename,file=get_file(filepath)
    if filename.endswith('.rpm'):
        #filepath = /home/jiliqiang/SCA_Code/RPM_package_src/glassfish-jaxb-2.2.11-1.oe2309.src.rpm
        #filename =glassfish-jaxb-2.2.11-1.oe2309.src.rpm
        dpkg_command = f'rpm2archive {filepath}'
        os.system(dpkg_command)

        tgzFilepath=filepath+'.tgz'
        unpack_dir = re.sub(r'\.rpm$', '', filepath)

        mkdir_command=f'mkdir {unpack_dir}'
        os.system(mkdir_command)
        unpack_command = f'tar -zxvf {tgzFilepath} -C {unpack_dir}'
        os.system(unpack_command)

        analysisi_path = unpack_dir
        command = f"{syft_path} scan  {analysisi_path} -o json"
        output = subprocess.check_output(command, shell=True)
        print(output.decode())
        #生成json
        output_json = json.loads(output.decode())
        for art in output_json['artifacts']:
            print(art['version'])
            # purl_spec = generate_purl_spec(art)
            # request_OSS(purl_spec)
            if art['version']=="":
                #进行其他分析
                print("版本号为空")
            else:
            #生成purl-spec组件坐标
                purl_spec=generate_purl_spec(art)
                request_data=request_OSS(purl_spec)


        # for root, dirs, files in os.walk(unpack_dir):
        #     for file in files:
        #         if file.endswith('.zip') or file.endswith('.rar'):
        #             # 执行处理文件夹的命令
        #             analysisi_path = os.path.join(root,file)
        #             command = f"{syft_path} {analysisi_path}"
        #             output = subprocess.check_output(command, shell=True)
        #             print(output.decode())
def generate_purl_spec(art):
    scheme = 'pkg'
    #
    type_temp = art['type']
    if "java" in type_temp:
        type='maven'
    namespace =art['id']
    name = art['name']
    version= art['version']
    str = type+':'+namespace+':'+name+'@'+version
    return  str

#请求OSS Index的API
def request_OSS(str):
    # 构建 API 请求 URL
    url = f"https://ossindex.sonatype.org/api/v3/component-report"
    # 设置请求头
    headers = {
        "accept": "application/vnd.ossindex.component-report.v1+json",
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": [str]
    }
    # 发送 GET 请求并获取响应
    response = requests.post(url, headers=headers, data=json.dumps(body))
    # 检查响应状态码
    if response.status_code == 200:
        # 解析 JSON 响应
        data = response.json()

        # 打印包信息
        print(data)
        return  data
    else:
        # 处理错误
        print(f"请求失败，状态码: {response.status_code}")
# Analysis_RPM_src("/home/jiliqiang/SCA_Code/RPM_package_src/glassfish-jaxb-2.2.11-1.oe2309.src.rpm")
##syft分析RPM包，分析出来一个文件或者组件，如果一个确定的组件，含有版本等，就不需要继续了
# 针对没有确定来源的源代码文件，和OSSIndex里面的做对比，。如果用一些方法推断出，这个文件可能来自某个包，就可以缩小对比范围。

def remove_file_extension(file_name):
    base = os.path.basename(file_name)
    file_name_without_extension = os.path.splitext(base)[0]
    return file_name_without_extension
#针对一个压缩包路径进行解压
def extract_archive(zip_path,dir_Path):
    target_dir = dir_Path+'/'+remove_file_extension(zip_path)
    decompress(zip_path,target_dir)
    return target_dir
#对deb的源码包进行预处理,将src.rpm文件解压，得到相关的路径
def preProcess(src_rpm_path):
    #将src.rpm转换成tz压缩包
    dpkg_command = f'rpm2archive {src_rpm_path}'
    os.system(dpkg_command)
    #创建一个文件夹放置解压后的文件
    tgzFilepath = src_rpm_path+'.tgz'
    dir_Path = re.sub(r'\.rpm$','',src_rpm_path)
    mkdir_command = f'mkdir {dir_Path}'
    os.system(mkdir_command)
    #解压tgz文件
    unpack_command = f'tar -zxvf {tgzFilepath} -C {dir_Path}'
    os.system(unpack_command)


    #找到关键压缩包，解压后，得到解压后的文件夹
    key_dir_path=''
    for root,dirs,files in os.walk(dir_Path):
        for file in files:
            if file.endswith('.zip') or file.endswith('.rar') or file.endswith('.tar') or file.endswith(
                    '.gz') or file.endswith('.bz2'):
                #获取压缩包完整路径
                zip_path = os.path.join(root,file)
                print("处理压缩包",zip_path)
                #解压压缩包
                key_dir_path = extract_archive(zip_path,dir_Path)
    return dir_Path,key_dir_path
    #返回dir_Path是解压后外部的路径
    #返回key_dir_path是解压后文件夹中关键压缩包的解压路径

def scan_rpm_src(src_rpm_path,output_file):
    dir_Path, key_dir_path = preProcess(src_rpm_path)

    scan_rpm_src_path(key_dir_path,output_file,dir_Path)

def parse_spec_file(file_path):
    """
    解析 "control" 文件,并返回一个包含文件信息的字典。

    参数:
    file_path (str): "control" 文件的路径。

    返回:
    dict: 包含文件信息的字典,键为字段名,值为字段值。
    """
    control_info = defaultdict(list)

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                if ':' in line:
                    field, value = line.split(':', 1)
                    control_info[field.strip()].append(value.strip())
                else:
                    control_info[field.strip()].append(line)

    return dict(control_info)
class ExternalDependency:
    name:str
    version:str
    def __init__(self,name,version):
        self.name = name
        self.version = version

def parse_spec_file(file_path):
    """
    解析 "spec" 文件,并返回一个包含文件信息的字典。

    参数:
    file_path (str): "control" 文件的路径。

    返回:
    dict: 包含文件信息的字典,键为字段名,值为字段值。
    """
    control_info = defaultdict(list)

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                if '#' in line:
                    continue
                if ':' in line:
                    field, value = line.split(':', 1)
                    control_info[field.strip()].append(value.strip())
                else:
                    control_info[field.strip()].append(line)

    return dict(control_info)
class ExternalDependency:
    name:str
    version:str
    def __init__(self,name,version):
        self.name = name
        self.version = version
#通过spec文件获取外部依赖信息
def findExterDependency(dir_Path):
    ExterDependencies = []
    for root,dirs,files in os.walk(dir_Path):
        for file in files:
            if file.endswith("spec"):
                file_path = os.path.join(root,file)
                with open(file_path,'r') as  f:
                    spec_data=parse_spec_file(file_path)
                    name = str(spec_data['Name']).strip("[]").strip("'")
                    version = str(spec_data['Version']).strip("[]").strip("'")
                    release = str(spec_data['Release']).strip("[]").strip("'")
                    for str_data in spec_data['Requires']:
                        if str_data:
                            dependStr_name = str_data.replace("%{name}",name)
                            dependStr_version = dependStr_name.replace("%{version}",version)
                            dependStr = dependStr_version.replace("%{release}",release)
                            if "=" in dependStr:
                                print(dependStr)
                                parts=dependStr.split("=")
                                part1=parts[0].strip()
                                part2 = parts[1].strip()
                                externalDependency = ExternalDependency(
                                    name = part1,
                                    version=part2
                                )
                                ExterDependencies.append(externalDependency)

                break;

    return ExterDependencies
#scan_path 是扫描项目的路径,输入的是rpm的src目录的文件夹,也就是key_dir_path
#output_file 指定要保存的文件路径
#这里输入的是deb源码包解压后的文件夹，输出的是sbom
def scan_rpm_src_path(scan_path,output_file,dir_Path):



    #处理内部依赖
    # project_name= remove_file_extension(scan_path)
    project_name = scan_path
    # 键是变量${xx},值是解析出来的具体数字
    dict_variable = {}
    accPathSum = []

    variableList = []
    matrix = np.zeros((1024, 1024))
    # 生成syft普通json
    command_syft = f"{syft_path} scan  {scan_path} -o json"
    syft_output = subprocess.check_output(command_syft, shell=True)
    syft_json = json.loads(syft_output.decode())

    artifacts = syft_json['artifacts']
    for artifact in artifacts:
        foundBy = artifact['foundBy']
        # 获取workdir
        workdir = ''
        locations = artifact['locations']
        accPathList = []
        for location in locations:
            accessPath = location['accessPath']
            base_path = accessPath.rsplit('/', 1)[0] + '/'
            workdir = scan_path + base_path
            accPathList.append(accessPath)
        accPathSum.append(accPathList)
        name = artifact['name']
        version = artifact['version']
        if foundBy == 'java-pom-cataloger':
            if name.startswith('$'):
                variableList.append(name)
                value_name = AnalysisVariabele(workdir, name)
                result = value_name.decode('utf-8').replace('b', '')
                artifact['name'] = result.replace("'", '')
                print(artifact['name'])
                dict_variable[name] = value_name
                for index_list, value_variableList in enumerate(variableList):
                    if value_variableList == name:
                        for index_path, path_list in enumerate(accPathSum):
                            if path_list == accPathList:
                                matrix[index_list, index_path] = 1
            if version.startswith('$'):
                variableList.append(version)
                value_version = AnalysisVariabele(workdir, version)
                result = value_version.decode('utf-8').replace('b', '')
                artifact['version'] = result.replace("'", '')
                print(artifact['version'])
                dict_variable[version] = value_version
                for index_variable, value_variable in enumerate(variableList):
                    if value_variable == version:
                        for index_path, path_acc in enumerate(accPathSum):
                            if path_acc == accPathList:
                                matrix[index_variable, index_path] = 1
    # 处理外部依赖
    # ExterDependencies = findExterDependency(scan_path)
    ExterDependencies = findExterDependency(dir_Path)
    convertSpdx(syft_json, project_name, output_file, ExterDependencies)
    # 生成cyclonedx的json
    # command_sbom = f"{syft_path} scan  {scan_path} -o cyclonedx-json"
    # cyclonedx_output = subprocess.check_output(command_sbom, shell=True)
    # cyclonedx_json= json.loads(cyclonedx_output.decode())
    # sbom_cyclonedx_json=cyclonedx_json
    # print(sbom_cyclonedx_json)
    # # 创建输出文件
    # open(output_file,"w").close()
    # #写入json文件
    # with open(output_file,"w") as file:
    #     json.dump(sbom_cyclonedx_json,file)
    # scan_path = '/home/jiliqiang/SCA_Evalutation/efda/java/maven/interpolated-variables'
    # output_file='/home/jiliqiang/SCA_Evalutation/efda/java/maven/sbom_cyclonedx/interpolated-variables.json'




src_rpm_path = '/home/jiliqiang/RPM/src/glassfish-jaxb-2.3.1-150200.5.5.9.src.rpm'
output_file = '/home/jiliqiang/RPM/src/glassfish_syft.spdx.json'
scan_rpm_src(src_rpm_path,output_file)

# dir_Path='/home/jiliqiang/RPM/src/glassfish-jaxb-2.3.1-150200.5.5.9.src'
# findExterDependency(dir_Path)