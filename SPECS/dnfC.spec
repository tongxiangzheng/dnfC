%global _python_bytecompile_errors_terminate_build 0
%define _binaries_in_noarch_packages_terminate_build   0

Name: dnfC
Version: 1.0
Release: 1%{?dist}
Summary: Check package before install 
License:        GPL v2.0
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  python3 python3-pyinstaller curl-devel gcc python3-devel openssl-devel python3-numpy python3-pycurl python3-pyyaml python3-semantic_version python3-chardet python3-jsonschema python3-lxml python3-pyparsing python3-attrs python3-jsonpointer python3-idna python3-six python3-dateutil python3-certifi python3-pyrpm python3-packaging python3-requests python3-referencing

%description
Check package before install 

%prep
rm -rf %{buildroot}
%setup -q

%build
# 如果需要编译或处理其他构建步骤，写在这里
pyinstaller src/dnfc

%install

mkdir -p %{buildroot}/usr/bin
cp %{_builddir}/%{name}-%{version}/dist/dnfc/dnfc %{buildroot}/usr/bin/
mkdir -p %{buildroot}/share/dnfC/spdx/
cp -r %{_builddir}/%{name}-%{version}/src/spdx/spdx11 %{buildroot}/share/dnfC/spdx/
# 根据实际项目调整安装路径和文件复制操作

%files
%defattr(-,root,root,-)
/share/dnfC/*
/usr/bin/dnfc

%post
# 安装后执行的脚本，如设置环境变量、启动服务等
sed -i "/alias dnf='dnfc'/d" /etc/bash.bashrc
sed -i "/alias yum='dnfc'/d" /etc/bash.bashrc
echo "alias dnf='dnfc'" >> /etc/bashrc
echo "alias yum='dnfc'" >> /etc/bashrc
%preun
# 卸载前执行的脚本

%postun
# 卸载后执行的脚本

%changelog
# 描述版本更新历史


