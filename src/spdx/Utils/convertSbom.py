#spdx2.3
import hashlib
import logging
import sys
from datetime import datetime
from typing import List
import cyclonedx
from spdx_tools.common.spdx_licensing import spdx_licensing
from spdx_tools.spdx.model import (
    Actor,
    ActorType,
    Checksum,
    ChecksumAlgorithm,
    CreationInfo,
    Document,
    ExternalPackageRef,
    ExternalPackageRefCategory,
    File,
    FileType,
    Package,
    PackagePurpose,
    PackageVerificationCode,
    Relationship,
    RelationshipType, SpdxNoAssertion,
)
from spdx_tools.spdx.validation.document_validator import validate_full_spdx_document
from spdx_tools.spdx.validation.validation_message import ValidationMessage
from spdx_tools.spdx.writer.write_anything import write_file
import uuid
import  re

#cyclonedx格式
from typing import TYPE_CHECKING

from packageurl import PackageURL

from cyclonedx.exception import MissingOptionalDependencyException
from cyclonedx.factory.license import LicenseFactory
from cyclonedx.model import XsUri
from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.model.contact import OrganizationalEntity
from cyclonedx.output import make_outputter
from cyclonedx.output.json import JsonV1Dot5
from cyclonedx.schema import OutputFormat, SchemaVersion
from cyclonedx.validation import make_schemabased_validator
from cyclonedx.validation.json import JsonStrictValidator
from cyclonedx.model import Tool,Property
if TYPE_CHECKING:
    from cyclonedx.output.json import Json as JsonOutputter
    from cyclonedx.output.xml import Xml as XmlOutputter
    from cyclonedx.validation.xml import XmlValidator

