%define distname %{name}-s%{version}

Summary:	Network monitoring tools including ping
Name:		iputils
Version:	20150815
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
Patch0:		iputils-rh.patch
Patch1:		iputils-ifenslave.patch
Patch3:		iputils-locale-i.patch

Requires(pre):	filesystem >= 2.1.9-18
BuildRequires:	docbook-dtd31-sgml
BuildRequires:	perl-SGMLSpm
BuildRequires:	pkgconfig(libidn)
BuildRequires:	sysfsutils-devel
BuildRequires:	cap-devel
BuildRequires:	pkgconfig(libidn)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(gnutls)
BuildRequires:	systemd
Requires(post):	rpm-helper
Requires(preun):	rpm-helper
Requires(postun):	rpm-helper

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
%setup -qn %{distname}

cp %{SOURCE1} .
cp %{SOURCE2} .
cp %{SOURCE3} .
%apply_patches
sed -i -e 's!\$\(MAKE\) -C doc html!!g' Makefile

%build
export CC=%{__cc}
%serverbuild
%make IDN="yes" OPTFLAGS="%{optflags} -fno-strict-aliasing"
%make ifenslave CFLAGS="%{optflags}"

make -C doc man

%install
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_mandir}/man8

install -c clockdiff %{buildroot}%{_sbindir}/

install -c arping -D %{buildroot}/sbin/arping

install -c ping %{buildroot}%{_bindir}/
install -c ifenslave %{buildroot}%{_sbindir}/
install -c ping6 %{buildroot}%{_bindir}/
install -c rdisc %{buildroot}%{_sbindir}/
install -c tracepath %{buildroot}%{_sbindir}/
install -c tracepath6 %{buildroot}%{_sbindir}/
install -c traceroute6 %{buildroot}%{_sbindir}/

install -c doc/*.8 %{buildroot}%{_mandir}/man8/
install -c ifenslave.8 %{buildroot}%{_mandir}/man8/

# these manpages are provided by other packages
rm -f %{buildroot}%{_mandir}/man8/rarpd.8*
rm -f %{buildroot}%{_mandir}/man8/tftpd.8*

#(tpg) systemd support
install -D -m 644 %{SOURCE5} %{buildroot}%{_unitdir}/rdisc.service
install -D -m 644 %{SOURCE6} %{buildroot}%{_unitdir}/ninfod.service

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-rdisc.preset << EOF
enable rdisc.service
EOF

cat > %{buildroot}%{_presetdir}/86-ninfod.preset << EOF
enable ninfod.service
EOF

# apparmor profile
mkdir -p %{buildroot}%{_sysconfdir}/apparmor.d/
install -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/apparmor.d/bin.ping

%posttrans
# if we have apparmor installed, reload if it's being used
if [ -x /sbin/apparmor_parser ]; then
        /sbin/service apparmor condreload
fi

%files
%doc RELNOTES bonding.txt
%config(noreplace) %{_sysconfdir}/apparmor.d/bin.ping
%{_presetdir}/86-rdisc.preset
%{_unitdir}/rdisc.service
%attr(0755,root,root) %{_sbindir}/clockdiff
%attr(0755,root,root) %{_sbindir}/arping
%attr(4755,root,root) %{_sbindir}/traceroute6
%attr(0755,root,root) %{_bindir}/ping
%{_sbindir}/ifenslave
%{_sbindir}/rdisc
%{_bindir}/tracepath
%{_bindir}/tracepath6
%{_sbindir}/ping6
%{_sbindir}/tracepath
%{_sbindir}/tracepath6
%attr(644,root,root) %{_mandir}/man8/clockdiff.8.gz
%attr(644,root,root) %{_mandir}/man8/arping.8.gz
%attr(644,root,root) %{_mandir}/man8/ping.8.gz
%attr(644,root,root) %{_mandir}/man8/ping6.8.gz
%attr(644,root,root) %{_mandir}/man8/rdisc.8.gz
%attr(644,root,root) %{_mandir}/man8/tracepath.8.gz
%attr(644,root,root) %{_mandir}/man8/tracepath6.8.gz
%attr(644,root,root) %{_mandir}/man8/traceroute6.8.gz
%attr(644,root,root) %{_mandir}/man8/ifenslave.8.gz

%files ninfod
%attr(0755,root,root) %{_sbindir}/ninfod
%{_presetdir}/86-ninfod.preset
%{_unitdir}/ninfod.service
%attr(644,root,root) %{_mandir}/man8/ninfod.8.gz
