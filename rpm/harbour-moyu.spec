Name:       harbour-moyu

%{!?qtc_qmake:%define qtc_qmake %qmake}
%{!?qtc_qmake5:%define qtc_qmake5 %qmake5}
%{!?qtc_make:%define qtc_make make}
%{?qtc_builddir:%define _builddir %qtc_builddir}

%define __requires_exclude ^libxyz\.birdzhang\.moyu\..*$
%global __provides_exclude_from %{_libdir}/qt5/qml/.*

Version:    0.5.9
Release:    1
Summary:    Moyu Rime Pinyin input method for Sailfish OS
License:    GPL-3.0-or-later AND BSD-3-Clause AND BSD-2-Clause AND Apache-2.0 AND LGPL-3.0-only
Group:      Qt/Qt
Source:     %{name}-%{version}.tar.gz
URL:        https://github.com/0312birdzhang/harbour-soumaoime
Requires:   jolla-keyboard >= 0.9.10
Provides:   xyz.birdzhang.moyu.ime = %{version}-%{release}
Obsoletes:  xyz.birdzhang.moyu.ime < %{version}-%{release}
BuildRequires:  pkgconfig(sailfishapp)
BuildRequires:  pkgconfig(Qt5Core)
BuildRequires:  pkgconfig(Qt5Qml)
BuildRequires:  pkgconfig(Qt5Quick)
BuildRequires:  pkgconfig(Qt5DBus)
BuildRequires:  boost-devel
BuildRequires:  boost-regex
BuildRequires:  yaml-cpp-devel
BuildRequires:  desktop-file-utils >= 0.26
BuildRequires:  doxygen >= 1.9.5
BuildRequires:  cmake >= 3.27.1
BuildRequires:  python3-base >= 3.8.18

%description
Provides Rime Pinyin input, user dictionary management and customizable
keyboard layouts for Simplified Chinese on Sailfish OS.


%prep
%setup -q -n %{name}-%{version}

%build

bash tools/build-rime.sh

%qtc_qmake5

%qtc_make %{?_smp_mflags}

MOYU_RIME_DATA_DIR="$PWD/.rime-build/data" \
MOYU_RIME_USER_DIR="$PWD/.rime-build/deployment" \
    ./librime/backend/harbour-moyu-rime --deploy
mkdir -p .rime-build/data/build
cp -a .rime-build/deployment/build/. .rime-build/data/build/


%install
rm -rf %{buildroot}
%qmake5_install

# Windows checkouts may carry CRLF and executable permissions on data files.
python3 - "%{buildroot}" <<'PY'
from pathlib import Path
import sys

text_suffixes = {'.qml', '.js', '.txt', '.yaml', '.desktop', '.conf', '.service', '.profile', '.md'}
paths = [Path('LICENSE')] + list(Path(sys.argv[1]).rglob('*'))
for path in paths:
    if path.is_file() and (path.suffix in text_suffixes or path.name in {'qmldir', 'LICENSE'}):
        path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n'))
PY

# 创建 handlers/ 软链作为包文件，兼容 5.2（从 handlers/ 读取）和低版本（从 com/jolla/ 读取）
mkdir -p %{buildroot}%{_datadir}/maliit/plugins/com/jolla/handlers
cd %{buildroot}%{_datadir}/maliit/plugins/com/jolla/handlers \
  && ln -s ../MoyuPinyinHandler.qml MoyuPinyinHandler.qml

# 移除 find-docs 生成的空文档占位文件
find %{buildroot} -name documentation.list -delete

# << install pre

# >> install post
# << install post

%posttrans
# Complete the renamed-package upgrade after the old package's removal scripts.
systemctl-user daemon-reload || true
systemctl-user try-restart harbour-moyu-rime || true
systemctl-user restart maliit-server || true

%postun
# >> postun
if [ "$1" -eq 0 ]; then
    systemctl-user stop harbour-moyu-rime || true
fi
systemctl-user daemon-reload || true
systemctl-user restart maliit-server || true
# << postun

%clean
rm -rf %{buildroot}

%files
%defattr(0644,root,root,0755)
%attr(0755,root,root) %{_bindir}/harbour-moyu
%attr(0755,root,root) %{_bindir}/harbour-moyu-rime
%{_datadir}/dbus-1/services/xyz.birdzhang.moyu.Rime.service
%{_prefix}/lib/systemd/user/harbour-moyu-rime.service
%license LICENSE
%dir %{_datadir}/licenses/harbour-moyu
%license %{_datadir}/licenses/harbour-moyu/rime
%{_datadir}/maliit/plugins/com/jolla/MoyuPinyinHandler.qml
%{_datadir}/maliit/plugins/com/jolla/handlers/MoyuPinyinHandler.qml
%exclude %{_datadir}/maliit/plugins/com/jolla/handlers/documentation.list
%{_datadir}/maliit/plugins/com/jolla/layouts/layouts_moyu.conf
%{_datadir}/maliit/plugins/com/jolla/layouts/zh_cn_moyu.qml
%{_datadir}/harbour-moyu
%{_datadir}/icons/hicolor/86x86/apps/harbour-moyu.png
%{_datadir}/applications/harbour-moyu.desktop
%config %{_sysconfdir}/sailjail/permissions/harbour-moyu.profile
%dir %{_libdir}/qt5/qml/xyz/birdzhang/moyu
%{_libdir}/qt5/qml/xyz/birdzhang/moyu/ime
%dir %{_datadir}/maliit/plugins/com/jolla
%{_datadir}/maliit/plugins/com/jolla/MoyuKeyboardRow.qml
%{_datadir}/maliit/plugins/com/jolla/MoyuLanguageKey.qml
