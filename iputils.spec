%define bondingver 1.1.0
%define version 20071127
%define release %mkrel 1
%define distname %{name}-s%{version}

Summary:	Network monitoring tools including ping
Name:		iputils
Version:	%{version}
Release:	%{release}
License:	BSD
Group:		System/Base
URL:		http://linux-net.osdl.org/index.php/Iputils
Source0:	http://www.skbuff.net/iputils/%{distname}.tar.bz2
Source1:	bonding-%{bondingver}.tar.bz2
Source2:	bin.ping.apparmor
Patch0:		iputils-s20070202-s_addr.patch
Patch2:		iputils-s20070202-ping_sparcfix.patch
Patch3:		iputils-s20070202-rdisc-server.patch
Patch4:		iputils-20020124-countermeasures.patch
BuildRequires:	perl-SGMLSpm
BuildRequires:	docbook-dtd31-sgml
Conflicts:	xinetd < 2.1.8.9pre14-2mdk
Conflicts:	apparmor-profiles < 2.1-1.961.5mdv2008.0

%description
The iputils package contains ping, a basic networking tool. The ping command
sends a series of ICMP protocol ECHO_REQUEST packets to a specified network
host and can tell you if that machine is alive and receiving network traffic.

%prep

%setup -q -n %{distname} -a 1
%patch0 -p1 -b .s_addr
%patch2 -p1 -b .ping_sparcfix
%patch3 -p1 -b .rdisc-server
%patch4 -p1 -b .counter

%build
%serverbuild
perl -pi -e 's!\$\(MAKE\) -C doc html!!g' Makefile
%make CCOPT="%{optflags}"
%make ifenslave CFLAGS="%{optflags}" -C bonding-%{bondingver}

make -C doc man

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
install -c bonding-%{bondingver}/ifenslave %{buildroot}/sbin/
install -c ping6 %{buildroot}%{_bindir}
install -c rdisc %{buildroot}%{_sbindir}/
install -c tracepath %{buildroot}%{_sbindir}/
install -c tracepath6 %{buildroot}%{_sbindir}/
install -c traceroute6 %{buildroot}%{_sbindir}/

install -c doc/*.8 %{buildroot}%{_mandir}/man8/
install -c bonding-%{bondingver}/ifenslave.8 %{buildroot}%{_mandir}/man8/

# these manpages are provided by other packages
rm -f %{buildroot}%{_mandir}/man8/rarpd.8*
rm -f %{buildroot}%{_mandir}/man8/tftpd.8*

# apparmor profile
mkdir -p %{buildroot}%{_sysconfdir}/apparmor.d/
install -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/apparmor.d/bin.ping

%posttrans
# if we have apparmor installed, reload if it's being used
if [ -x /sbin/apparmor_parser ]; then
        /sbin/service apparmor condreload
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc RELNOTES bonding-%{bondingver}/bonding.txt
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
