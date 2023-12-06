Name:           adw-tweaks
Version:        39
Release:        28%{?dist}
Summary:        Libadwaita Tweak Tool forked from risiTweaks

License:        GPL v3
URL:            https://github.com/pizzalovingnerd/adwTweaks
Source0:        https://github.com/pizzalovingnerd/adwTweaks/archive/refs/heads/main.tar.gz

BuildArch:	noarch

BuildRequires:  python
Requires:       python
Requires:	    python3-gobject
Requires:       python3-yaml
Requires:       rtheme-lib

Conflicts:      adw-tweaks
Provides:		adw-tweaks

%description
The tweak tool for risiOS. Full alternative to GNOME Tweaks

%prep
%autosetup -n risiTweaksAdw-main

%build
%install

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
mkdir -p %{buildroot}%{_datadir}/applications

cp -a adw-tweaks %{buildroot}%{_datadir}/risiTweaks
cp io.risi.Tweaks.desktop %{buildroot}%{_datadir}/applications/io.risi.Tweaks.desktop
cp io.risi.Tweaks.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/io.risi.Tweaks.svg

cat > adw-tweaks-bin <<EOF
#!/bin/sh
/usr/bin/env python %{_datadir}/risi-tweaks/__main__.py
EOF
install -m 755 adw-tweaks-bin %{buildroot}%{_bindir}/adw-tweaks

%files
# %license add-license-file-here
# %doc add-docs-here
%{_datadir}/risi-tweaks/*.py
%{_datadir}/applications/io.risi.Tweaks.desktop
%{_datadir}/icons/hicolor/scalable/apps/io.risi.Tweaks.svg
%{_bindir}/adw-tweaks

%changelog
* Tue May 02 2023 PizzaLovingNerd
- Libadwaita redesign

* Fri Sep 02 2022 PizzaLovingNerd
- Changed version scheme to match risiOS
- Made button borders invisible in color selection window

* Sun Aug 07 2022 PizzaLovingNerd
- Added accent colors 

* Tue Jul 13 2021 PizzaLovingNerd
- First spec file
