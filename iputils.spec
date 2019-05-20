%define distname %{name}-s%{version}

Summary:	Network monitoring tools including ping
Name:		iputils
Version:	20190515
Release:	1
License:	BSD
Group:		System/Base
URL:		https://github.com/iputils/iputils
Source0:	https://codeload.github.com/iputils/iputils/%{distname}.tar.gz
# ifenslave.c seems to come from linux-2.6.25/Documentation/networking/ifenslave.c
Source1:	ifenslave.c
# bonding.txt seems to come from linux-2.6.25/Documentation/networking/bonding.txt
Source2:	bonding.txt
Source3:	ifenslave.8
Source4:	bin.ping.apparmor
Source5:	rdisc.service
Source6:	ninfod.service
Patch3:		iputils-ifenslave.patch
BuildRequires:	docbook-dtd31-sgml
BuildRequires:	perl-SGMLSpm >= 1.1-2
BuildRequires:	cap-devel
BuildRequires:	pkgconfig(libidn2)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(gnutls)
BuildRequires:	pkgconfig(libsystemd)
BuildRequires:	systemd-macros
BuildRequires:	xsltproc
BuildRequires:	docbook-style-xsl
BuildRequires:	docbook-style-xsl-ns
BuildRequires:	meson
BuildRequires:	cmake
Requires(post):	filesystem >= 2.1.9-18
Requires(post):	libcap-utils
Requires(post):	rpm-helper

%description
The iputils package contains ping, a basic networking tool. The ping command
sends a series of ICMP protocol ECHO_REQUEST packets to a specified network
host and can tell you if that machine is alive and receiving network traffic.

%package ninfod
Summary:	Node Information Query Daemon
Group:		System/Base
Requires:	%{name} = %{EVRD}

%description ninfod
Node Information Query (RFC4620) daemon. Responds to IPv6 Node Information
Queries.

%prep
%setup -n %{distname}

cp %{SOURCE1} .
cp %{SOURCE2} .
cp %{SOURCE3} .

%autopatch -p1

%build
%ifarch %{ix86}
# FIXME workaround for build failure at link time with clang 7.0-331886, binutils 2.30
export CC=gcc
%else
export CC=%{__cc}
%endif
%serverbuild_hardened

%meson -DBUILD_TFTPD=false -Dsystemunitdir="%{_unitdir}"
%meson_build

%make_build ifenslave CFLAGS="%{optflags} -fPIC"

%install
%meson_install
mkdir -p %{buildroot}{%{_sbindir},/sbin,%{_mandir}/man8}
ln -sf %{_bindir}/ping %{buildroot}%{_sbindir}/ping
ln -sf %{_bindir}/ping %{buildroot}%{_sbindir}/ping6
ln -sf %{_bindir}/tracepath %{buildroot}%{_sbindir}/tracepath
ln -sf %{_bindir}/traceroute6 %{buildroot}%{_sbindir}/traceroute6
# (tpg) compat symlink
ln -sf %{_bindir}/arping %{buildroot}/sbin/arping

install -cp ifenslave %{buildroot}%{_sbindir}/
install -cp ifenslave.8 %{buildroot}%{_mandir}/man8/

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-rdisc.preset << EOF
disable rdisc.service
EOF

cat > %{buildroot}%{_presetdir}/86-ninfod.preset << EOF
enable ninfod.service
EOF

# apparmor profile
mkdir -p %{buildroot}%{_sysconfdir}/apparmor.d/
install -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/apparmor.d/bin.ping

%post
if [ -x /usr/sbin/setcap ]; then
    setcap cap_net_raw+ep /usr/bin/ping ||:
fi

%files
%doc README.md bonding.txt
%config(noreplace) %{_sysconfdir}/apparmor.d/bin.ping
%{_presetdir}/86-rdisc.preset
%{_unitdir}/rdisc.service
%attr(0755,root,root) %{_bindir}/clockdiff
%attr(0755,root,root) %{_bindir}/arping
%attr(4755,root,root) %{_sbindir}/traceroute6
%attr(0755,root,root) %{_bindir}/ping

/sbin/arping
%{_sbindir}/ifenslave
%{_sbindir}/rdisc
%{_sbindir}/ping6
%{_bindir}/tracepath
%{_sbindir}/tracepath
%{_sbindir}/traceroute6
%attr(644,root,root) %{_mandir}/man8/clockdiff.8.*
%attr(644,root,root) %{_mandir}/man8/arping.8.*
%attr(644,root,root) %{_mandir}/man8/ping.8.*
%attr(644,root,root) %{_mandir}/man8/ping6.8.*
%attr(644,root,root) %{_mandir}/man8/rdisc.8.*
%attr(644,root,root) %{_mandir}/man8/tracepath.8.*
%attr(644,root,root) %{_mandir}/man8/traceroute6.8.*
%attr(644,root,root) %{_mandir}/man8/ifenslave.8.*

%files ninfod
%attr(0755,root,root) %{_sbindir}/ninfod
%{_presetdir}/86-ninfod.preset
%{_unitdir}/ninfod.service
%attr(644,root,root) %{_mandir}/man8/ninfod.8.*
