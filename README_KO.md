# 🖱️ Solaar App Launcher

**Logitech MX Master 3S의 Gesture Button을 활용한 GTK3 앱 런처**

🇺🇸 [English README](README.md)

Gesture Button(엄지 버튼)을 클릭하면 자주 사용하는 앱 목록이 표시되고, 원하는 앱을 바로 실행할 수 있습니다.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![GTK](https://img.shields.io/badge/GTK-3.0-green?logo=gnome&logoColor=white)
![Solaar](https://img.shields.io/badge/Solaar-1.1+-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| 🚀 **빠른 앱 실행** | Gesture Button 한 번으로 앱 런처 표시 → 클릭으로 바로 실행 |
| 📂 **그룹 분류** | 앱을 카테고리별로 그룹화하여 가로 컬럼으로 표시 |
| 🎨 **아이콘 표시** | `.desktop` 파일에서 아이콘을 자동으로 파싱하여 표시 |
| ⠿ **드래그 정렬** | `⠿` 핸들을 드래그하여 앱 순서 변경 및 그룹 간 이동 |
| ➕ **앱 관리** | 설치된 프로그램 목록에서 검색하여 추가 / 삭제 |
| 🌐 **웹사이트 바로가기** | 웹사이트 URL을 직접 추가 — 기본 브라우저로 열기 |
| 📝 **그룹 관리** | 그룹 추가, 이름 변경 (그룹명 클릭) |
| 🔄 **토글 동작** | 런처가 열린 상태에서 다시 누르면 종료 |
| ⌨️ **ESC 종료** | `ESC` 키로 이전 화면 / 종료 |

---

## 📋 요구 사항

- **Linux** (Ubuntu / Fedora / Arch 등)
- **Python 3.8+**
- **GTK 3.0** (`python3-gi`, `gir1.2-gtk-3.0`)
- **Solaar 1.1+** (Logitech Unifying/Bolt 디바이스 매니저)
- **Logitech MX Master 3S** (또는 Gesture Button 지원 마우스)

---

## 🔧 설치

### 1. 의존성 설치

```bash
# Ubuntu / Debian
sudo apt install python3-gi gir1.2-gtk-3.0 solaar

# Fedora
sudo dnf install python3-gobject gtk3 solaar

# Arch Linux
sudo pacman -S python-gobject gtk3 solaar
```

### 2. 앱 런처 설치

```bash
git clone https://github.com/YOUR_USERNAME/solaar-app-launcher.git
cd solaar-app-launcher
chmod +x install.sh
./install.sh
```

설치 스크립트가 다음을 수행합니다:

- `src/` → `~/.local/bin/` 에 실행 파일 복사
- `config/` → `~/.config/solaar/` 에 기본 앱 목록 생성 (기존 파일 보존)

### 3. Solaar 규칙 설정

Solaar GUI 또는 `~/.config/solaar/rules.yaml`을 통해 Gesture Button 규칙을 설정합니다.

#### 방법 A: Solaar GUI

1. Solaar 앱 열기
2. 마우스 선택 → **Rule Editor** 탭
3. 새 규칙 추가:
   - **조건**: `MouseGesture` → `[]` (제스처 없이 클릭)
   - **동작**: `Execute` → `~/.local/bin/solaar-app-launcher.sh`

#### 방법 B: rules.yaml 직접 편집

```yaml
%YAML 1.3
---
- MouseGesture: []
- Execute: [~/.local/bin/solaar-app-launcher.sh]
...
```

> [!IMPORTANT]
> Solaar에서 마우스의 **Gesture Button**이 **Mouse Gestures** 모드로 설정되어 있어야 합니다.
> Solaar → 마우스 선택 → Gesture Button → **Diverted** 또는 **Mouse Gestures** 로 변경하세요.

---

## 📖 사용법

### 기본 사용

1. **MX Master 3S의 Gesture Button** (엄지 아래 버튼)을 **클릭** (움직이지 않고)
2. 앱 런처가 표시됨
3. 원하는 앱을 **클릭하여 실행**
4. 런처가 열린 상태에서 다시 Gesture Button을 누르면 **종료**

### 앱 관리

| 동작 | 방법 |
|------|------|
| 앱 추가 | `➕ 추가` 버튼 → 그룹 선택 → 앱 검색/선택 → 이름/명령 확인 → 저장 |
| 웹사이트 추가 | `➕ 추가` 버튼 → `🌐 웹사이트` → 이름 & URL 입력 → 저장 |
| 앱 삭제 | `➖ 삭제` 버튼 → 체크박스 선택 → 삭제 |
| 앱 순서 변경 | `⠿` 핸들을 **드래그**하여 원하는 위치로 이동 |
| 그룹 추가 | `📂 그룹추가` 버튼 |
| 그룹 이름 변경 | 그룹명(`📂 개발` 등)을 **클릭** |

---

## ⚙️ 설정 파일

### 앱 목록: `~/.config/solaar/app-launcher-apps.conf`

```ini
[개발]
VS Code|code|visual-studio-code
Obsidian|obsidian|obsidian

[시스템]
터미널|gnome-terminal|utilities-terminal
계산기|gnome-calculator|org.gnome.Calculator

[업무/소통]
Zoom|zoom|Zoom
Firefox|firefox|firefox

[웹사이트]
GitHub|xdg-open https://github.com|web-browser
```

**형식:** `표시이름|실행명령|아이콘이름`

| 필드 | 설명 | 예시 |
|------|------|------|
| 표시이름 | 런처에 표시될 이름 | `VS Code` |
| 실행명령 | 터미널에서 실행할 명령 | `code`, `gnome-terminal` |
| 아이콘이름 | GTK 아이콘 테마 이름 또는 절대 경로 | `visual-studio-code` |

> [!TIP]
> 아이콘 이름은 `.desktop` 파일의 `Icon=` 필드에서 확인할 수 있습니다.
>
> ```bash
> grep -r "^Icon=" /usr/share/applications/code.desktop
> ```

---

## 📁 프로젝트 구조

```
solaar-app-launcher/
├── README.md                  # 이 문서
├── install.sh                 # 설치 스크립트
├── LICENSE                    # MIT 라이선스
├── src/
│   ├── solaar-app-launcher.py # 메인 GTK3 앱 (Python)
│   └── solaar-app-launcher.sh # 셸 래퍼 스크립트
└── config/
    ├── app-launcher-apps.conf.example  # 앱 목록 예시
    └── rules.yaml.example              # Solaar 규칙 예시
```

---

## 🔧 Gesture Button 추가 활용 (선택)

Gesture Button에 방향별 동작을 추가할 수 있습니다:

| 제스처 | 동작 | rules.yaml |
|--------|------|------------|
| 클릭 (제자리) | 앱 런처 | `MouseGesture: []` → `Execute` |
| ↑ 위로 | 창 최대화 | `MouseGesture: [Mouse Up]` → `KeyPress: [Super_L, Up]` |
| ↓ 아래로 | 창 최소화 | `MouseGesture: [Mouse Down]` → `KeyPress: [Super_L, Down]` |
| ← 왼쪽 | 뒤로가기 | `MouseGesture: [Mouse Left]` → `KeyPress: XF86_Back` |
| → 오른쪽 | 앞으로가기 | `MouseGesture: [Mouse Right]` → `KeyPress: XF86_Forward` |

전체 예시는 [`config/rules.yaml.example`](config/rules.yaml.example)을 참고하세요.

---

## 🤝 기여

1. 이 저장소를 **Fork** 합니다
2. 기능 브랜치를 만듭니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push 합니다 (`git push origin feature/amazing-feature`)
5. **Pull Request**를 생성합니다

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
