import json
import os
from pathlib import Path
from sys import argv
from time import sleep

# CONFIG -> Nextcloud or basically any root folder where you store your files
# this is the default dir if -r, --root is not defined
ROOT_DIR = '/No/Valid/Path/'

# {0} -> Current File Path
# {1} -> Target File Path
VERIFY_CMD_TAGS = 'ffprobe -v quiet -of json -show_entries format_tags "{0}"'
VERIFY_CMD_CODEC = 'ffprobe -v quiet -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "{0}"'
CONVERT_CMD_MP42 = 'ffmpeg -i "{0}" -y -brand mp42 -vcodec libx264 -acodec aac -filter:v fps=60 "{1}"'

CONVERT_IGNORE_FOLDERS = ['Ignore File Convert',
                          'SofortUpload']  # In this case it's '/ROOT_DIR/.../Ignore File Convert'

# *.mkv *.webm *.flv *.vob *.ogg *.ogv *.drc *.mng *.avi *.mov *.qt *.wmv *.yuv *.rm *.rmvb *.asf *.amv *.mp4 *.m4v *.mp *.svi *.3gp *.f4v
FILE_EXTENSIONS = ['.mkv', '.webm', '.flv', '.vob', '.ogg', '.ogv', '.drc', '.mng', '.avi', '.mov', '.qt',
                   '.wmv', '.yuv', '.rm', '.rmvb', '.asf', '.amv', '.mp4', '.m4v', '.mp', '.svi', '.3gp',
                   '.f4v']
FILE_EXTENSION_WANTED = '.mp4'

ROOT_ARG_SYN = ['-r', '--root']
ONCE_ARG_SYN = ['-o', '--once']
KEEP_ARG_SYN = ['-k', '--keep']

global video_converter


def run_command(cmd):
    process = os.popen(cmd)

    output = process.read()
    process.close()

    return output.strip()


def normalize_path(path_str):
    path_str = os.path.normpath(path_str)
    path_str = os.path.normcase(path_str)
    return path_str


class VideoConverter:
    def __init__(self, keep_files):
        self.ignore_path_folders = []
        for folder in CONVERT_IGNORE_FOLDERS:
            self.ignore_path_folders.append(normalize_path('/' + folder + '/'))
        self.keep_original_files = keep_files
        self.files_mtimes = dict(file_path='', mtime=-1)

    def file_action(self, file_extension_current, file_path):
        if not os.path.isfile(file_path):
            return

        file_abs_path = str(normalize_path(file_path.absolute()))
        file_mtime = os.path.getmtime(file_path)
        if file_abs_path in self.files_mtimes:
            if self.files_mtimes[file_abs_path] == file_mtime:
                return
        self.files_mtimes[file_abs_path] = file_mtime

        for folder in self.ignore_path_folders:
            if folder in file_abs_path:
                return

        if self.video_has_nice_format(file_abs_path):
            return

        file_name_current = file_path.name
        file_name_next = file_name_current.replace(file_extension_current, FILE_EXTENSION_WANTED)
        file_parent_dir = file_path.parent.absolute()
        file_abs_path_next = os.path.join(file_parent_dir, file_name_next)

        if file_name_current == file_name_next:
            # Keep the original file is here not possible without creating a new file ... so it's not original anymore anyway
            need_convert = False
            if self.keep_original_files:
                if not self.video_has_nice_format(file_abs_path_next):
                    need_convert = True
            else:
                need_convert = True

            if need_convert:
                file_abs_path_temp = os.path.join(file_parent_dir, 'Temp1234562' + file_name_next)
                if not os.path.isfile(file_abs_path_temp):
                    os.rename(file_abs_path, file_abs_path_temp)
                convert_cmd = CONVERT_CMD_MP42.format(file_abs_path_temp, file_abs_path_next)
                run_command(convert_cmd)
                os.remove(file_abs_path_temp)
        else:
            need_convert_but_keep = False
            if self.keep_original_files:
                if os.path.isfile(file_abs_path_next):
                    if not self.video_has_nice_format(file_abs_path_next):
                        need_convert_but_keep = True
                else:
                    need_convert_but_keep = True

            if not self.keep_original_files or need_convert_but_keep:
                convert_cmd = CONVERT_CMD_MP42.format(file_abs_path, file_abs_path_next)
                run_command(convert_cmd)
                if not need_convert_but_keep:
                    os.remove(file_abs_path)


    def scan_files(self):
        def recursive_scan(dir_path):
            for path in os.scandir(dir_path):
                if path.is_dir():
                    recursive_scan(path.path)
                else:
                    path_lower = path.path.lower()
                    for extension in FILE_EXTENSIONS:
                        if path_lower.endswith(extension):
                            self.file_action(extension, Path(path.path))
                            break

        recursive_scan(ROOT_DIR)

    # Returns true if the video has the correct format
    def video_has_nice_format(self, file_abs_path):
        verify_cmd_tags = run_command(VERIFY_CMD_TAGS.format(file_abs_path))

        verify_cmd_tags_json = json.loads(verify_cmd_tags)
        try:
            video_brand = verify_cmd_tags_json['format']['tags']['major_brand']
        except KeyError:
            video_brand = ''
        try:
            video_codec = str(run_command(VERIFY_CMD_CODEC.format(file_abs_path)))
        except ValueError:
            video_codec = ''
        if video_brand.__eq__('mp42') and video_codec.__eq__('h264'):
            return True
        return False


if __name__ == '__main__':
    args = argv[1:]
    if len(args) % 2 == 1:
        print('You called an arg but miss the value .. ')
    run_once = 'false'
    keep_files = 'true'
    for argi in range(len(args)):
        # Needs to be just every periodic arg to check
        if argi % 2 == 0:
            arg_lower = args[argi].lower()
            for arg in ROOT_ARG_SYN:
                if arg_lower == arg:
                    path = args[argi + 1].replace('\'', '').replace('"', '')
                    if os.path.isdir(path):
                        ROOT_DIR = path

            for arg in ONCE_ARG_SYN:
                if arg_lower == arg:
                    run_once_ = args[argi + 1].lower()
                    if run_once_ == 'true' or run_once_ == 'false':
                        run_once = run_once_

            for arg in KEEP_ARG_SYN:
                if arg_lower == arg:
                    keep_files_ = args[argi + 1].lower()
                    if keep_files_ == 'true' or keep_files_ == 'false':
                        keep_files = keep_files_

    ROOT_DIR = normalize_path(ROOT_DIR)

    print('Using root dir ->', ROOT_DIR)
    print('Running once ->', run_once)
    print('Keep original files ->', keep_files)

    if not os.path.isdir(ROOT_DIR):
        print('No Valid Root Directory ... Please check your root path argument..., sometimes you may need to add "" or \'\' like "/Path/"')
        err = 'err'
        int(err)

    if keep_files == 'true':
        keep_files = True
    elif keep_files == 'false':
        keep_files = False
    video_converter = VideoConverter(keep_files)
    # Comment out if you don't want to convert videos on start of the app...
    video_converter.scan_files()

    if run_once == 'false':
        try:
            while True:
                video_converter.scan_files()
                sleep(5)
        except KeyboardInterrupt:
            pass
