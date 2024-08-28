FROM centos:latest

WORKDIR /root/rpmbuild

RUN sed -i -e "s|mirrorlist=|#mirrorlist=|g" /etc/yum.repos.d/CentOS-*
RUN sed -i -e "s|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g" /etc/yum.repos.d/CentOS-*
RUN dnf clean all
RUN dnf makecache
RUN dnf install -y python3 rpmdevtools python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install pyinstaller
RUN pip3 install pycurl certifi requests pyrpm wget numpy loguru rarfile winrar pyzstd
RUN pip3 install beartype dataclasses uritools rdflib xmltodict packageurl-python serializable sortedcontainers
RUN rpmdev-setuptree 

COPY * /root/dnfC/

RUN tar czvf ~/rpmbuild/SOURCES/dnfC-1.0.tar.gz /root/dnfC

COPY /SPECS/dnfC.spec ~/rpmbuild/SPECS

RUN rpmbuild -ba SPECS/dnfC.spec


CMD  ["cp","/app/aptc_1.0_all.deb","/mnt/res"]