def convertSpdx(syft_json,project_name,output_file,ExterDependencies):
    current_date = datetime.today().date()
    #当前的时间
    current_time = datetime.now()
    #project就是scan_path，这里生成哈希码
    PathHash= hashlib.sha256(project_name.encode()).hexdigest()
    creation_info = CreationInfo(
        spdx_version="SPDX-2.3",
        spdx_id="SPDXRef-DOCUMENT",
        name=project_name,
        data_license="CC0-1.0",
        document_namespace="https://anchore.com/syft/dir"+project_name+"-"+PathHash,
        creators=[Actor(ActorType.ORGANIZATION, "Rest", "jiliqiang.iscas@ac.com"),Actor(ActorType.TOOL,"Syft-Plus")],
        #created= datetime(current_date.year, current_date.month, current_date.day),
        created=current_time,
    )
    document = Document(creation_info)
    #键是id,值是spdx_id
    id_spdxId ={}
    #处理外部依赖
    spdx_id_externalDependencies = []
    for exterDependency in ExterDependencies:
        spdx_id_externalDependency = f"SPDXRef-Package-Deb---{exterDependency.name}--{uuid.uuid4()}"
        #存储所有外部依赖的spdxid
        spdx_id_externalDependencies.append(spdx_id_externalDependency)
        package_exterDependency =  Package(
            name=exterDependency.name,
            spdx_id=spdx_id_externalDependency,
            download_location="https://download.com",
            version=exterDependency.version,
            source_info="External Dependency",
            files_analyzed= False,
            description=f"Deb",
            copyright_text="Copyright 2024 Jane Doe",
        )
        package_exterDependency.license_concluded = SpdxNoAssertion()
        package_exterDependency.license_declared = SpdxNoAssertion()
        package_exterDependency.external_references.append(ExternalPackageRef(
            category=ExternalPackageRefCategory.PACKAGE_MANAGER,
            reference_type="purl",
            locator=f"pkg:deb/debian/{exterDependency.name}@{exterDependency.version}"
        ))
        document.packages.append(package_exterDependency)
    # 获取source信息
    source = syft_json['source']
    id = source['id']
    type = source['type']
    name = source['name'].replace("/", "-")
    spdx = ''
    if type == 'directory':
        projectStr = project_name.replace("/", "-").replace("_", "-").replace("@", "")
        spdx = f"SPDXRef-DocumentRoot-Directory-{projectStr}"
    elif type == 'file':
        spdx = f"SPDXRef-DocumentRoot-File-{name}"
    id_spdxId[id] = spdx
    package_source = Package(
        name=project_name,
        spdx_id=spdx,
        download_location="https://download.com",
        version=source['version'],
        description=type,
    )
    document.packages.append(package_source)
    sourceRealationShip = Relationship("SPDXRef-DOCUMENT",RelationshipType.DESCRIBES,spdx)
    document.relationships.append(sourceRealationShip)
    #默认source和外部依赖的关系是BUILD_DEPENDENCY_OF
    for spdx_id_externalDependency in spdx_id_externalDependencies:
        document.relationships.append(Relationship(spdx,RelationshipType.BUILD_DEPENDENCY_OF,spdx_id_externalDependency))
    #处理artifact
    artifacts = syft_json['artifacts']
    #保存package里面的spdx_id
    package_spdx_id = []
    for artifact in artifacts:
        Locations=artifact['locations']
        path=''
        accessPath=''
        annotations=''
        for location in Locations:
            path=location['path']
            accessPath=location['accessPath']
            annotations=location['annotations']
        licenses = artifact['licenses']
        tempName = artifact['name'].replace("_","-").replace("@","").replace("/","-")
        spdx_id_result=f"SPDXRef-Package-{artifact['type']}---{tempName}-{uuid.uuid4()}"
        id = artifact['id']
        id_spdxId[id]=spdx_id_result
        package = Package(
            name=artifact['name'],
            spdx_id=spdx_id_result,
            download_location="https://download.com",
            version=artifact['version'],

            #file_name="./foo.bar",
            #supplier=Actor(ActorType.ORGANIZATION,f""),
            #originator=Actor(ActorType.ORGANIZATION, "some organization", "contact@example.com"),
            source_info="Inner Dependency",
            files_analyzed=True,
            # verification_code=PackageVerificationCode(
            #     value="d6a770ba38583ed4bb4525bd96e50461655d2758", excluded_files=["./some.file"]
            # ),
            # checksums=[
            #     Checksum(ChecksumAlgorithm.SHA1, "d6a770ba38583ed4bb4525bd96e50461655d2758"),
            #     Checksum(ChecksumAlgorithm.MD5, "624c1abb3664f4b35547e7c73864ad24"),
            # ],
            # license_concluded=spdx_licensing.parse("GPL-2.0-only OR MIT"),
            #license_info_from_files=[spdx_licensing.parse("GPL-2.0-only"), spdx_licensing.parse("MIT")],
            # license_declared=spdx_licensing.parse("GPL-2.0-only AND MIT"),
            # license_comment="license comment",
            copyright_text="Copyright 2022 Jane Doe",
            description=f"{artifact['type']}",
            # attribution_texts=["package attribution"],
            # primary_package_purpose=PackagePurpose.LIBRARY,
            # release_date=datetime(2015, 1, 1),
            # external_references=[
            #     ExternalPackageRef(
            #         category=ExternalPackageRefCategory.OTHER,
            #         reference_type="http://reference.type",
            #         locator="reference/locator",
            #         comment="external reference comment",
            #     )
            # ],
            #external_references= ExternalPackageRefList,
        )
        package.license_concluded = SpdxNoAssertion()
        package.license_declared = SpdxNoAssertion()
        # if len(licenses) == 0:
        #     package.license_concluded=SpdxNoAssertion()
        #     package.license_declared=SpdxNoAssertion()
        # else:
        #     for license in licenses:
        #         package.license_concluded+=spdx_licensing.parse(license)
        #         package.license_declared += spdx_licensing.parse(license)

        #ExternalPackageRefList = []
        cpes = artifact['cpes']
        for cpe in cpes:
            externPackageRef=ExternalPackageRef(
                category=ExternalPackageRefCategory.SECURITY,
                reference_type="cpe23Type",
                locator=cpe
            )
            package.external_references.append(externPackageRef)
        purl = artifact['purl']
        externPackageRef=ExternalPackageRef(
            category=ExternalPackageRefCategory.PACKAGE_MANAGER,
            reference_type="purl",
            locator=purl
        )
        package.external_references.append(externPackageRef)
        #document.packages.append([package])
        document.packages.append(package)
        #document.packages = [package]
        package_spdx_id.append(package.spdx_id)
    
    
    #创建文件关系
    fileSpdxIdList = []
    try:
        files = syft_json['files']
        for file in files:
            location = file['location']
            fileName = location['path']
            if fileName[0] == "/":
                fileNameResult = '.' + fileName
            spdxId = fileName.replace("/", "-").replace("_", "-").replace("@", "").replace("+", "-")
            spdxId_result = f"SPDXRef-File--{spdxId}-{uuid.uuid4()}"
            id = file['id']
            id_spdxId[id] = spdxId_result
            # 创建文件字段
            file1 = File(
                name=fileNameResult,
                spdx_id=spdxId_result,
                # file_types=[FileType.SOURCE],
                checksums=[
                    Checksum(ChecksumAlgorithm.SHA1, "d6a770ba38583ed4bb4525bd96e50461655d2758"),
                    Checksum(ChecksumAlgorithm.MD5, "624c1abb3664f4b35547e7c73864ad24"),
                ],
                # license_concluded=spdx_licensing.parse("MIT"),
                # license_info_in_file=[spdx_licensing.parse("MIT")],
                copyright_text="Copyright 2022 Jane Doe",
            )
            fileSpdxIdList.append(spdxId_result)
            document.files.append(file1)
    except KeyError:
        print("'files' field not found in the JSON data.")



    # for spdxIdLi in fileSpdxIdList:
    #     contains_relationship1 = Relationship("SPDXRef-Package", RelationshipType.CONTAINS, "SPDXRef-File1")
    #处理关系
    artifactRelationships = syft_json['artifactRelationships']
    for artifactRelationship in artifactRelationships:
        parent = id_spdxId[artifactRelationship['parent']]
        child = id_spdxId[artifactRelationship['child']]
        relationshipType = artifactRelationship['type']
        if relationshipType=='contains':
            contains_relationship = Relationship(parent,RelationshipType.CONTAINS,child)
            document.relationships.append(contains_relationship)
        else:
            contains_relationship = Relationship(parent, RelationshipType.OTHER, child)
            document.relationships.append(contains_relationship)
    # for package_spdx in package_spdx_id:
    #     describes_relationship = Relationship(spdx, RelationshipType.CONTAINS, package_spdx)
    #     document.relationships.append(describes_relationship)
    # write_file(document, "/home/jiliqiang/SCA_Evalutation/efda/java/maven/sbom_spdx/my_spdx_document.spdx.json")
    write_file(document, output_file)

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
def convertSpdx_binaryRPM(syft_json, project_name, output_file,purlList):
    current_date = datetime.today().date()
    # 当前的时间
    current_time = datetime.now()
    # project就是scan_path，这里生成哈希码
    PathHash = hashlib.sha256(project_name.encode()).hexdigest()
    creation_info = CreationInfo(
        spdx_version="SPDX-2.3",
        spdx_id="SPDXRef-DOCUMENT",
        name=project_name,
        data_license="CC0-1.0",
        document_namespace="https://anchore.com/syft/dir" + project_name + "-" + PathHash,
        creators=[Actor(ActorType.ORGANIZATION, "Rest", "jiliqiang.iscas@ac.com"), Actor(ActorType.TOOL, "Syft-Plus")],
        # created= datetime(current_date.year, current_date.month, current_date.day),
        created=current_time,
    )
    document = Document(creation_info)
    # 键是id,值是spdx_id
    id_spdxId = {}
    # 处理外部依赖
    spdx_id_externalDependencies = []
    for  purl in purlList:
        purlComponent = parse_purl(str(purl))
        name = purlComponent['name']
        version = purlComponent['version']
        spdx_id_externalDependency = f"SPDXRef-Package-RPM---{name}--{uuid.uuid4()}"
        # 存储所有外部依赖的spdxid
        spdx_id_externalDependencies.append(spdx_id_externalDependency)
        package_exterDependency = Package(
            name=name,
            spdx_id=spdx_id_externalDependency,
            download_location="https://download.com",
            version=version,
            source_info="External Dependency",
            files_analyzed=False,
            description=f"RPM",
            copyright_text="Copyright 2024 Jane Doe",
        )
        package_exterDependency.license_concluded = SpdxNoAssertion()
        package_exterDependency.license_declared = SpdxNoAssertion()
        package_exterDependency.external_references.append(ExternalPackageRef(
            category=ExternalPackageRefCategory.PACKAGE_MANAGER,
            reference_type="purl",
            locator=purl
        ))
        document.packages.append(package_exterDependency)
    # 获取source信息
    source = syft_json['source']
    id = source['id']
    type = source['type']
    name = source['name'].replace("/", "-")
    spdx = ''
    if type == 'directory':
        projectStr = project_name.replace("/", "-").replace("_", "-")
        spdx = f"SPDXRef-DocumentRoot-Directory-{projectStr}"
    elif type == 'file':
        spdx = f"SPDXRef-DocumentRoot-File-{name}"
    id_spdxId[id] = spdx
    package_source = Package(
        name=project_name,
        spdx_id=spdx,
        download_location="https://download.com",
        version=source['version'],
        description=type,
    )
    document.packages.append(package_source)
    sourceRealationShip = Relationship("SPDXRef-DOCUMENT", RelationshipType.DESCRIBES, spdx)
    document.relationships.append(sourceRealationShip)
    # 默认source和外部依赖的关系是BUILD_DEPENDENCY_OF
    for spdx_id_externalDependency in spdx_id_externalDependencies:
        document.relationships.append(
            Relationship(spdx, RelationshipType.BUILD_DEPENDENCY_OF, spdx_id_externalDependency))
    # 处理artifact
    artifacts = syft_json['artifacts']
    # 保存package里面的spdx_id
    package_spdx_id = []
    for artifact in artifacts:
        Locations = artifact['locations']
        path = ''
        accessPath = ''
        annotations = ''
        for location in Locations:
            path = location['path']
            accessPath = location['accessPath']
            annotations = location['annotations']
        licenses = artifact['licenses']
        tempName = artifact['name'].replace("_", "-").replace("@", "").replace("/", "-")
        # tempName = artifact['name'].replace("_", "-")
        spdx_id_result = f"SPDXRef-Package-{artifact['type']}---{tempName}-{uuid.uuid4()}"
        id = artifact['id']
        id_spdxId[id] = spdx_id_result
        package = Package(
            name=artifact['name'],
            spdx_id=spdx_id_result,
            download_location="https://download.com",
            version=artifact['version'],

            # file_name="./foo.bar",
            # supplier=Actor(ActorType.ORGANIZATION,f""),
            # originator=Actor(ActorType.ORGANIZATION, "some organization", "contact@example.com"),
            source_info="Inner Dependency",
            files_analyzed=True,
            # verification_code=PackageVerificationCode(
            #     value="d6a770ba38583ed4bb4525bd96e50461655d2758", excluded_files=["./some.file"]
            # ),
            # checksums=[
            #     Checksum(ChecksumAlgorithm.SHA1, "d6a770ba38583ed4bb4525bd96e50461655d2758"),
            #     Checksum(ChecksumAlgorithm.MD5, "624c1abb3664f4b35547e7c73864ad24"),
            # ],
            # license_concluded=spdx_licensing.parse("GPL-2.0-only OR MIT"),
            # license_info_from_files=[spdx_licensing.parse("GPL-2.0-only"), spdx_licensing.parse("MIT")],
            # license_declared=spdx_licensing.parse("GPL-2.0-only AND MIT"),
            # license_comment="license comment",
            copyright_text="Copyright 2022 Jane Doe",
            description=f"{artifact['type']}",
            # attribution_texts=["package attribution"],
            # primary_package_purpose=PackagePurpose.LIBRARY,
            # release_date=datetime(2015, 1, 1),
            # external_references=[
            #     ExternalPackageRef(
            #         category=ExternalPackageRefCategory.OTHER,
            #         reference_type="http://reference.type",
            #         locator="reference/locator",
            #         comment="external reference comment",
            #     )
            # ],
            # external_references= ExternalPackageRefList,
        )
        package.license_concluded = SpdxNoAssertion()
        package.license_declared = SpdxNoAssertion()
        # if len(licenses) == 0:
        #     package.license_concluded = SpdxNoAssertion()
        #     package.license_declared = SpdxNoAssertion()
        # else:
        #     for license in licenses:
        #         package.license_concluded += spdx_licensing.parse(license)
        #         package.license_declared += spdx_licensing.parse(license)

        # ExternalPackageRefList = []
        cpes = artifact['cpes']
        for cpe in cpes:
            externPackageRef = ExternalPackageRef(
                category=ExternalPackageRefCategory.SECURITY,
                reference_type="cpe23Type",
                locator=cpe
            )
            package.external_references.append(externPackageRef)
        purl = artifact['purl']
        externPackageRef = ExternalPackageRef(
            category=ExternalPackageRefCategory.PACKAGE_MANAGER,
            reference_type="purl",
            locator=purl
        )
        package.external_references.append(externPackageRef)
        # document.packages.append([package])
        document.packages.append(package)
        # document.packages = [package]
        package_spdx_id.append(package.spdx_id)

    # 创建文件关系
    fileSpdxIdList = []
    try:
        files = syft_json['files']
        for file in files:
            location = file['location']
            fileName = location['path']
            if fileName[0] == "/":
                fileNameResult = '.' + fileName
            spdxId = fileName.replace("/", "-").replace("_", "-")
            spdxId_result = f"SPDXRef-File--{spdxId}-{uuid.uuid4()}"
            id = file['id']
            id_spdxId[id] = spdxId_result
            # 创建文件字段
            file1 = File(
                name=fileNameResult,
                spdx_id=spdxId_result,
                # file_types=[FileType.SOURCE],
                checksums=[
                    Checksum(ChecksumAlgorithm.SHA1, "d6a770ba38583ed4bb4525bd96e50461655d2758"),
                    Checksum(ChecksumAlgorithm.MD5, "624c1abb3664f4b35547e7c73864ad24"),
                ],
                # license_concluded=spdx_licensing.parse("MIT"),
                # license_info_in_file=[spdx_licensing.parse("MIT")],
                copyright_text="Copyright 2022 Jane Doe",
            )
            fileSpdxIdList.append(spdxId_result)
            document.files.append(file1)
    except KeyError:
        print("'files' field not found in the JSON data.")

    # for spdxIdLi in fileSpdxIdList:
    #     contains_relationship1 = Relationship("SPDXRef-Package", RelationshipType.CONTAINS, "SPDXRef-File1")
    # 处理关系
    artifactRelationships = syft_json['artifactRelationships']
    for artifactRelationship in artifactRelationships:
        parent = id_spdxId[artifactRelationship['parent']]
        child = id_spdxId[artifactRelationship['child']]
        relationshipType = artifactRelationship['type']
        if relationshipType == 'contains':
            contains_relationship = Relationship(parent, RelationshipType.CONTAINS, child)
            document.relationships.append(contains_relationship)
        else:
            contains_relationship = Relationship(parent, RelationshipType.OTHER, child)
            document.relationships.append(contains_relationship)
    # for package_spdx in package_spdx_id:
    #     describes_relationship = Relationship(spdx, RelationshipType.CONTAINS, package_spdx)
    #     document.relationships.append(describes_relationship)
    # write_file(document, "/home/jiliqiang/SCA_Evalutation/efda/java/maven/sbom_spdx/my_spdx_document.spdx.json")
    write_file(document, output_file)
