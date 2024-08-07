import os.path
import xml.etree.ElementTree as ET
#提取一个项目里面所有的pom文件
#输入是项目文件夹的路径
dict_pomObject = {}
dict_pomPath = {}
dict_artifactName = {}
class Artifact:
    group_id = '1.0'
    artifact_id = 'abs'
    version = "unknow"
    def __int__(self,group_id,artifact_id,version):
        self.artifact_id=artifact_id
        self.group_id=group_id
        self.version=version
def extract_pom_files(project_dir):
    pom_files = []
    for root,dirs,files in os.walk(project_dir):
        for file in files:
            if file.lower() == 'pom.xml':
                pom_file_path = os.path.join(root,file)
                pom_files.append(pom_file_path)
                file_name = file
                #解析一个pom文件，得到artifact对象
                pom_object = ET.parse(pom_file_path)
                root = pom_object.getroot()
                # 获取artifact信息
                group_id = root.find('groupId').text
                artifact_id = root.find('artifactId').text
                version = root.find('version').text
                artifact =Artifact(group_id,artifact_id,version)
                dict_artifactName[artifact]=pom_file_path

                dict_pomObject[pom_object] = pom_file_path
                dict_pomPath[pom_file_path] =pom_object

    return  pom_files
#输入一个pom文件和组件名称,还有无法显示版本号类型，找到这个组件的版本
#unknowVersion_type:   1  代表${}   2代表 ${project.version}  3代表''
#根据规则找到每个组件的版本
def getDetail(pom_path,artifact,unknowVersion_type):
    pom_object = ET.parse(pom_path)
    root = pom_object.getroot()
    #获取项目信息
    model_version = root.find('modelVersion').text
    group_id = root.find('groupId').text
    artifact_id = root.find('artifactId').text
    version = root.find('version').text
    dependencies = root.find('dependencies')


    # for dependency in dependencies.findall('dependency'):
    #     dependency_artifact_id =dependency.find('artifactId').text
    #     if dependency_artifact_id == artifact.artifact_id:
    #         a=1
    if unknowVersion_type == 1:
        properties = root.find('jaxb-api.version')
        print(properties)
        for property in properties:
            dependency_version = property.find(artifact.version)
            if dependency_version:
                artifact.version= dependency_version
            else:
                print("版本号错误")
    if unknowVersion_type == 3 or unknowVersion_type==2:
        flag=0

        while flag == 0:
            parent_artifact = findParentArtifact(pom_path)
            parent_pom_file_path = dict_artifactName[parent_artifact]
            if parent_pom_file_path:
                pom_path = parent_pom_file_path
                parent_pom_object = ET.parse(parent_pom_file_path)
                parent_root = parent_pom_object.getroot()
                if unknowVersion_type==2:
                    # 解决${project.version}
                    parent_version= parent_root.find('version').text
                    if parent_version:
                        artifact.version=parent_version
                        flag=1
                    else:
                        continue
                if  unknowVersion_type==3:
                    #dependencyManagement
                    parent_dependency_manage= parent_root.find('dependencyManagement')
                    if parent_dependency_manage:
                        manage_dependencies = parent_dependency_manage.find(dependencies)
                        isMatch=0
                        for manage_dependency in manage_dependencies:
                            if manage_dependency.find('artifactId').text==artifact.artifact_id:
                                isMatch =1
                                manage_dependency_version =manage_dependency.find('version').text
                                #if manage_dependency_version
                                    #如果manage_dependency_version是纯数字，那么直接填充
                                    #如果还是$配置，那么调用自己函数，找到这个版本号
                                #else
                        #如果都没有匹配上
                        if isMatch==0:
                            print("pom文件错误，无法解析版本")
                    else:
                        print("pom文件错误，无法解析版本")


            else:
                #如果整个项目找不到这样的pom文件，说明在maven仓库，这里待完善
                break


#输入一个pom文件路径，返回一个artifact类型
def findParentArtifact(pom_path):
    pom_object = ET.parse(pom_path)
    root = pom_object.getroot()
    parent = root.find('parent')
    group_id = parent.find('groupId').text
    artifact_id = parent.find('artifactId').text
    version = parent.find('version').text
    parent_artifact = Artifact(group_id, artifact_id, version)
    return  parent_artifact
#extract_pom_files('/home/jiliqiang/Rpm_Deb/Rpm/glassfish-jaxb/jaxb-v2-jaxb-2_2_11-branch')
def analysispom(pom_path):
    pom_object = ET.parse(pom_path)
    root = pom_object.getroot()
    namespace = {
        "p":"http://maven.apache.org/POM/4.0.0"
    }
    # for child in root:
    #     print(child.tag)

    # 获取 Pom 文件中的元素
    group_id = root.find("p:groupId",namespace).text
    artifact_id = root.find("p:artifactId",namespace).text
    version = root.find("p:version",namespace).text
    #
    # # 打印元素的值
    # print("Group ID:", group_id)
    # print("Artifact ID:", artifact_id)
    # print("Version:", version)
    parent = root.find("p:parent",namespace)
    parent_artifactId= parent.find("p:artifactId",namespace).text
    print(parent_artifactId)

analysispom('/home/jiliqiang/Rpm_Deb/Rpm/glassfish-jaxb/jaxb-v2-jaxb-2_2_11-branch/jaxb-ri/boms/bom/pom.xml')