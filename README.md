### What is it:
It does sync your defined folder constantly searching for an optimized video format which is like better for web browsers...
You can run the script at startup or even schedule it with crontab and customize it how you like ...

### How to use it:
- Linux Install:
  - Install Python
  - This app requires `ffmpeg`
  - Open the Terminal
    ```shell
    # Install Python...
    python --version
    # Output
    # Python 3.12.4
    
    sudo apt update
    
    sudo apt install -y ffmpeg
    ffmpeg -version
    # Output
    # ffmpeg version 6.1.1-3ubuntu5 Copyright (c) 2000-2023 the FFmpeg developers
    # built with gcc 13 (Ubuntu 13.2.0-23ubuntu3)
    ```
- Windows Install:
  - Install Python
  - This app requires `ffmpeg`
  - Open PowerShell
    ```shell
    # Install Python...
    python --version
    # Output
    # Python 3.12.4
    
    # Install ffmpeg on windows the correct way so the next command gives a valid version
    ffmpeg -version
    # Output
    # ffmpeg version 7.0.2-essentials_build-www.gyan.dev Copyright (c) 2000-2024 the FFmpeg developers
    # built with gcc 13.2.0 (Rev5, Built by MSYS2 project)
    ```
- Download `main.py`
- Open `main.py` and edit stuff like the converter settings etc
- Run it with `python '/Path/To/main.py' --root '/Path/To/Video/Folder/' --keep true`

### Development:
- python 3.12
- this should be a native python script so don't add packages
- please don't ask for fixing bugs and please don't send pull requests, this repo is just a container

### API:
- Root Arg: `-r <Path>`, `--root <Path>` (Required)
  - Uses the defined Path as root directory of your sync folder, all videos inside this root folder getting converted, except for the videos in folder `'/Path/To/Root/Folder/Ignore File Convert/'`
- Run once Arg: `-o <Bool>`, `--once <Bool>` (Optional) -> default (`false`)
  - Force the app to run only once and exit after the scan of the videos is done, otherwise it keeps running and looking for future changes
- Keep original video Arg: `-k <Bool>`, `--keep <Bool>` (Optional) -> default (`true`)
  - Keeps the original video if set to `true`, if `false` it converts the video in place so there is only the optimized version left, by default it is set to `true` and keeps all original videos 
