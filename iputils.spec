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

%build
export CC=%{__cc}
%serverbuild_hardened
%make OPTFLAGS="%{optflags} -fno-strict-aliasing"

pushd ninfod
%configure
%make
popd

%make ifenslave CFLAGS="%{optflags}"
make man

%install
mkdir -p %{buildroot}/sbin
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}

install -c clockdiff %{buildroot}%{_sbindir}/
install -cp arping %{buildroot}%{_sbindir}/
install -cp ping %{buildroot}%{_bindir}/
install -cp rdisc %{buildroot}%{_sbindir}/
install -cp ping6 %{buildroot}%{_bindir}/
install -cp ifenslave %{buildroot}%{_sbindir}/
install -cp tracepath %{buildroot}%{_sbindir}/
install -cp tracepath6 %{buildroot}%{_sbindir}/
install -cp traceroute6 %{buildroot}%{_sbindir}/
install -cp ninfod/ninfod %{buildroot}%{_sbindir}/

mkdir -p %{buildroot}%{_bindir}
ln -sf ../bin/ping6 %{buildroot}%{_sbindir}
ln -sf ../sbin/tracepath %{buildroot}%{_bindir}
ln -sf ../sbin/tracepath6 %{buildroot}%{_bindir}
ln -sf ../sbin/traceroute6 %{buildroot}%{_bindir}
# (tpg) compat symlink
ln -sf ../sbin/arping %{buildroot}/sbin

mkdir -p %{buildroot}%{_mandir}/man8
install -cp doc/clockdiff.8 %{buildroot}%{_mandir}/man8/
install -cp doc/arping.8 %{buildroot}%{_mandir}/man8/
install -cp doc/ping.8 %{buildroot}%{_mandir}/man8/
install -cp doc/rdisc.8 %{buildroot}%{_mandir}/man8/
install -cp doc/tracepath.8 %{buildroot}%{_mandir}/man8/
install -cp doc/ninfod.8 %{buildroot}%{_mandir}/man8/
install -c ifenslave.8 %{buildroot}%{_mandir}/man8/
ln -s ping.8.gz %{buildroot}%{_mandir}/man8/ping6.8.gz
ln -s tracepath.8.gz %{buildroot}%{_mandir}/man8/tracepath6.8.gz

iconv -f ISO88591 -t UTF8 RELNOTES -o RELNOTES.tmp
touch -r RELNOTES RELNOTES.tmp
mv -f RELNOTES.tmp RELNOTES

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
%attr(0755,root,root) %{_bindir}/ping6
/sbin/arping
%{_sbindir}/ifenslave
%{_sbindir}/rdisc
%{_bindir}/tracepath
%{_bindir}/tracepath6
%{_sbindir}/ping6
%{_sbindir}/tracepath
%{_sbindir}/tracepath6
%{_bindir}/traceroute6
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
