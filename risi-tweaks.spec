Name:           risi-tweaks
Version:        38
Release:        23%{?dist}
Summary:        risiOS's Tweak Tool

License:        GPL v3
URL:            https://github.com/risiOS/risiTweaksAdw
Source0:        https://github.com/risiOS/risiTweaksAdw/archive/refs/heads/main.tar.gz

BuildArch:	noarch

BuildRequires:  python
Requires:       python
Requires:	    python3-gobject
Requires:       python3-yaml
Requires:       rtheme-lib

Conflicts:      risi-tweaks
Provides:		risi-tweaks

%description
The tweak tool for risiOS. Full alternative to GNOME Tweaks

%prep
%autosetup -n risi-tweaks-main

%build
%install

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/risiTweaks
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
mkdir -p %{buildroot}%{_datadir}/applications

cp -a risi-tweaks %{buildroot}%{_datadir}/risi-tweaks
cp io.risi.Tweaks.desktop %{buildroot}%{_datadir}/applications/io.risi.Tweaks.desktop
cp io.risi.Tweaks.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/io.risi.Tweaks.svg

cat > risi-tweaks <<EOF
#!/bin/sh
/usr/bin/env python %{_datadir}/risiTweaks/__main__.py
EOF
install -m 755 risi-tweaks %{buildroot}%{_bindir}

%files
# %license add-license-file-here
# %doc add-docs-here
%dir %{_datadir}/risi-tweaks
%{_datadir}/applications/io.risi.Tweaks.desktop
%{_datadir}/icons/hicolor/scalable/apps/io.risi.Tweaks.svg
%{_bindir}/risi-tweaks

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
