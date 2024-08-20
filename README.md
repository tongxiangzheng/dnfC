# dnfC

## 如何在docker内进行测试：
### 构建docker:
```
docker run --name dnfc -v <项目位置>:/code -it centos:8.4.2105 /bin/bash
docker run --name dnfc -v <项目位置>:/code -it openeuler/openeuler /bin/bash
```
进入docker后，在docker内执行:
```
sed -i -e "s|mirrorlist=|#mirrorlist=|g" /etc/yum.repos.d/CentOS-*
sed -i -e "s|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g" /etc/yum.repos.d/CentOS-*
yum clean all
yum makecache
(centos)
/usr/bin/yum -y install make curl-devel gcc python3-devel openssl-devel python3-numpy python3-pycurl python3-pyyaml python3-semantic_version python3-chardet python3-jsonschema python3-lxml python3-pyparsing python3-attrs python3-jsonpointer python3-idna python3-six python3-dateutil 
(openEuler)
/usr/bin/yum -y install make curl-devel gcc python3-devel openssl-devel python3-numpy python3-pyyaml python3-semantic_version python3-chardet python3-jsonschema python3-lxml python3-pyparsing python3-attrs python3-jsonpointer python3-idna python3-six python3-dateutil   python3-packaging  python3-referencing

python3-pycurl python3-certifi python3-requests python3-pyrpm python3-numpy



cd /code
#make build
echo "alias dnf='dnfc'" >> /etc/bashrc
echo "alias yum='dnfc'" >> /etc/bashrc
make install
```
### 运行docker:
```
docker start dnfc
docker exec -it dnfc /bin/bash
```
### 在docker内测试：
dnf install xxx，此时会执行检查

## 构建
### 构建软件包
```
sudo dnf install rpmdevtools
sudo pip3 install pyinstaller
rpmdev-setuptree
cd ..
cp dnfC dnfC-1.0 -r
tar czvf ~/rpmbuild/SOURCES/dnfC-1.0.tar.gz dnfC-1.0
cd ~/rpmbuild
rpmbuild -ba SPECS/dnfC.spec
```