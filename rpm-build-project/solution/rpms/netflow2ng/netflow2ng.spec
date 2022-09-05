Name:           netflow2ng
Version:        0.0.3
Release:        1%{?dist}
Summary:        NetFlow v9 collector for ntopng
Source0:	netflow2ng-0.0.3.tar.gz

License:        MIT

BuildRequires:	make
BuildRequires:	golang
BuildRequires:	zeromq-devel
BuildRequires:	git
BuildRequires:	epel-release

Requires:	zeromq

%description

%prep
%autosetup


%build
make
mkdir -p %{buildroot}/%{_bindir}/%{name}
cp ./dist/%{name}-%{version} %{buildroot}/%{_bindir}/

%files
%{_bindir}/%{name}-%{version}

%changelog
* Mon Aug 15 2022 root
- 
