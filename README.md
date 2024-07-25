# dnfC

## 如何在docker内进行测试：
### 构建docker:
```
docker run --name dnfc -v <项目位置>:/code -it centos:8.4.2105 /bin/bash
```
进入docker后，在docker内执行:
```
sed -i -e "s|mirrorlist=|#mirrorlist=|g" /etc/yum.repos.d/CentOS-*
sed -i -e "s|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g" /etc/yum.repos.d/CentOS-*
/usr/bin/yum update
/usr/bin/yum -y install curl-devel gcc python3-devel openssl-devel
echo "alias dnf='dnfc'" >> /etc/bashrc
echo "alias yum='dnfc'" >> /etc/bashrc
pip3 install -r requirements.txt
cd /code
chmod +x install.sh
./install.sh
```
### 运行docker:
```
docker start dnfc
docker exec -it dnfc /bin/bash
```
### 在docker内测试：
apt install xxx，此时会执行检查