%define version 20101006
%define distname %{name}-s%{version}

Summary:	Network monitoring tools including ping
Name:		iputils
Version:	%{version}
Release:	%mkrel 2
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
Patch6:		iputils-20020927-addrcache.patch
Patch7:		iputils-20020927-ping-subint.patch
Patch9:		iputils-ifenslave.patch
Patch10:	iputils-s20100418-arping-infiniband.patch
Patch11:	iputils-s20100418-idn.patch
Patch12:	iputils-20070202-traffic_class.patch
Patch13:	iputils-s20100418-arping_timeout.patch
Patch14:	iputils-20071127-output.patch
Patch15:	iputils-s20100418-ia64_align.patch
Patch16:	iputils-20071127-warnings.patch
Patch17:	iputils-s20071127-format_not_a_string_literal_and_no_format_arguments.diff
Patch18:	iputils-s20100418-fix_in6_pktinfo.patch
Patch19:	iputils-s20100418-icmp_return_messages.patch
Patch20:	iputils-s20100418-fix_ping_stats_for_dead_hosts.patch
Patch21:	iputils-s20100418-addoptlags.patch
BuildRequires:	docbook-dtd31-sgml
BuildRequires:	libidn-devel
BuildRequires:	sysfsutils-devel
BuildRequires:	perl-SGMLSpm
BuildRequires:	openssl-devel
Conflicts:	xinetd < 2.1.8.9pre14-2mdk
Conflicts:	apparmor-profiles < 2.1-1.961.5mdv2008.0
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The iputils package contains ping, a basic networking tool. The ping command
sends a series of ICMP protocol ECHO_REQUEST packets to a specified network
host and can tell you if that machine is alive and receiving network traffic.

%prep

%setup -q -n %{distname}

cp %{SOURCE1} .
cp %{SOURCE2} .
cp %{SOURCE3} .

%patch0 -p0 -b .s_addr
%patch2 -p1 -b .ping_sparcfix
%patch3 -p1 -b .rdisc-server
%patch4 -p1 -b .counter
%patch6 -p1 -b .addrcache
%patch7 -p1 -b .ping-subint
%patch9 -p1 -b .addr
%patch10 -p1 -b .infiniband
%patch11 -p1 -b .idn
%patch12 -p1 -b .traffic_class
#%patch13 -p1 -b .arping_timeout
#%patch14 -p1 -b .output
%patch15 -p1 -b .ia64_align
%patch17 -p1 -b .format_not_a_string_literal_and_no_format_arguments
%patch18 -p1 -b .in6_pktinfo
%patch19 -p1 -b .icmp_return_messages
%patch20 -p1 -b .dead-hosts
%patch21 -p1 -b .optflags

%build
%serverbuild
perl -pi -e 's!\$\(MAKE\) -C doc html!!g' Makefile
%make IDN="yes" OPTFLAGS="%{optflags} -fno-strict-aliasing"
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


%changelog
* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 20101006-2mdv2011.0
+ Revision: 665520
- mass rebuild

* Tue Nov 23 2010 Eugeni Dodonov <eugeni@mandriva.com> 20101006-1mdv2011.0
+ Revision: 600271
- Updated to 20101006.
  Drop P22 (merged upstream).

* Sun Aug 22 2010 Tomasz Pawel Gajc <tpg@mandriva.org> 20100418-1mdv2011.0
+ Revision: 572040
- add buildrequires on openssl-devel
- update to new version 20100418
- rediff patches 4,6,7,9,12,15
- diable patches 13 and 14
- Patch22: prevent ping against DOS attacks

  + Oden Eriksson <oeriksson@mandriva.com>
    - P22: security fix for CVE-2010-2529

* Sun Apr 18 2010 Tomasz Pawel Gajc <tpg@mandriva.org> 20100214-1mdv2010.1
+ Revision: 536085
- update to new version 20100214
- drop patch 5, fixed by upstream
- split patch 8 into patch 19 and 20
- Patch21: deal correctly with optflags
- provide better version of patch 11
- disable patches 4,6,7,9,12,14 and 15 (hard to guess which one is still needed, probably none)

* Sun Mar 14 2010 Oden Eriksson <oeriksson@mandriva.com> 20071127-8mdv2010.1
+ Revision: 519011
- rebuild

* Wed Sep 02 2009 Christophe Fergeau <cfergeau@mandriva.com> 20071127-7mdv2010.0
+ Revision: 425374
- rebuild

* Sun Dec 21 2008 Oden Eriksson <oeriksson@mandriva.com> 20071127-6mdv2009.1
+ Revision: 316953
- rediffed one fuzzy patch
- fix build with -Werror=format-security (P17)

  + Olivier Blin <oblin@mandriva.com>
    - revert explicit provide of /sbin/arping, it is handled in media_info/file-deps

  + Frederic Crozat <fcrozat@mandriva.com>
    - add explicit provides for /sbin/arping, fix upgrade from 2008.1

* Sun Jul 27 2008 Oden Eriksson <oeriksson@mandriva.com> 20071127-5mdv2009.0
+ Revision: 250431
- rebuild

* Tue Jul 08 2008 Oden Eriksson <oeriksson@mandriva.com> 20071127-4mdv2009.0
+ Revision: 232779
- sync patches with iputils-20071127-3.fc10.src.rpm
- use more up to date ifenslave code
- "ping www.r?\195?\164ksm?\195?\182rg?\195?\165s.se" works now

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild
    - fix no-buildroot-tag

* Sat Jan 26 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 20071127-2mdv2008.1
+ Revision: 158286
- looks like OPEN_MAX define has been removed from kernel's limits.h, fix this with patch 5
- add more ICMP return codes with patch 6 from Debian

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild with fixed %%serverbuild macro

* Sun Dec 30 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 20071127-1mdv2008.1
+ Revision: 139639
- new snapshot
- drop useless buildrequires

* Mon Dec 17 2007 Thierry Vignaud <tv@mandriva.org> 20070202-3mdv2008.1
+ Revision: 127142
- kill re-definition of %%buildroot on Pixel's request

* Wed Sep 19 2007 Andreas Hasenack <andreas@mandriva.com> 20070202-3mdv2008.0
+ Revision: 91193
- ship apparmor profile and use it if apparmor is in effect

* Wed Jun 27 2007 Andreas Hasenack <andreas@mandriva.com> 20070202-2mdv2008.0
+ Revision: 45087
- using serverbuild macro (-fstack-protector-all)

* Fri Apr 20 2007 Olivier Blin <oblin@mandriva.com> 20070202-1mdv
+ Revision: 16253
- fix URL
- 20070202 version
- Patch0: fix build by using s_addr field
- drop rh7 patch
- drop merged datalen patch and buggy datalen patches
- rediff ping_sparcfix and rdisc-server patches
- drop ipv6calc, it is now in its own package


* Sun Mar 18 2007 Oden Eriksson <oeriksson@mandriva.com> 20020927-10mdv2007.1
+ Revision: 145736
- prevent man page file clashes

* Sat Mar 17 2007 Oden Eriksson <oeriksson@mandriva.com> 20020927-9mdv2007.1
+ Revision: 145453
- rebuild
- rebuild
- Import iputils

* Wed Nov 22 2006 Oden Eriksson <oeriksson@mandriva.com> 20020927-7
- bunzip patches
- spec file massage

* Sat Dec 31 2005 Mandriva Linux Team <http://www.mandrivaexpert.com/> 
- Rebuild

* Sun May 16 2004 Luca Berra <bluca@vodka.it> 20020927-5mdk 
- bonding 1.1.0 from kernel source + debian manpage

