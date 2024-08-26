%if 0%{?suse_version} >= 1550
  %define _pam_confdir %{_pam_vendordir}
  %define _config_norepl %nil
%else
  %define _pam_confdir %{_sysconfdir}/pam.d
  %define _config_norepl %config(noreplace)
%endif

Name:           greetd
Version:        0.10.3
Release:        1
Summary:        Minimal and flexible login manager daemon
License:        GPL-3.0-only
Group:          System/Management
URL:            https://git.sr.ht/~kennylevinsen/greetd
Source:         https://git.sr.ht/~kennylevinsen/greetd/archive/%{version}/%{name}-%{version}.tar.gz
Source1:        vendor.tar.xz
Source2:        cargo_config
Source3:        greetd.pam
Source4:        %{name}.sysusers

BuildRequires:  cargo
BuildRequires:  rust-packaging
BuildRequires:  pam-devel
BuildRequires:  systemd-rpm-macros
Requires:       pam

%description
greetd is a login manager daemon. greetd on its own does not have any user interface,
but instead offloads that to greeters, which are arbitrary applications that implement the greetd IPC protocol.

%prep
%autosetup -a1
%cargo_prep -v vendor
#mkdir .cargo
#cp %{SOURCE2} .cargo/config

%build
%cargo_build

%install

install -D -p -m 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}
install -D -p -m 0755 target/release/agreety %{buildroot}%{_bindir}/agreety

# https://github.com/openSUSE/openSUSEway/issues/37
sed -i -e "s|\$SHELL|bash|" config.toml
install -D -p -m 0644 config.toml %{buildroot}/%{_sysconfdir}/%{name}/config.toml

install -D -m 0644 %{name}.service %{buildroot}/%{_unitdir}/%{name}.service

install -D -m 0644 %{SOURCE3} %{buildroot}/%{_pam_confdir}/greetd

install -d %{buildroot}%{_localstatedir}/cache/greetd
install -d %{buildroot}%{_sharedstatedir}/greetd
install -d %{buildroot}/run/greetd

install -D -m644 -vp %{SOURCE4}       %{buildroot}%{_sysusersdir}/%{name}.conf

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_bindir}/agreety
%{_unitdir}/%{name}.service
%{_sysusersdir}/%{name}.conf
%dir %{_sysconfdir}/%{name}
%attr(644,greeter,greeter) %config(noreplace) %{_sysconfdir}/%{name}/config.toml
%_config_norepl %{_pam_confdir}/greetd
%ghost %attr(711,root,greeter) %dir /run/greetd/
%attr(750,greeter,greeter) %dir %{_sharedstatedir}/greetd
%ghost %dir %{_localstatedir}/cache/greetd/
