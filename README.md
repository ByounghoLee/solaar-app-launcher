# 🖱️ Solaar App Launcher

**A GTK3 App Launcher for Logitech MX Master 3S Gesture Button**

Click the Gesture Button (thumb button) to display a list of your favorite apps and launch them instantly.

🇰🇷 [한국어 README](README_KO.md)

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![GTK](https://img.shields.io/badge/GTK-3.0-green?logo=gnome&logoColor=white)
![Solaar](https://img.shields.io/badge/Solaar-1.1+-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🚀 **Quick Launch** | One click on Gesture Button to show launcher → click to run |
| 📂 **Group Categories** | Organize apps into groups displayed as horizontal columns |
| 🎨 **App Icons** | Automatically parsed from `.desktop` files |
| ⠿ **Drag to Reorder** | Drag the `⠿` handle to rearrange apps or move between groups |
| ➕ **App Management** | Search & add from installed programs / delete apps |
| 📝 **Group Management** | Add new groups, rename by clicking group header |
| 🔄 **Toggle Behavior** | Press again while open to close the launcher |
| ⌨️ **ESC to Close** | Press `ESC` to go back or quit |

---

## 📋 Requirements

- **Linux** (Ubuntu / Fedora / Arch, etc.)
- **Python 3.8+**
- **GTK 3.0** (`python3-gi`, `gir1.2-gtk-3.0`)
- **Solaar 1.1+** (Logitech Unifying/Bolt device manager)
- **Logitech MX Master 3S** (or any mouse with Gesture Button support)

---

## 🔧 Installation

### 1. Install Dependencies

```bash
# Ubuntu / Debian
sudo apt install python3-gi gir1.2-gtk-3.0 solaar

# Fedora
sudo dnf install python3-gobject gtk3 solaar

# Arch Linux
sudo pacman -S python-gobject gtk3 solaar
```

### 2. Install App Launcher

```bash
git clone https://github.com/YOUR_USERNAME/solaar-app-launcher.git
cd solaar-app-launcher
chmod +x install.sh
./install.sh
```

The install script will:

- Copy executables to `~/.local/bin/`
- Create a default app list at `~/.config/solaar/app-launcher-apps.conf` (preserves existing)

### 3. Configure Solaar Rules

Set up the Gesture Button rule via Solaar GUI or by editing `~/.config/solaar/rules.yaml`.

#### Option A: Solaar GUI

1. Open Solaar
2. Select your mouse → **Rule Editor** tab
3. Add a new rule:
   - **Condition**: `MouseGesture` → `[]` (click without gesture)
   - **Action**: `Execute` → `~/.local/bin/solaar-app-launcher.sh`

#### Option B: Edit rules.yaml

```yaml
%YAML 1.3
---
- MouseGesture: []
- Execute: [~/.local/bin/solaar-app-launcher.sh]
...
```

> [!IMPORTANT]
> Make sure the **Gesture Button** is set to **Mouse Gestures** (Diverted) mode in Solaar.
> Solaar → Select mouse → Gesture Button → Change to **Diverted** or **Mouse Gestures**.

---

## 📖 Usage

### Basic Usage

1. **Click** the MX Master 3S **Gesture Button** (thumb button, no movement)
2. App Launcher appears
3. **Click** any app to launch it
4. **Press Gesture Button again** while open → closes the launcher

### App Management

| Action | How |
|--------|-----|
| Add app | `➕ Add` → Select group → Search/select app → Confirm name/command → Save |
| Delete app | `➖ Delete` → Check apps → Delete |
| Reorder apps | **Drag** the `⠿` handle to the desired position |
| Add group | `📂 Add Group` button |
| Rename group | **Click** the group header (`📂 Development`, etc.) |

---

## ⚙️ Configuration

### App List: `~/.config/solaar/app-launcher-apps.conf`

```ini
[Development]
VS Code|code|visual-studio-code
Obsidian|obsidian|obsidian

[System]
Terminal|gnome-terminal|utilities-terminal
Calculator|gnome-calculator|org.gnome.Calculator

[Communication]
Zoom|zoom|Zoom
Firefox|firefox|firefox
```

**Format:** `DisplayName|Command|IconName`

| Field | Description | Example |
|-------|-------------|---------|
| DisplayName | Name shown in launcher | `VS Code` |
| Command | Shell command to execute | `code`, `gnome-terminal` |
| IconName | GTK icon theme name or absolute path | `visual-studio-code` |

> [!TIP]
> You can find icon names from `.desktop` files:
>
> ```bash
> grep -r "^Icon=" /usr/share/applications/code.desktop
> ```

---

## 📁 Project Structure

```
solaar-app-launcher/
├── README.md                  # This document (English)
├── README_KO.md               # Korean documentation
├── install.sh                 # Install script
├── LICENSE                    # MIT License
├── src/
│   ├── solaar-app-launcher.py # Main GTK3 application
│   └── solaar-app-launcher.sh # Shell wrapper script
└── config/
    ├── app-launcher-apps.conf.example  # App list example
    └── rules.yaml.example              # Solaar rules example
```

---

## 🔧 Bonus: Additional Gesture Actions

You can add directional gestures to the Gesture Button:

| Gesture | Action | rules.yaml |
|---------|--------|------------|
| Click (no movement) | App Launcher | `MouseGesture: []` → `Execute` |
| ↑ Up | Maximize window | `MouseGesture: [Mouse Up]` → `KeyPress: [Super_L, Up]` |
| ↓ Down | Minimize window | `MouseGesture: [Mouse Down]` → `KeyPress: [Super_L, Down]` |
| ← Left | Browser back | `MouseGesture: [Mouse Left]` → `KeyPress: XF86_Back` |
| → Right | Browser forward | `MouseGesture: [Mouse Right]` → `KeyPress: XF86_Forward` |

See [`config/rules.yaml.example`](config/rules.yaml.example) for the full example.

---

## 🤝 Contributing

1. **Fork** this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a **Pull Request**

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
