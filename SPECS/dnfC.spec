%global _python_bytecompile_errors_terminate_build 0
%global debug_package %{nil}

Name: dnfC
Version: 1.0
Release: 1%{?dist}
Summary: Check package before install 
License:        GPL v2.0
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python3 python3-pyinstaller
BuildRequires:  python3-pycurl python3-certifi python3-requests python3-pyrpm python3-numpy
#BuildRequires:  python3-semantic_version python3-chardet python3-jsonschema python3-lxml python3-pyparsing
#BuildRequires:  python3-attrs python3-jsonpointer python3-idna python3-six python3-dateutil python3-certifi
#BuildRequires:  python3-pyrpm python3-packaging python3-requests python3-referencing

%description
Check package before install 

%prep
rm -rf %{buildroot}
%setup -q

%build
#pip3 install wget loguru rarfile cyclonedx-bom cyclonedx-python-lib winrar pyzstd
pyinstaller -F src/dnfc

%install

mkdir -p %{buildroot}/usr/bin
cp %{_builddir}/%{name}-%{version}/dist/dnfc %{buildroot}/usr/bin/
mkdir -p %{buildroot}/share/dnfC/spdx/
cp -r %{_builddir}/%{name}-%{version}/src/spdx/spdx11 %{buildroot}/share/dnfC/spdx/
mkdir -p %{buildroot}/share/dnfC/license_expression/
cp -r %{_builddir}/%{name}-%{version}/src/license_expression/data %{buildroot}/share/dnfC/license_expression/
mkdir -p %{buildroot}/share/dnfC/cyclonedx/
cp -r %{_builddir}/%{name}-%{version}/src/cyclonedx %{buildroot}/share/dnfC/

mkdir -p %{buildroot}/etc/
cp -r %{_builddir}/%{name}-%{version}/etc/aptC %{buildroot}/etc/

%files
%defattr(-,root,root,-)
/share/dnfC/*
/usr/bin/dnfc
/etc/aptC/*
%post

sed -i "/set PATH='\/share\/dnfC\/bin;\$PATH'/d" /etc/bashrc
echo "set PATH='/share/dnfC/bin;\$PATH'" >> /etc/bashrc
%preun


%postun


sed -i "/set PATH='/share/dnfC/bin;\$PATH'/d" /etc/bashrc

%changelog



