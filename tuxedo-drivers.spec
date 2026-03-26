%global         _sysconf_modprobe_d     %{_sysconfdir}/modprobe.d/
%define         buildforkernels         akmod
%global         AkmodsBuildRequires     make gcc sed gawk
%global module_names tuxedo_compatibility_check tuxedo_keyboard clevo_acpi clevo_wmi uniwill_wmi tuxedo_io tuxedo_nb02_nvidia_power_ctrl ite_8291 ite_8291_lb ite_8297 ite_829x tuxedo_nb05_ec tuxedo_nb05_power_profiles tuxedo_nb05_sensors tuxedo_nb05_keyboard tuxedo_nb05_kbd_backlight tuxedo_nb05_fan_control tuxedo_nb04_keyboard tuxedo_nb04_wmi_ab tuxedo_nb04_wmi_bs tuxedo_nb04_sensors tuxedo_nb04_power_profiles tuxedo_nb04_kbd_backlight stk8321 gxtp7380 tuxedo_tuxi_fan_control tuxi_acpi

%if 0%{?fedora}
%global         debug_package           %{nil}
%endif

Name:           tuxedo-drivers
Version:        ${latestVersion}
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

Provides: %{name} = %{version}
Obsoletes: %{name} < 4.0.0

%description
Tuxedo drivers as kmod

%{!?kernels:BuildRequires: buildsys-build-%{repo}-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }
%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%prep
echo "Prepare stage -----------------------------------------------------------------------------------------------"
%setup -q -c -T -a 0
cd %{name}-%{version} || true
for kernel_version  in %{?kernel_versions} ; do
  cp -a src _kmod_build_${kernel_version%%___*}
done

%build
echo "Build stage -----------------------------------------------------------------------------------------------"

for kernel_version in %{?kernel_versions}; do
  make V=1 %{?_smp_mflags} -C /lib/modules/${kernel_version%%___*}/build M=${PWD}/%{name}-%{version}/_kmod_build_${kernel_version%%___*} modules
done

%install
echo "Install stage ---------------------------------------------------------------------------------------------"

for kernel_version in %{?kernel_versions}; do
  mkdir -p %{buildroot}/lib/modules/${kernel_version%%___*}/extra/%{name}/
  install -D -m 755 %{name}-%{version}/_kmod_build_${kernel_version%%___*}/**/*.ko %{buildroot}/lib/modules/${kernel_version%%___*}/extra/%{name}/
  install -D -m 755 %{name}-%{version}/_kmod_build_${kernel_version%%___*}/*.ko %{buildroot}/lib/modules/${kernel_version%%___*}/extra/%{name}/
  chmod a+x %{buildroot}/lib/modules/${kernel_version%%___*}/extra/%{name}/*.ko
done

# install for common
mkdir -p %{buildroot}%{_modulesloaddir}
for module in %{module_names}; do
    echo "$module" > ${module}.conf
    install -D -m 0644 ${module}.conf %{buildroot}%{_modulesloaddir}/${module}.conf
done


# Copy configs
mkdir -p %{buildroot}/usr/lib/modprobe.d/

# Copy udev rules
mkdir -p %{buildroot}/usr/lib/udev/rules.d/
install -D -m 0644 %{name}-%{version}/*.rules %{buildroot}/usr/lib/udev/rules.d/

# Copy udev hwdb
mkdir -p %{buildroot}/usr/lib/udev/hwdb.d/
install -D -m 0644 %{name}-%{version}/*.hwdb %{buildroot}/usr/lib/udev/hwdb.d/

%{?akmod_install}

%files

%changelog

%package kmod-common
Summary:  Tuxedo drivers kmod common files
Requires: %{name}-kmod-common >= %{version}
BuildRequires: systemd-rpm-macros

%description kmod-common
Tuxedo drivers kmod common files

%files kmod-common
%{_modulesloaddir}/*.conf
/usr/lib/udev/rules.d/*.rules
/usr/lib/udev/hwdb.d/*.hwdb
# %doc README.md
# %license debian/copyright

%changelog kmod-common
