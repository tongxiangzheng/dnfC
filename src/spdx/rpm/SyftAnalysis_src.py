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
syft_path11 = '/usr/share/dnfC/spdx/syft11/syft'
extract_dir = "/home/jiliqiang/Rpm_Deb/RPM/RPM_exact_src"



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

def scan_rpm_src(src_rpm_path,output_file,ExternalDependencies,sbomType):
    dir_Path, key_dir_path = preProcess(src_rpm_path)

    scan_rpm_src_path(key_dir_path,output_file,dir_Path)


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
    command_syft = f"{syft_path11} scan  {scan_path} -o json"
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