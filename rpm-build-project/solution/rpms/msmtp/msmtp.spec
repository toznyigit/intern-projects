Name:           msmtp
Version:        1.8.22
Release:        1%{?dist}
Summary:        Labris Networks msmtp rpm build example

License:        GPLv3+
URL:            https://marlam.de/msmtp/
Source0:        https://marlam.de/%{name}/releases/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:	make
BuildRequires:	gettext-devel
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libsecret-devel
BuildRequires:	gnutls-devel

%description
msmtp transmits a mail to an SMTP server which takes care of further delivery.

%prep
%autosetup

%build
gettextize -f
autoreconf -i
./configure
make

%install
%make_install

%files
/usr/local/bin/%{name}
/usr/lib/debug/usr/local/bin/msmtpd-1.8.22-1.el8.x86_64.debug
/usr/local/bin/msmtpd
/usr/local/share/info/dir
/usr/local/share/info/msmtp.info
/usr/local/share/locale/de/LC_MESSAGES/msmtp.mo
/usr/local/share/locale/eo/LC_MESSAGES/msmtp.mo
/usr/local/share/locale/fr/LC_MESSAGES/msmtp.mo
/usr/local/share/locale/pt_BR/LC_MESSAGES/msmtp.mo
/usr/local/share/locale/sr/LC_MESSAGES/msmtp.mo
/usr/local/share/locale/ta/LC_MESSAGES/msmtp.mo
/usr/local/share/locale/uk/LC_MESSAGES/msmtp.mo
/usr/local/share/man/man1/msmtp.1
/usr/local/share/man/man1/msmtpd.1


%changelog
* Fri Aug 12 2022 root
- Test
