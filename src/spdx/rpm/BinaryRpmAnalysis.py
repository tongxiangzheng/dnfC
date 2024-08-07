import os
import re
import subprocess
import json
import pyrpm

from Utils.convertSbom import convertSpdx, convertSpdx_binaryRPM

syft_path = '/home/jiliqiang/SCA_Tools/Syft/./syft'
#对rpm的二进制包进行预处理，得到相关路径
def preProcess(rpm_path):
    #将rpm包转换成tgz压缩包
    rpm_command = f'rpm2archive {rpm_path}'
    os.system(rpm_command)
    # 创建一个文件夹放置解压后的文件
    tgzFilepath = rpm_path + '.tgz'
    dir_Path = re.sub(r'\.rpm$', '', rpm_path)
    mkdir_command = f'mkdir {dir_Path}'
    os.system(mkdir_command)
    # 解压tgz文件
    unpack_command = f'tar -zxvf {tgzFilepath} -C {dir_Path}'
    os.system(unpack_command)
    return  dir_Path
# class ExternalDependency:
#     name:str
#     version:str

#     def __init__(self,name,version):
#         self.name = name
#         self.version = version
def getRpmName(scan_path):
    rpmName = os.path.basename(scan_path)
    return rpmName


def parse_purl(purl):
    """
    解析一个 purl 链接,返回各个组件。
    """
    # 匹配 purl 的正则表达式
    purl_pattern = r"^pkg:(?P<type>\w+)\/(?P<namespace>[^@]+)\/(?P<name>[^@]+)(?:@(?P<version>.+))?(?:\?(?P<qualifiers>.+))?(?:#(?P<subpath>.+))?"

    match = re.match(purl_pattern, purl)
    if not match:
        raise ValueError("Invalid purl format: {}".format(purl))

    # 提取各个组件
    components = match.groupdict()

    return components
#获取外部依赖
def getExternalDependencies(scan_path,resultJsonPath):
    rpmName=getRpmName(scan_path)
    command_docker = f"docker run --name parsePackageC -v {scan_path}:/mnt/analyze-package/{rpmName} -v {resultJsonPath}:/mnt/analyze-package/result.json -v parse_package-repoMetadata:/app/repoMetadata --rm parse_package"
    print(command_docker)
    result = subprocess.check_output(command_docker, shell=True)
    print("完成")
    Required=[]
    ExternalDependencies = []
    with open(resultJsonPath,"r") as json_file:
        json_data = json.load(json_file)
    if json_data[str(rpmName)]:
        print("解析")
        #都是purl链接
        Required = json_data[str(rpmName)]
        #获取dependency实例数组
        for require in Required:
            purlComponent =  parse_purl(str(require))
            name =purlComponent['name']
            version =  purlComponent['version']
            Dependency = ExternalDependency(
                name = name,
                version= version
            )
            ExternalDependencies.append(Dependency)
            print("require:",require)
            print("name:",name)
            print("version",version)
    else:
        print("无外部依赖")
    return Required
#针对二进制的rpm包做分析
def binaryRpmScan(scan_path,output_file,PurlList):
    # resultJsonPath = "/home/jiliqiang/RPM/rpm/result.json"
    #处理外部依赖
    # PurlList = getExternalDependencies(scan_path,resultJsonPath)
    
    #解压rpm二进制包
    dir_Path = preProcess(scan_path)

    #处理内部依赖
    project_name = dir_Path
    # 生成syft普通json
    command_syft = f"{syft_path} scan  {dir_Path} -o json"
    syft_output = subprocess.check_output(command_syft, shell=True)
    syft_json = json.loads(syft_output.decode())
    tempath = scan_path + '-syft.json'
    with open(tempath, "w") as f:
        json_string =json.dumps(syft_json,indent=4, separators=(',', ': '))
        f.write(json_string)

    convertSpdx_binaryRPM(syft_json, project_name, output_file,PurlList)

#scan_path = "/home/jiliqiang/RPM/rpm/glassfish-jaxb-2.3.1-150200.5.5.9.noarch.rpm"
# scan_path = "/home/jiliqiang/RPM/rpm/keepass-2.54-2.mga9.noarch.rpm"
# output_file = "/home/jiliqiang/RPM/rpm/SBOM/keepass-2.54-2.mga9.noarch.rpm.spdx.json"
# resultJsonPath = "/home/jiliqiang/RPM/rpm/result.json"
# binaryRpmScan(scan_path,output_file)
# getExternalDependencies(scan_path)
#getExternalDependencies(scan_path,resultJsonPath)