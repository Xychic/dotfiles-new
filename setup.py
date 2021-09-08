import shutil
import os
import sys
import subprocess
import uuid
from collections import defaultdict
from getpass import getuser

DISTRO = subprocess.check_output(["lsb_release", "-is"]).decode('ascii').strip()
TO_COPY = [
    (f"{sys.path[0]}/home/.", f"{os.environ['HOME']}"),
]
PROGRAMS = [
    "wmctrl",
    "vim",
    "exa",
    "fzf",
    "ncdu",
    "neofetch",
    "python2",
    "zsh", 
    "zsh-syntax-highlighting", 
    "zsh-autosuggestions",
]

def configureKDE(wallpaper):
    # Wallpaper
    subprocess.run(f"kwriteconfig5 --file kscreenlockerrc --group Greeter --group Wallpaper --group org.kde.image --group General --key Image {wallpaper}".split(" "))

    # Lock Screen
    subprocess.run(f"kwriteconfig5 --file plasma-org.kde.plasma.desktop-appletsrc --group Containments --group 17 --group Wallpaper --group org.kde.image --group General --key Image {wallpaper}".split(" "))

    # Splash Screen
    subprocess.run(f"kwriteconfig5 --file ksplashrc --group KSplash --key Theme None".split(" "))
    subprocess.run(f"kwriteconfig5 --file ksplashrc --group KSplash --key Engine None".split(" "))

    #Virtual Desktop
    for i in range(9):
        subprocess.run(f"kwriteconfig5 --file kwinrc --group Desktops --key Id_{i+1} {uuid.uuid4()}".split(" "))
    subprocess.run(f"kwriteconfig5 --file kwinrc --group Desktops --key Number 9".split(" "))
    subprocess.run(f"kwriteconfig5 --file kwinrc --group Desktops --key Rows 3".split(" "))

    #Keyboard Shortcuts
    subprocess.run(f"kwriteconfig5 --file kglobalshortcutsrc --group kwin --key Switch\sOne\sDesktop\sDown Meta+Ctrl+Down,Meta+Ctrl+Down,Switch One Desktop Down".split(" "))
    subprocess.run(f"kwriteconfig5 --file kglobalshortcutsrc --group kwin --key Switch\sOne\sDesktop\sUp Meta+Ctrl+Up,Meta+Ctrl+Up,Switch One Desktop Up".split(" "))
    subprocess.run(f"kwriteconfig5 --file kglobalshortcutsrc --group kwin --key Switch\sOne\sDesktop\sto\sthe\sLeft Meta+Ctrl+Left,Meta+Ctrl+Left,Switch One Desktop to the Left".split(" "))
    subprocess.run(f"kwriteconfig5 --file kglobalshortcutsrc --group kwin --key Switch\sOne\sDesktop\sto\sthe\sRight Meta+Ctrl+Right,Meta+Ctrl+Right,Switch One Desktop to the Right".split(" "))
    subprocess.run(f"kwriteconfig5 --file kglobalshortcutsrc --group kwin --key next\sactivity none,none,Walk through activities".split(" "))
    subprocess.run(f"kwriteconfig5 --file kglobalshortcutsrc --group kwin --key ShowDesktopGrid Meta+Tab,Ctrl+F8,Show Desktop Grid".split(" "))

    #Task Bar
    # subprocess.run(f"kwriteconfig5 --file plasma-org.kde.plasma.desktop-appletsrc --group Containments --group 1 --key formfactor 3".split(" "))
    # subprocess.run(f"kwriteconfig5 --file plasma-org.kde.plasma.desktop-appletsrc --group Containments --group 1 --key location 5".split(" "))
    # subprocess.run(f"kwriteconfig5 --file plasma-org.kde.plasma.desktop-appletsrc --group Containments --group 8 --key formfactor 3".split(" "))
    # subprocess.run(f"kwriteconfig5 --file plasma-org.kde.plasma.desktop-appletsrc --group Containments --group 8 --key location 5".split(" "))

def getWallpaper():
    wallpapersDict = defaultdict(lambda: "wallpaper.svg")
    wallpapersDict.update({
        "ManjaroLinux" : "wallpaper-manjaro.svg",
        "KaliLinux" : "wallpaper-kali.svg"
    })

    return f"{sys.path[0]}/files/{wallpapersDict[DISTRO]}"

def installPrograms(programNames):
    installers = {
        "ManjaroLinux" : "sudo pacman -Sy --noconfirm --needed",
        "KaliLinux" : "sudo apt-get install -y"
    }

    if DISTRO not in installers:
        print("Please install the following and press enter to continue: ")
        for p in programNames:
            print(f"\t- {p}")
        input("Press enter once installed: ")
    else:
        command = f"{installers[DISTRO]} {' '.join(programNames)}"
        print(f"Running: \"{command}\"")
        subprocess.run(command.split(" "))

def archSpecifics():
    subprocess.run("sudo pacman -S --noconfirm --needed base-devel git pkgfile".split(" "))
    subprocess.run("git clone https://aur.archlinux.org/pikaur.git".split(" "), cwd=f"{sys.path[0]}")
    subprocess.run("makepkg -fsri --noconfirm".split(" "), cwd=f"{sys.path[0]}/pikaur")
    subprocess.run("pikaur -S --noconfirm --needed visual-studio-code-bin google-chrome".split(" "), cwd=f"{sys.path[0]}/pikaur")

def debianSpecifics():
    command = f"sudo apt-get install -y {' '.join(['python-is-python3'])}"
    print(f"Running: \"{command}\"")
    subprocess.run(command.split(" "))

def runSpecifics():
    specifics = {
        "ManjaroLinux" : archSpecifics,
        "KaliLinux" : debianSpecifics
    }

    if DISTRO in specifics:
        specifics[DISTRO]()

def runCommands():
    subprocess.run(f"sudo chsh {getuser()} -s /usr/bin/zsh".split(" "))
    subprocess.run(f"chmod +x {os.environ['HOME']}/.config/autostart/setvd1.desktop".split(" "))
    
def copyDirs(toCopy):
    for src, dst in toCopy:
        os.makedirs(dst, exist_ok=True)
        command = f"cp -rfv {src} {dst}"
        print(command)
        subprocess.run(command.split(" "))

def main():
    runSpecifics()
    configureKDE(getWallpaper())
    installPrograms(PROGRAMS)
    copyDirs(TO_COPY)
    runCommands()

if __name__ == "__main__":
    main()