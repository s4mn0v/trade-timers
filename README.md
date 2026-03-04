> [!TIP]
> # Example Image Of Local App
> <img width="969" height="206" alt="image" src="https://github.com/user-attachments/assets/d273a7c5-1f57-4584-a2ef-ffa473d6cec1" />

> [!TIP]
> # Example Image Of Online App
> ![example](https://github.com/user-attachments/assets/ea3a4156-b1da-41fc-ab64-ed798b16601c)

---

# Timeframe Sync

Is a lightweight, floating desktop widget designed for traders and financial analysts who need to track multiple timeframe countdowns and global trading sessions simultaneously.

It provides:

- Real-time candle close countdowns (1M → 1D)
- Visual progress bars for each timeframe
- Double-click to arm a specific timeframe
- Sound alert when the selected timeframe closes
- On-screen alert indicator showing the armed timeframe
- Live trading session detection (Asia, London, New York)
- Session countdown timer
- Always-on-top floating interface
- Drag to move / Right-click drag to resize
- Automatic UI scaling when resized

---

# Create the app with pyinstaller

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

Linux

```bash
pip install pygame pyinstaller
```

```bash
pyinstaller -F timers.py \
--add-data "beep.wav:." \
--hidden-import=pygame \
--hidden-import=pygame.mixer \
--collect-all pygame
```

When done, deactivate env

```bash
deactivate
```

---

# How to Make Your Python Binary a Visible App in Linux
<details>
  <summary>Show Steps</summary>

## Step 1: Create an Applications Folder

Open a terminal and create a folder for your apps:

```bash
mkdir -p ~/Applications
```

Move your binary file into this folder:

```bash
mv /path/to/your/binary ~/Applications/
```

example path

```
/home/user/folder/TradingTimers/dist/timers
```

---

## Step 2: Create the App Launcher File

Create a `.desktop` file in the right location:

```bash
mkdir -p ~/.local/share/applications
nano ~/.local/share/applications/myapp.desktop
```

Copy and paste this template into the editor:

```bash
[Desktop Entry]
Type=Application
Name=Trading Timers
Exec=/home/YOUR_USERNAME/Applications/your-binary-name
Icon=/home/YOUR_USERNAME/Applications/icon.png
Terminal=false
Categories=Utility;
```

**Important changes you must make:**

- Replace `YOUR_USERNAME` with your actual username
- Replace `your-binary-name` with your actual file name
- Replace `My App` with whatever name you want to see in the menu
- If you don't have an icon, delete the `Icon=` line

Save and exit:

- Press `Ctrl + O` (save)
- Press `Enter` (confirm)
- Press `Ctrl + X` (exit)

---

## Step 3: Make It Work

Make the launcher file executable:

```bash
chmod +x ~/.local/share/applications/myapp.desktop
```

Refresh the application menu:

```bash
update-desktop-database ~/.local/share/applications/
```

---

## Done

Press the **Super key** (Windows key) and search for your app by the name you chose. It should appear just like any installed application.

---

### Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| App doesn't appear in menu | Run `update-desktop-database ~/.local/share/applications/` again |
| App appears but won't launch | Check that the `Exec` path in your `.desktop` file is the **full absolute path** to your binary |
| No icon | Either add a `.png` icon file to your Applications folder and set the `Icon` path, or delete the `Icon=` line entirely |

</details>
