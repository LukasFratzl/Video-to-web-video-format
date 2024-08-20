import platform
import os
from pathlib import Path
from time import sleep


# CONFIG -> Nextcloud or basically any root folder where you store your files
ROOT_DIR_LINUX = '/home/flow____/Nextcloud/'
# Would be better with a config file or through the cmd interface pushing the platform paths...
ROOT_DIR_WINDOWS = ''

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


def RunCommand(cmd):
    process = os.popen('bash -c \'{0}\''.format(cmd))

    output = process.read()
    process.close()
    return output


def is_int(element: any) -> bool:
    # If you expect None to be passed:
    if element is None:
        return False
    try:
        int(element)
        return True
    except ValueError:
        return False


class VideoConverter:
    def __init__(self):
        self.is_windows = platform.platform() == 'Windows'

    def FileAction(self, file_extension_current, file_path):
        if not os.path.isfile(file_path):
            return

        path_parts = os.path.normpath(file_path).split(os.path.sep)
        for part in path_parts:
            if CONVERT_IGNORE_FOLDER == part:
                return

        file_path_resolved = Path(file_path)

        file_name_current = file_path_resolved.name
        file_name_next = file_name_current.replace(file_extension_current, FILE_EXTENSION_WANTED)

        file_parent_dir = file_path_resolved.parent.absolute()

        if self.is_windows:
            verify_cmd = VERIFY_CMD_WINDOWS.format(file_name_current, file_name_next, file_parent_dir, ROOT_DIR_WINDOWS)
        else:
            verify_cmd = VERIFY_CMD_LINUX.format(file_name_current, file_name_next, file_parent_dir, ROOT_DIR_LINUX)
        # print(verify_cmd)
        verify_result_str = RunCommand(verify_cmd)
        # print(verify_result_str)
        if is_int(verify_result_str):
            verify_result = int(verify_result_str)
            if verify_result != 0:
                if self.is_windows:
                    convert_cmd = CONVERT_CMD_WINDOWS.format(file_name_current, file_name_next, file_parent_dir, ROOT_DIR_WINDOWS)
                else:
                    convert_cmd = CONVERT_CMD_LINUX.format(file_name_current, file_name_next, file_parent_dir, ROOT_DIR_LINUX)
                # print(convert_cmd)
                convert_result_str = RunCommand(convert_cmd)


    def ScanFiles(self):
        if self.is_windows:
            root_dir = ROOT_DIR_WINDOWS
        else:
            root_dir = ROOT_DIR_LINUX

        if not os.path.isdir(root_dir):
            print('No Valid Root Dir ->', root_dir)
            return False

        some_files_match = False
        for sub_dir, dirs, files in os.walk(root_dir):
            for file in files:
                file_path = sub_dir + os.sep + file

                for extension in FILE_EXTENSIONS:
                    if file_path.endswith(extension):
                        some_files_match = True
                        self.FileAction(extension, file_path)
                        break

        if not some_files_match:
            return False

        return True


if __name__ == '__main__':
    CONVERT_IGNORE_FOLDER = CONVERT_IGNORE_FOLDER.replace(os.path.sep, '')
    converter = VideoConverter()
    if converter.is_windows:
        ignore_path = os.path.join(ROOT_DIR_WINDOWS, CONVERT_IGNORE_FOLDER)
    else:
        ignore_path = os.path.join(ROOT_DIR_LINUX, CONVERT_IGNORE_FOLDER)
    if not os.path.isdir(ignore_path):
        os.mkdir(ignore_path)
    try:
        while True:
            scan_valid = converter.ScanFiles()
            sleep(3)
    except KeyboardInterrupt:
        pass
