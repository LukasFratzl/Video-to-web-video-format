#!/bin/bash

# https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

python3  '/home/flow/Documents/Video-to-web-video-format/video-converter.py' --root $SCRIPT_DIR --bitrate 8000000 --once true --keep false
