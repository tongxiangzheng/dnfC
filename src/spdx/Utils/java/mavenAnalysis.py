import os
#通过命令help:valuate 来解析变量
#workdir  pom文件所在的目录
#variable 变量${}
#mvn help:evaluate -Dexpression=project.version -q -DforceStdout
import subprocess
import  json
import  re
def AnalysisVariabele(workdir,variable):
    #进入工作目录
    os.chdir(workdir)
    #去除$
    value = removeDollar(variable)
    output =-1
    if value !='':
        command = f"mvn help:evaluate -Dexpression={value} -q -DforceStdout"
        output= subprocess.check_output(command,shell=True)
    return  output
def removeDollar(variable):
    pattern = r'\$\{(.+?)\}'
    value = ''
    match = re.match(pattern,variable)
    if match:
        value = match.group(1)
        return value
    return value
# workdir ='/home/jiliqiang/SCA_Evalutation/efda/java/maven/interpolated-variables/child-module'
# variable='${sling.engine.version}'
# print(AnalysisVariabele(workdir,variable))


import zipfile

def read_jar_metadata(jar_file_path):
    try:
        with zipfile.ZipFile(jar_file_path, 'r') as jar_file:
            print("Manifest information:")
            manifest = jar_file.read('META-INF/MANIFEST.MF')
            for line in manifest.decode().split('\n'):
                if line.strip():
                    print(f"  {line}")

            print("\nEntries:")
            for entry in jar_file.namelist():
                print(f"  {entry}")
    except (FileNotFoundError, zipfile.BadZipFile) as e:
        print(f"Error reading JAR file: {e}")

# 使用示例
# read_jar_metadata('/home/jiliqiang/SCA_Evalutation/efda/java/jars/original-jars/lib/org/spamframework/spam-web/version.RELEASE/spam-web-version.RELEASE.jar')
read_jar_metadata('/home/jiliqiang/Deb/src/rstudio/src/gwt/lib/gwt/gwt-rstudio/requestfactory-client+src.jar')