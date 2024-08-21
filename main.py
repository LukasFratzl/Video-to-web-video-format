import platform
import os
from pathlib import Path
from sys import argv
from time import sleep


# CONFIG -> Nextcloud or basically any root folder where you store your files
# this is the default dir if -r, --root is not defined
ROOT_DIR = '/No/Valid/Path/'

# Default update interval in seconds, every x seconds the file search is starting
TICK_INTERVAL = 3

VERIFY_CMD_LINUX = """
#!/bin/bash

: "

Verifies if the file should be converted with ffprobe
returns 0 or 1

{0} -> Current File Name
{1} -> Wanted File Name
{2} -> Current File Directory
{3} -> Root Folder Directory

"

cd "{2}"
Brand=$(ffprobe -v quiet -of json -show_entries format_tags "{0}" | jq -r .format.tags.major_brand)
Codec=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "{0}")
if [[ "$Brand" == "mp42" && "$Codec" == "h264" ]]; then echo 0; else echo 1; fi
"""

VERIFY_CMD_WINDOWS = """"""

CONVERT_CMD_LINUX = """
#!/bin/bash

: "

Removes the Original File after conversation

{0} -> Current File Name
{1} -> Wanted File Name
{2} -> Current File Directory
{3} -> Root Folder Directory

"

cd "{2}"
sleep 2
if [[ "{0}" == "{1}" ]]; then
  mv "{0}" "Temp{0}"
  ffmpeg -i "Temp{0}" -y -brand mp42 -vcodec libx264 -acodec aac -filter:v fps=60 "{1}"
  rm "Temp{0}"
else
    ffmpeg -i "{0}" -y -brand mp42 -vcodec libx264 -acodec aac -filter:v fps=60 "{1}"
    rm "{0}"
fi
"""

CONVERT_CMD_WINDOWS = """"""

CONVERT_IGNORE_FOLDER = 'Ignore File Convert'  # Int his case it's '/home/flow____/Nextcloud/Ignore File Convert'

# *.mkv *.webm *.flv *.vob *.ogg *.ogv *.drc *.mng *.avi *.mov *.qt *.wmv *.yuv *.rm *.rmvb *.asf *.amv *.mp4 *.m4v *.mp *.svi *.3gp *.f4v
FILE_EXTENSIONS = ['.mkv', '.webm', '.flv', '.vob', '.ogg', '.ogv', '.drc', '.mng', '.avi', '.mov', '.qt',
                   '.wmv', '.yuv', '.rm', '.rmvb', '.asf', '.amv', '.mp4', '.m4v', '.mp', '.svi', '.3gp',
                   '.f4v']
FILE_EXTENSION_WANTED = '.mp4'

ROOT_ARG_SYN = ['-r', '--root']
TICK_ARG_SYN = ['-i', '--interval']


def run_command(cmd):
    if platform.system() == 'Windows':
        process = os.popen('bash -c \'{0}\''.format(cmd))
    else:
        process = os.popen('bash -c \'{0}\''.format(cmd))

    output = process.read()
    process.close()
    return output


class VideoConverter:
    def __init__(self):
        self.is_windows = platform.platform() == 'Windows'
        self.ignore_path = os.path.join(ROOT_DIR, CONVERT_IGNORE_FOLDER)
        self.ignore_path = os.path.normpath(self.ignore_path)
        self.ignore_path = os.path.normcase(self.ignore_path)
        if not os.path.isdir(self.ignore_path):
            os.mkdir(self.ignore_path)
        if self.is_windows:
            self.verify_cmd = VERIFY_CMD_WINDOWS
            self.convert_cmd = CONVERT_CMD_WINDOWS
        else:
            self.verify_cmd = VERIFY_CMD_LINUX
            self.convert_cmd = CONVERT_CMD_LINUX

    def file_action(self, file_extension_current, file_path):
        if not os.path.isfile(file_path):
            return

        file_abs_path = file_path.absolute()
        if self.ignore_path in str(file_abs_path):
            return

        file_name_current = file_path.name
        file_name_next = file_name_current.replace(file_extension_current, FILE_EXTENSION_WANTED)
        file_parent_dir = file_path.parent.absolute()

        verify_cmd = self.verify_cmd.format(file_name_current, file_name_next, file_parent_dir, ROOT_DIR)
        # print(verify_cmd)
        verify_result_str = run_command(verify_cmd)
        # print(verify_result_str)
        try:
            verify_result = int(verify_result_str)
        except ValueError:
            verify_result = 0
        if verify_result != 0:
            convert_cmd = self.convert_cmd.format(file_name_current, file_name_next, file_parent_dir, ROOT_DIR)
            print(convert_cmd)
            run_command(convert_cmd)

    def scan_files(self):
        some_files_match = False
        for sub_dir, dirs, files in os.walk(ROOT_DIR):
            for file in files:
                file_path = os.path.join(sub_dir, file)
                file_path = os.path.normpath(file_path)
                file_path = os.path.normcase(file_path)

                for extension in FILE_EXTENSIONS:
                    if file_path.lower().endswith(extension):
                        some_files_match = True
                        self.file_action(extension, Path(file_path))
                        break

        if not some_files_match:
            return False

        return True


if __name__ == '__main__':

    args = argv[1:]
    for argi in range(len(args)):
        # Needs to be just every periodic arg to check
        if argi % 2 == 0:
            arg_lower = args[argi].lower()
            for arg in ROOT_ARG_SYN:
                if arg_lower == args[argi]:
                    path = args[argi + 1].replace('\'', '').replace('"', '')
                    if os.path.isdir(path):
                        ROOT_DIR = path

            for arg in TICK_ARG_SYN:
                if arg_lower == args[argi]:
                    try:
                        TICK_INTERVAL = float(args[argi + 1])
                    except ValueError:
                        pass

    ROOT_DIR = os.path.normpath(ROOT_DIR)
    ROOT_DIR = os.path.normcase(ROOT_DIR)

    print('Using root dir ->', ROOT_DIR)
    print('Using Tick interval ->', TICK_INTERVAL, 'Seconds')

    if not os.path.isdir(ROOT_DIR):
        print('No Valid Root Dir ->', ROOT_DIR)

    converter = VideoConverter()
    try:
        while True:
            scan_valid = converter.scan_files()
            if TICK_INTERVAL > 0:
                sleep(TICK_INTERVAL)
            elif TICK_INTERVAL < 0:
                break
    except KeyboardInterrupt:
        pass
