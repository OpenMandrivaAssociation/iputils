%define distname %{name}-s%{version}

Summary:	Network monitoring tools including ping
Name:		iputils
Version:	20101006
Release:	2
License:	BSD
Group:		System/Base
Url:		http://linux-net.osdl.org/index.php/Iputils
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
Patch6:		iputils-20020927-addrcache.patch
Patch7:		iputils-20020927-ping-subint.patch
Patch9:		iputils-ifenslave.patch
Patch10:	iputils-s20100418-arping-infiniband.patch
Patch11:	iputils-s20100418-idn.patch
Patch12:	iputils-20070202-traffic_class.patch
#Patch13:	iputils-s20100418-arping_timeout.patch
#Patch14:	iputils-20071127-output.patch
Patch15:	iputils-s20100418-ia64_align.patch
#Patch16:	iputils-20071127-warnings.patch
Patch17:	iputils-s20071127-format_not_a_string_literal_and_no_format_arguments.diff
Patch18:	iputils-s20100418-fix_in6_pktinfo.patch
Patch19:	iputils-s20100418-icmp_return_messages.patch
Patch20:	iputils-s20100418-fix_ping_stats_for_dead_hosts.patch
Patch21:	iputils-s20100418-addoptlags.patch

BuildRequires:	docbook-dtd31-sgml
BuildRequires:	perl-SGMLSpm
BuildRequires:	sysfsutils-devel
BuildRequires:	pkgconfig(libidn)
BuildRequires:	pkgconfig(openssl)

%description
The iputils package contains ping, a basic networking tool. The ping command
sends a series of ICMP protocol ECHO_REQUEST packets to a specified network
host and can tell you if that machine is alive and receiving network traffic.

%prep
%setup -qn %{distname}
cp %{SOURCE1} .
cp %{SOURCE2} .
cp %{SOURCE3} .

%apply_patches
sed -i -e 's!\$\(MAKE\) -C doc html!!g' Makefile

%build
%serverbuild
%make IDN="yes" OPTFLAGS="%{optflags} -fno-strict-aliasing"
%make ifenslave CFLAGS="%{optflags}"

make man

%install
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

%files
%doc RELNOTES bonding.txt
%config(noreplace) %{_sysconfdir}/apparmor.d/bin.ping
%{_sbindir}/clockdiff
%attr(4755,root,root) /bin/ping
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

