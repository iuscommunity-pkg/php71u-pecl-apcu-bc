# IUS spec file for php71u-pecl-apcu-bc, forked from:
#
# Fedora spec file for php-pecl-apcu-bc
# without SCL compatibility, from
#
# remirepo spec file for php-pecl-apcu-bc
#
# Copyright (c) 2015-2016 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%global pecl_name  apcu_bc
%global ext_name   apc
%global apcver     %(%{_bindir}/php -r 'echo (phpversion("apcu")?:0);' 2>/dev/null || echo 65536)
# After 40-apcu.ini
%global ini_name   50-%{ext_name}.ini
%global php        php71u

%bcond_without zts

Name:           %{php}-pecl-apcu-bc
Summary:        APCu Backwards Compatibility Module
Version:        1.0.3
Release:        1.ius%{?dist}
Source0:        http://pecl.php.net/get/%{pecl_name}-%{version}.tgz

License:        PHP
Group:          Development/Languages
URL:            https://pecl.php.net/package/%{pecl_name}

BuildRequires:  %{php}-devel
BuildRequires:  pecl >= 1.10.0
BuildRequires:  %{php}-pecl-apcu-devel >= 5.1.2

Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}
Requires:       %{php}-pecl-apcu%{?_isa} >= 5.1.2

Requires(post): pecl >= 1.10.0
Requires(postun): pecl >= 1.10.0

# provide the stock name
Provides:       php-pecl-apc              = %{apcver}
Provides:       php-pecl-apc%{?_isa}      = %{apcver}
Provides:       php-pecl-apcu-bc          = %{version}
Provides:       php-pecl-apcu-bc%{?_isa}  = %{version}

# provide the stock and IUS names without pecl
Provides:       php-apc                   = %{apcver}
Provides:       php-apc%{?_isa}           = %{apcver}
Provides:       %{php}-apc                = %{apcver}
Provides:       %{php}-apc%{?_isa}        = %{apcver}
Provides:       php-apcu-bc               = %{version}
Provides:       php-apcu-bc%{?_isa}       = %{version}
Provides:       %{php}-apcu-bc            = %{version}
Provides:       %{php}-apcu-bc%{?_isa}    = %{version}

# provide the stock and IUS names in pecl() format
Provides:       php-pecl(APC)             = %{apcver}
Provides:       php-pecl(APC)%{?_isa}     = %{apcver}
Provides:       %{php}-pecl(APC)          = %{apcver}
Provides:       %{php}-pecl(APC)%{?_isa}  = %{apcver}
Provides:       php-pecl(%{pecl_name})         = %{version}
Provides:       php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides:       %{php}-pecl(%{pecl_name})         = %{version}
Provides:       %{php}-pecl(%{pecl_name})%{?_isa} = %{version}

# conflict with the stock name
Conflicts:      php-pecl-apc              < %{apcver}
Conflicts:      php-pecl-apcu-bc          < %{version}

%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_provides_in: %filter_provides_in %{php_ztsextdir}/.*\.so$}
%{?filter_setup}


%description
This module provides a backwards compatible API for APC.


%prep
%setup -qc
mv %{pecl_name}-%{version} NTS

# Don't install/register tests
sed -e 's/role="test"/role="src"/' \
    -e '/LICENSE/s/role="doc"/role="src"/' \
    -i package.xml

# Sanity check, really often broken
extver=$(sed -n '/#define PHP_APCU_BC_VERSION/{s/.* "//;s/".*$//;p}' NTS/php_apc.h)
if test "x${extver}" != "x%{version}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}.
   exit 1
fi

%if %{with zts}
# duplicate for ZTS build
cp -pr NTS ZTS
%endif

cat << 'EOF' | tee %{ini_name}
; Enable %{summary}
extension=%{ext_name}.so
EOF

: Build apcu_bc %{version} with apcu %{apcver}


%build
pushd NTS
%{_bindir}/phpize
%configure \
   --enable-apcu-bc \
   --with-php-config=%{_bindir}/php-config
%make_build
popd

%if %{with zts}
pushd ZTS
%{_bindir}/zts-phpize
%configure \
   --enable-apcu-bc \
   --with-php-config=%{_bindir}/zts-php-config
%make_build
popd
%endif


%install
# Install the NTS stuff
make -C NTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

%if %{with zts}
# Install the ZTS stuff
make -C ZTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

# Install the package XML file
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml

# Documentation
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
pushd NTS
# Check than both extensions are reported (BC mode)
%{__php} -n \
   -d extension=apcu.so \
   -d extension=%{buildroot}%{php_extdir}/apc.so \
   -m | grep 'apc$'

# Upstream test suite for NTS extension
TEST_PHP_EXECUTABLE=%{__php} \
TEST_PHP_ARGS="-n -d extension=apcu.so -d extension=%{buildroot}%{php_extdir}/apc.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__php} -n run-tests.php --show-diff
popd

%if %{with zts}
pushd ZTS
%{__ztsphp} -n \
   -d extension=apcu.so \
   -d extension=%{buildroot}%{php_ztsextdir}/apc.so \
   -m | grep 'apc$'

# Upstream test suite for ZTS extension
TEST_PHP_EXECUTABLE=%{__ztsphp} \
TEST_PHP_ARGS="-n -d extension=apcu.so -d extension=%{buildroot}%{php_ztsextdir}/apc.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__ztsphp} -n run-tests.php --show-diff
popd
%endif


%post
%{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ]; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%license NTS/LICENSE
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{pecl_name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/apc.so

%if %{with zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/apc.so
%endif


%changelog
* Tue Mar 21 2017 Carl George <carl.george@rackspace.com> - 1.0.3-1.ius
- Port from Fedora to IUS
- Install package.xml as %%{pecl_name}.xml, not %%{name}.xml
- Re-add scriptlets (file triggers not yet available in EL)
- Use modern conditional for zts

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Nov 14 2016 Remi Collet <remi@fedoraproject.org> - 1.0.3-4
- rebuild for https://fedoraproject.org/wiki/Changes/php71

* Sun Jun 26 2016 Remi Collet <remi@fedoraproject.org> - 1.0.3-3
- drop SCL stuff for Fedora review

* Mon Mar  7 2016 Remi Collet <remi@fedoraproject.org> - 1.0.3-2
- fix apcver macro definition

* Thu Feb 11 2016 Remi Collet <remi@fedoraproject.org> - 1.0.3-1
- Update to 1.0.3 (beta)

* Fri Jan 29 2016 Remi Collet <remi@fedoraproject.org> - 1.0.2-1
- Update to 1.0.2 (beta)

* Wed Jan  6 2016 Remi Collet <remi@fedoraproject.org> - 1.0.1-1
- Update to 1.0.1 (beta)

* Mon Jan  4 2016 Remi Collet <remi@fedoraproject.org> - 1.0.1-0
- test build for upcoming 1.0.1

* Sat Dec 26 2015 Remi Collet <remi@fedoraproject.org> - 1.0.0-2
- missing dependency on APCu

* Mon Dec  7 2015 Remi Collet <remi@fedoraproject.org> - 1.0.0-1
- Update to 1.0.0 (beta)

* Mon Dec  7 2015 Remi Collet <remi@fedoraproject.org> - 1.0.0-0.2
- test build of upcomming 1.0.0

* Fri Dec  4 2015 Remi Collet <remi@fedoraproject.org> - 5.1.2-0.1.20151204git52b97a7
- test build of upcomming 5.1.2
- initial package
