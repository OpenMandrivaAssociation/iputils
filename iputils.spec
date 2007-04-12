#rh-20020124-2
%define ipcalcname ipv6calc
%define ipcalcversion 0.19
%define bondingver 1.1.0
%define ver 020927

Summary:	Network monitoring tools including ping
Name:		iputils
Version:	20%{ver}
Release:	%mkrel 10
License:	BSD
Group:		System/Base
URL:		ftp://ftp.inr.ac.ru/ip-routing/
Source0:	http://ftp.sunet.se/pub/os/Linux/ip-routing/iputils-ss%{ver}.tar.bz2
Source1:	bonding-%{bondingver}.tar.bz2
Source2:	ftp://ftp.bieringer.de/pub/linux/IPv6/ipv6calc/%{ipcalcname}-%{ipcalcversion}.tar.bz2
Patch0:		iputils-20001007-rh7.patch
Patch1:		iputils-20020927-datalen.patch
Patch2:		iputils-20020927-ping_sparcfix.patch
Patch3:		iputils-20020124-rdisc-server.patch
Patch4:		iputils-20020124-countermeasures.patch
Patch122:	ipv6calc-0.19-Makefile.patch
Patch124:	ipv6calc-0.19-help-arg.patch
Patch125:	iputils-20020927-fix-traceroute.patch
BuildRequires:	openjade
BuildRequires:	perl-SGMLSpm
BuildRequires:	docbook-dtd31-sgml
Conflicts:	xinetd < 2.1.8.9pre14-2mdk
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
The iputils package contains ping, a basic networking tool. The ping command
sends a series of ICMP protocol ECHO_REQUEST packets to a specified network
host and can tell you if that machine is alive and receiving network traffic.

ipv6calc is a small utility which formats and calculates IPv6 addresses in
different ways. It extends the existing address detection on IPv6 initscript
setup or make life easier in adding reverse IPv6 zones to DNS or using in DNS
queries like  nslookup -q=ANY `ipv6calc -r 3ffe:400:100:f101::1/48
See also here for more details: http://www.bieringer.de/linux/IPv6/

%prep

%setup -q -n %{name} -a 1
%setup -q -D -T -c -a 2 -n %{name}

%patch0 -p1 -b .rh7
%patch1 -p1 -b .datalen
%patch2 -p1 -b .ping_sparcfix
%patch3 -p1 -b .rdisc
%patch4 -p1 -b .counter

%patch122 -p0
%patch124 -p0 -b .helparg
%patch125 -p1

%build
perl -pi -e 's!\$\(MAKE\) -C doc html!!g' Makefile
%make CCOPT="%{optflags}"
%make ifenslave CFLAGS="%{optflags}" -C bonding-%{bondingver}

pushd %{ipcalcname}-%{ipcalcversion} && {
    make clean
    make COPTS="%{optflags}"
} && popd

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

pushd %{ipcalcname}-%{ipcalcversion} && {
    make installonly root=%{buildroot}
} && popd

# these manpages are provided by other packages
rm -f %{buildroot}%{_mandir}/man8/rarpd.8*
rm -f %{buildroot}%{_mandir}/man8/tftpd.8*

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc RELNOTES bonding-%{bondingver}/bonding.txt
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
/bin/ipv6calc


