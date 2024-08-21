### What is it:
It does sync your defined folder constantly searching for an optimized video format which is like better for web browsers...
You can run the script at startup or even schedule it with crontab and customize it how you like ...

### How to use it:
- Linux Install:
  - Install Python
  - This app requires `ffmpeg`, `jq`
    ```shell
    # Install Python...
    # and
    
    sudo apt update
    
    sudo apt install -y ffmpeg
    ffmpeg -version
    # Output
    # ffmpeg version 6.1.1-3ubuntu5 Copyright (c) 2000-2023 the FFmpeg developers
    # built with gcc 13 (Ubuntu 13.2.0-23ubuntu3)
    
    sudo apt install -y jq
    jq --version
    # Output
    # jq-1.7
    ```
- Windows Install: ( Right now under construction )
  - Install Python
  - This app requires `ffmpeg`
    ```shell
    # Coming soon
    ```
- Download `main.py`
- Open `main.py` and edit stuff like the paths and converter settings etc
- Run it with `python '/Path/To/main.py' --root '/Path/To/Video/Folder/' --interval 5'`

### Development:
- python 3.12
- no external modules
- please don't ask for fixing bugs and please don't send pull requests, this repo is just a container

### API:
- Root Arg: `-r <Path>`, `--root <Path>` (Required)
  - Uses the defined Path as root directory of your sync folder, all videos inside this root folder getting converted, except for the videos in folder `'/Path/To/Root/Folder/Ignore File Convert/'`
- interval Arg: `-i <Seconds>`, `--interval <Seconds>` (Optional)
  - Iterates scanning for changed in the used root directory every x seconds, default is 3 seconds and if set to `-1` or any negative value it does run the converter just 1 time and ends the app after this, otherwise if set to `0` it will run without any delay ( not recommended )