%global         modname                 tuxedo-drivers
%global         _sysconf_modprobe_d     %{_sysconfdir}/modprobe.d/
%define         buildforkernels         akmod
%define        __libdir  /usr/lib
%global         AkmodsBuildRequires     make gcc sed gawk

%if 0%{?fedora}
%global         debug_package           %{nil}
%endif

Name:           %{modname}-kmod
Version:  4.22.2
Release:        1%{?dist}
Summary:        Tuxedo drivers as akmod
Group:          System Environment/Kernel
License:        GPL-2.0-or-later
URL:            https://github.com/tuxedocomputers/tuxedo-drivers

Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

BuildRequires: kmodtool
BuildRequires: kernel-devel
BuildRequires: make
BuildRequires: gcc

Provides:       %{name} = %{version}
Provides:       tuxedo-cc-wmi = 4.0.0-1
Provides:       tuxedo-keyboard = 4.0.0-1
Provides:       tuxedo-keyboard-kmod = 4.0.0-1
Provides:       tuxedo-keyboard-ite = 4.0.0-1
Provides:       tuxedo-touchpad-fix = 4.0.0-1
Provides:       tuxedo-wmi-kmod = 4.0.0-1
Provides:       tuxedo-xp-xc-airplane-mode-fix = 4.0.0-1
Provides:       tuxedo-xp-xc-touchpad-key-fix = 4.0.0-1
Obsoletes:      tuxedo-cc-wmi < 4.0.0-1
Obsoletes:      tuxedo-keyboard < 4.0.0-1
Obsoletes:      tuxedo-keyboard-kmod < 4.0.0-1
Obsoletes:      tuxedo-keyboard-ite < 4.0.0-1
Obsoletes:      tuxedo-touchpad-fix < 4.0.0-1
Obsoletes:      tuxedo-wmi-kmod < 4.0.0-1
Obsoletes:      tuxedo-xp-xc-airplane-mode-fix < 4.0.0-1
Obsoletes:      tuxedo-xp-xc-touchpad-key-fix < 4.0.0-1
Conflicts:      tuxedo-keyboard-dkms <= 4.0.0-1
Conflicts:      tuxedo-wmi-dkms <= 4.0.0-1
Conflicts:      tuxedo-keyboard-dkms > 4.0.0-1
Conflicts:      tuxedo-wmi-dkms > 4.0.0-1

%description
Tuxedo drivers as kmod

%{!?kernels:BuildRequires: buildsys-build-%{repo}-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }
%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%prep
echo "Prepare stage -----------------------------------------------------------------------------------------------"
%setup -q -c -T -a 0

for kernel_version  in %{?kernel_versions} ; do
  # prepare kernel build
  rm -rf _kmod_build_${kernel_version%%___*}
  mkdir -p _kmod_build_${kernel_version%%___*}
  tar xzf %{SOURCE0} --strip-components=1 -C _kmod_build_${kernel_version%%___*}
  # prepare common installation
  if [ ! -d "%{modname}-%{version}" ]; then
    mkdir -p %{modname}-%{version}
    tar xzf %{SOURCE0} --strip-components=1 -C %{modname}-%{version}
  fi
done

%build
echo "Build stage -----------------------------------------------------------------------------------------------"

for kernel_version in %{?kernel_versions}; do
  make V=1 %{?_smp_mflags} -C /lib/modules/${kernel_version%%___*}/build M=${PWD}/_kmod_build_${kernel_version%%___*} VERSION=v%{version} modules
done

%install
echo "Install stage ---------------------------------------------------------------------------------------------"

for kernel_version in %{?kernel_versions}; do
  mkdir -p %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
  find _kmod_build_${kernel_version%%___*} -type f -name "*.ko" -exec install -D -m 755 {} %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/ \;
done

# Copy configs
mkdir -p %{buildroot}%{_sysconfdir}/modprobe.d/
cp %{modname}-%{version}/tuxedo_keyboard.conf %{buildroot}%{_sysconfdir}/modprobe.d/

mkdir -p %{buildroot}%{_sysconfdir}/modules-load.d/
cat >%{buildroot}%{_sysconfdir}/modules-load.d/99-tuxedo.conf <<EOF
tuxedo_keyboard
tuxedo_io
clevo_acpi
clevo_wmi
EOF

# Copy udev rules
mkdir -p %{buildroot}%{__libdir}/udev/rules.d/
install -D -m 644 %{modname}-%{version}/*.rules %{buildroot}%{__libdir}/udev/rules.d/

# Copy udev hwdb
mkdir -p %{buildroot}%{__libdir}/udev/hwdb.d/
install -D -m 644 %{modname}-%{version}/*.hwdb %{buildroot}%{__libdir}/udev/hwdb.d/

%{?akmod_install}

%files

%changelog

%package common
Summary:  Tuxedo drivers kmod common files
BuildRequires: systemd-rpm-macros

%description common
Tuxedo drivers kmod common files

%files common
%config(noreplace) %{_sysconfdir}/modprobe.d/tuxedo_keyboard.conf
%config(noreplace) %{_sysconfdir}/modules-load.d/99-tuxedo.conf
%{__libdir}/udev/rules.d/*.rules
%{__libdir}/udev/hwdb.d/*.hwdb
# %doc README.md
# %license debian/copyright

%changelog common
