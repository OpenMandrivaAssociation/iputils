%define version 20071127
%define distname %{name}-s%{version}

Summary:	Network monitoring tools including ping
Name:		iputils
Version:	%{version}
Release:	%mkrel 6
License:	BSD
Group:		System/Base
URL:		http://linux-net.osdl.org/index.php/Iputils
Source0:	http://www.skbuff.net/iputils/%{distname}.tar.bz2
# ifenslave.c seems to come from linux-2.6.25/Documentation/networking/ifenslave.c
Source1:	ifenslave.c
# bonding.txt seems to come from linux-2.6.25/Documentation/networking/bonding.txt
Source2:	bonding.txt
Source3:	ifenslave.8
Source4:	bin.ping.apparmor
Patch0:		iputils-s20070202-s_addr.patch
Patch2:		iputils-s20070202-ping_sparcfix.patch
Patch3:		iputils-s20070202-rdisc-server.patch
Patch4:		iputils-20020124-countermeasures.patch
Patch5:		iputils-s20071127-OPEN_MAX-is-dead.patch
Patch6:		iputils-20020927-addrcache.patch
Patch7:		iputils-20020927-ping-subint.patch
Patch8:		iputils-ping_cleanup.patch
Patch9:		iputils-ifenslave.patch
Patch10:	iputils-20020927-arping-infiniband.patch
Patch11:	iputils-20070202-idn.patch
Patch12:	iputils-20070202-traffic_class.patch
Patch13:	iputils-20070202-arping_timeout.patch
Patch14:	iputils-20071127-output.patch
Patch15:	iputils-20070202-ia64_align.patch
Patch16:	iputils-20071127-warnings.patch
BuildRequires:	docbook-dtd31-sgml
BuildRequires:	libidn-devel
BuildRequires:	libsysfs-devel
BuildRequires:	perl-SGMLSpm
Conflicts:	xinetd < 2.1.8.9pre14-2mdk
Conflicts:	apparmor-profiles < 2.1-1.961.5mdv2008.0
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Provides:	/sbin/arping

%description
The iputils package contains ping, a basic networking tool. The ping command
sends a series of ICMP protocol ECHO_REQUEST packets to a specified network
host and can tell you if that machine is alive and receiving network traffic.

%prep

%setup -q -n %{distname}

cp %{SOURCE1} .
cp %{SOURCE2} .
cp %{SOURCE3} .

%patch0 -p1 -b .s_addr
%patch2 -p1 -b .ping_sparcfix
%patch3 -p1 -b .rdisc-server
%patch4 -p1 -b .counter
%patch5 -p1 -b .openmax
%patch6 -p1 -b .addrcache
%patch7 -p1 -b .ping-subint
%patch8 -p1 -b .cleanup
%patch9 -p1 -b .addr
%patch10 -p1 -b .infiniband
%patch11 -p1 -b .idn
%patch12 -p1 -b .traffic_class
%patch13 -p1 -b .arping_timeout
%patch14 -p1 -b .output
%patch15 -p1 -b .ia64_align
%patch16 -p1 -b .warnings

%build
%serverbuild
perl -pi -e 's!\$\(MAKE\) -C doc html!!g' Makefile
%make CCOPT="%{optflags}"
%make ifenslave CFLAGS="%{optflags}"

make man

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_bindir}
install -d %{buildroot}/{bin,sbin}
install -d %{buildroot}%{_mandir}/man8

install -c clockdiff		%{buildroot}%{_sbindir}/

install -c arping %{buildroot}/sbin/
ln -s ../../sbin/arping %{buildroot}%{_sbindir}/arping

install -c ping %{buildroot}/bin/
install -c ifenslave %{buildroot}/sbin/
install -c ping6 %{buildroot}%{_bindir}
install -c rdisc %{buildroot}%{_sbindir}/
install -c tracepath %{buildroot}%{_sbindir}/
install -c tracepath6 %{buildroot}%{_sbindir}/
install -c traceroute6 %{buildroot}%{_sbindir}/

install -c doc/*.8 %{buildroot}%{_mandir}/man8/
install -c ifenslave.8 %{buildroot}%{_mandir}/man8/

# these manpages are provided by other packages
rm -f %{buildroot}%{_mandir}/man8/rarpd.8*
rm -f %{buildroot}%{_mandir}/man8/tftpd.8*

# apparmor profile
mkdir -p %{buildroot}%{_sysconfdir}/apparmor.d/
install -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/apparmor.d/bin.ping

%posttrans
# if we have apparmor installed, reload if it's being used
if [ -x /sbin/apparmor_parser ]; then
        /sbin/service apparmor condreload
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc RELNOTES bonding.txt
%config(noreplace) %{_sysconfdir}/apparmor.d/bin.ping
%{_sbindir}/clockdiff
%attr(4755,root,root)	/bin/ping
/sbin/arping
%{_sbindir}/arping
/sbin/ifenslave
#%ifnarch ppc
%attr(4755,root,root) %{_bindir}/ping6
%{_sbindir}/tracepath6
#%endif
%{_sbindir}/tracepath
%attr(4755,root,root) %{_sbindir}/traceroute6
%{_sbindir}/rdisc
%{_mandir}/man8/*
