import shutil
import os
import sys
import subprocess
import uuid
import requests
from collections import defaultdict
from getpass import getuser


HOME = os.path.expanduser("~")
DISTRO = subprocess.check_output(["lsb_release", "-is"]).decode('ascii').strip()
TO_COPY = [
    (f"{sys.path[0]}/home/.", f"{HOME}"),
]
PROGRAMS = [
    "wmctrl",
    "vim",
    "exa",
    "fzf",
    "ncdu",
    "neofetch",
    "python2",
    "unzip",
    "zsh", 
    "zsh-syntax-highlighting", 
    "zsh-autosuggestions",
]

CODE_EXTENSIONS = [
    "austin.code-gnu-global", 
    "DavidAnson.vscode-markdownlint", 
    "esbenp.prettier-vscode", 
    "formulahendry.code-runner", 
    "haskell.haskell", 
    "hoovercj.haskell-linter", 
    "justusadam.language-haskell", 
    "lunaryorn.hlint", 
    "mads-hartmann.bash-ide-vscode", 
    "ms-python.python", 
    "ms-toolsai.jupyter", 
    "ms-vscode.cpptools", 
    "naco-siren.gradle-language", 
    "pejmannikram.vscode-auto-scroll", 
    "redhat.java", 
    "richardwillis.vscode-gradle", 
    "richardwillis.vscode-gradle-extension-pack", 
    "VisualStudioExptTeam.vscodeintellicode", 
    "vsciot-vscode.vscode-arduino", 
    "vscjava.vscode-java-debug", 
    "vscjava.vscode-java-dependency", 
    "vscjava.vscode-java-pack", 
    "vscjava.vscode-java-test", 
    "vscjava.vscode-maven",
]

def init():
    updaters = {
        "ManjaroLinux" : "sudo pacman -Syu --noconfirm",
        "KaliLinux" : "sudo apt-get update && sudo apt-get upgrade -y"
    }
    subprocess.run(f"git submodule update --init --recursive".split(" "))
    if DISTRO in updaters:
        subprocess.run(f"{updaters[DISTRO]}".split(" "))


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
    lines = [line.strip() for line in open(f"{HOME}/.config/plasma-org.kde.plasma.desktop-appletsrc")]

    locationsList = ["plugin=org.kde.panel","plugin=org.kde.plasma.private.systemtray"]
    lineNum = 0
    for i, line in enumerate(lines):
        if line in locationsList:
            lineNum = i
            while not lines[lineNum].startswith("["):
                lineNum -= 1
            data = " --group ".join(lines[lineNum][1:-1].split("]["))
            subprocess.run(f"kwriteconfig5 --file plasma-org.kde.plasma.desktop-appletsrc --group {data} --key formfactor 3".split())
            subprocess.run(f"kwriteconfig5 --file plasma-org.kde.plasma.desktop-appletsrc --group {data} --key location 5".split())
            
            locationsList.remove(line)
            if not locationsList:
                break

    ## Pinned
    lineNum = 0
    for i, line in enumerate(lines):
        if line.startswith("launchers="):
            lineNum = i
            break
    while not lines[lineNum].startswith("["):
        lineNum -= 1
    data = " --group ".join(lines[lineNum][1:-1].split("]["))
    
    subprocess.run(f"kwriteconfig5 --file plasma-org.kde.plasma.desktop-appletsrc --group {data} --key launchers applications:google-chrome.desktop,applications:visual-studio-code.desktop,applications:org.kde.dolphin.desktop".split(" "))

    ## To Remove
    removeID = []
    removeList = ["plugin=org.kde.plasma.pager", "plugin=org.kde.plasma.showdesktop","plugin=org.kde.plasma.trash"]

    for i, line in enumerate(lines):
        if line in removeList:
            lineNum = i

            while not lines[lineNum].startswith("["):
                lineNum -= 1
            removeID.append(lines[lineNum][1:-1].split("][")[-1])
            removeList.remove(line)
            if not removeList:
                break

    for i, line in enumerate(lines):
        if line.startswith("AppletOrder="):
            appletOrder = line.split("=")[1]
            lineNum = i
            break

    while not lines[lineNum].startswith("["):
        lineNum -= 1
    
    groups = lines[lineNum][1:-1].split("][")
    for ID in removeID:
        appletOrder = appletOrder.replace(ID, "")
        appletOrder = appletOrder.replace(";;", ";")
        subprocess.run(f"kwriteconfig5 --file plasma-org.kde.plasma.desktop-appletsrc --group {' --group '.join(groups[:2])} --group Applets --group {ID} --key immutability --delete".split())
        subprocess.run(f"kwriteconfig5 --file plasma-org.kde.plasma.desktop-appletsrc --group {' --group '.join(groups[:2])} --group Applets --group {ID} --key plugin --delete".split())

    subprocess.run(f"kwriteconfig5 --file plasma-org.kde.plasma.desktop-appletsrc --group {' --group '.join(groups)} --key AppletOrder {appletOrder}".split())

    #Look and Feel
    subprocess.run(f"lookandfeeltool -a org.kde.breezedark.desktop".split())


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
    subprocess.run("git clone https://aur.archlinux.org/pikaur.git".split(" "), cwd=sys.path[0])
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
    def installCascadia():
        url = requests.get("https://github.com/microsoft/cascadia-code/releases/latest").url
        for line in requests.get(url).text.split("\n"):
            if "/microsoft/cascadia-code/releases/download/" in line:
                line = line.split("\"")[1]
                os.makedirs(f"{sys.path[0]}/cascadia", exist_ok=True)
                subprocess.run(f"curl -o {sys.path[0]}/cascadia/cascadia.zip -L https://github.com/{line}".split())
                break
        subprocess.run(f"unzip -o cascadia.zip".split(), cwd=f"{sys.path[0]}/cascadia")
        os.makedirs(f"{HOME}/.local/share/fonts/Cascadia", exist_ok=True)
        for root, dirs, files in os.walk(f"{sys.path[0]}/cascadia"):
            for file in files:
                if file.endswith(".ttf"):
                    subprocess.run(f"cp -fv {root}/{file} {HOME}/.local/share/fonts/Cascadia/{file}".split())
        subprocess.run(f"fc-cache -f -v".split(), cwd=f"{sys.path[0]}")
        subprocess.run(f"rm -rf cascadia".split(), cwd=f"{sys.path[0]}")

    subprocess.run(f"sudo chsh {getuser()} -s /usr/bin/zsh".split(" "))
    subprocess.run(f"chmod +x {HOME}/.config/autostart/setvd1.desktop".split(" "))
    subprocess.run(f"rm -f {HOME}/.config/autostart/org.kde.yakuake.desktop".split(" "))

    for ext in CODE_EXTENSIONS:
        subprocess.run(f"code --install-extension {ext}".split(" "))
    
    installCascadia()
    
def copyDirs(toCopy):
    for src, dst in toCopy:
        os.makedirs(dst, exist_ok=True)
        subprocess.run(f"cp -rfv {src} {dst}".split(" "))

def main():
    init()
    runSpecifics()
    configureKDE(getWallpaper())
    installPrograms(PROGRAMS)
    copyDirs(TO_COPY)
    runCommands()

if __name__ == "__main__":
    main()