%global optflags %{optflags} -Oz -fpie
%global build_ldflags %{build_ldflags} -pie -Wl,-z,relro,-z,now

Summary:	Network monitoring tools including ping
Name:		iputils
Version:	20210722
Release:	1
License:	BSD
Group:		System/Base
URL:		https://github.com/iputils/iputils
Source0:	https://codeload.github.com/iputils/iputils/%{name}-%{version}.tar.gz
# ifenslave.c seems to come from linux-2.6.25/Documentation/networking/ifenslave.c
Source1:	ifenslave.c
# bonding.txt seems to come from linux-2.6.25/Documentation/networking/bonding.txt
Source2:	bonding.txt
Source3:	ifenslave.8
Source4:	bin.ping.apparmor
Patch3:		iputils-ifenslave.patch
%ifarch riscv64
BuildRequires:	atomic-devel
%endif
BuildRequires:	iproute
BuildRequires:	intltool
BuildRequires:	docbook-style-xsl-ns
BuildRequires:	docbook-dtd31-sgml
BuildRequires:	perl-SGMLSpm >= 1.1-2
BuildRequires:	cap-devel
BuildRequires:	libcap-utils
BuildRequires:	pkgconfig(libidn2)
BuildRequires:	pkgconfig(libsystemd)
BuildRequires:	systemd-rpm-macros
BuildRequires:	xsltproc
BuildRequires:	docbook-style-xsl
BuildRequires:	meson
BuildRequires:	cmake
Requires(post):	filesystem >= 2.1.9-18
%{?systemd_ordering}

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
%setup -q

cp %{SOURCE1} .
cp %{SOURCE2} .
cp %{SOURCE3} .

%autopatch -p1

%build
%meson -DBUILD_TFTPD=false
%meson_build

%make_build ifenslave CFLAGS="%{optflags} -fPIC"

%install
%meson_install
mkdir -p %{buildroot}{%{_sbindir},/sbin,%{_mandir}/man8}
ln -sf %{_bindir}/ping %{buildroot}%{_sbindir}/ping
ln -sf %{_bindir}/ping %{buildroot}%{_sbindir}/ping6
ln -sf %{_bindir}/tracepath %{buildroot}%{_sbindir}/tracepath

# (tpg) compat symlink
ln -sf %{_bindir}/arping %{buildroot}/sbin/arping
ln -sf %{_bindir}/arping %{buildroot}%{_sbindir}/arping
ln -sf %{_bindir}/clockdiff %{buildroot}%{_sbindir}/clockdiff

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

%find_lang %{name}

%files -f %{name}.lang
%doc README.md bonding.txt
%config(noreplace) %{_sysconfdir}/apparmor.d/bin.ping
%{_presetdir}/86-rdisc.preset
%{_unitdir}/rdisc.service
%attr(0755,root,root) %caps(cap_net_raw=p) %{_bindir}/clockdiff
%attr(0755,root,root) %caps(cap_net_raw=p) %{_bindir}/arping
%attr(0755,root,root) %{_bindir}/ping
%{_bindir}/tracepath
/sbin/arping
%{_sbindir}/arping
%{_sbindir}/clockdiff
%{_sbindir}/ifenslave
%{_sbindir}/rdisc
%{_sbindir}/ping
%{_sbindir}/ping6
%{_sbindir}/tracepath
%doc %attr(644,root,root) %{_mandir}/man8/clockdiff.8.*
%doc %attr(644,root,root) %{_mandir}/man8/arping.8.*
%doc %attr(644,root,root) %{_mandir}/man8/ping.8.*
%doc %attr(644,root,root) %{_mandir}/man8/rdisc.8.*
%doc %attr(644,root,root) %{_mandir}/man8/tracepath.8.*
%doc %attr(644,root,root) %{_mandir}/man8/ifenslave.8.*

%files ninfod
%attr(0755,root,root) %{_sbindir}/ninfod
%{_presetdir}/86-ninfod.preset
%{_unitdir}/ninfod.service
%doc %attr(644,root,root) %{_mandir}/man8/ninfod.8.*