#转换成cyclonedx格式
def convertCyclonedx(syft_json,project_name,output_file_cyclone,ExterDependencies):
    lc_factory = LicenseFactory()
    # region build the BOM

    bom = Bom()
    bom.metadata.component = root_component = Component(
        name=project_name,
        type=ComponentType.FILE,
        #licenses=[lc_factory.make_from_string('MIT')],
        bom_ref='myApp',

    )
    # bom.metadata.tools = Tool(
    #     name='jiliqiang',
    #     version='1.0.0',
    #
    # )
    # bom.metadata.tools = Component(
    #     type = ComponentType.APPLICATION,
    #     author= 'ISCA',
    #     name = 'jiliqiang',
    #     version='1.0.0',
    # )
    # 当前的时间
    current_time = datetime.now()
    bom.metadata.timestamp=current_time

    #处理外部依赖
    for externalDependency in ExterDependencies:
        exterpackageRef =f"pkg:deb/debian/{externalDependency.name}@{externalDependency.version}?package-id={uuid.uuid4()}"
        component = Component(
            type = ComponentType.LIBRARY,
            name= externalDependency.name,
            #group=
            version= externalDependency.version,
            bom_ref=exterpackageRef,
            purl=PackageURL('deb','debian',externalDependency.name,externalDependency.version),
            description='External Dependency',
            properties = [
                Property(name="syft:package:type", value='Deb'),
                Property(name="syft:package:purl", value=f"pkg:deb/debian/{externalDependency.name}@{externalDependency.version}")
            ],
        )
        bom.components.add(component)
        bom.register_dependency(root_component, [component])

    #处理内部依赖
    artifacts = syft_json['artifacts']
    for artifact in artifacts:
        innerpackageRef = f"{artifact['purl']}?package-id={artifact['id']}"
        purlString = artifact['purl']
        # organization = re.search(r"pkg:(\w+)/", purlString).group(1)
        # groups = re.search(r"/(\w+)/", purlString).group(1)
        component1 = Component(
            type = ComponentType.LIBRARY,
            name=artifact['name'],
            #group='acme',
            version=artifact['version'],
            #licenses=[lc_factory.make_from_string('(c) 2021 Acme inc.')],
            # supplier=OrganizationalEntity(
            #     name='Acme Inc',
            #     urls=[XsUri('https://www.acme.org')]
            # ),
            bom_ref=innerpackageRef,
            description= 'Inner Dependency',
            properties=[
                Property(name="syft:package:type",value=artifact['type']),
                Property(name="syft:package:purl",value=artifact['purl'])
            ]
            #purl=PackageURL(organization,groups,artifact['name'],artifact['version'])
        )
        bom.components.add(component1)
        bom.register_dependency(root_component, [component1])





    # endregion build the BOM

    # region JSON
    """demo with explicit instructions for SchemaVersion, outputter and validator"""

    my_json_outputter: 'JsonOutputter' = JsonV1Dot5(bom)
    serialized_json = my_json_outputter.output_as_string(indent=2)
    my_json_outputter.output_to_file(output_file_cyclone,True)

    print(serialized_json)
    my_json_validator = JsonStrictValidator(SchemaVersion.V1_6)
    try:
        validation_errors = my_json_validator.validate_str(serialized_json)
        if validation_errors:
            print('JSON invalid', 'ValidationError:', repr(validation_errors), sep='\n', file=sys.stderr)
            sys.exit(2)
        print('JSON valid')
    except MissingOptionalDependencyException as error:
        print('JSON-validation was skipped due to', error)

    # endregion JSON

    print('', '=' * 30, '', sep='\n')
