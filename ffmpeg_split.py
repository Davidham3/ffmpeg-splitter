# -*- coding:utf-8 -*-

import subprocess
import re
import os
import shutil
import platform

def get_duration(filename):
    if platform.system() == 'Windows':
        command = ["ffprobe", "-loglevel", "quiet",
                   "-show_format", "-show_streams",
                   "-i", filename]
        output = subprocess.Popen(command,
                                  shell = True,
                                  stdout = subprocess.PIPE,
                                  stderr = subprocess.STDOUT).stdout.read().decode()
        matches = re.compile("duration=(\d+\.\d*)\r").search(output)
        if matches:
            video_length = float(matches.group(1))
        else:
            print("Can't determine video length.")
            raise SystemExit
    else:
        output = subprocess.Popen("ffmpeg -i \"" + filename + "\" 2>&1 | grep 'Duration'",
                                shell = True,
                                stdout = subprocess.PIPE
                                ).stdout.read().decode()

        matches = re.compile('Duration: (\d{2}):(\d{2}):(\d{2})\.\d+,').search(output)
        if matches:
            video_length = int(matches.group(1)) * 3600 + int(matches.group(2)) * 60 + int(matches.group(3))
        else:
            print("Can't determine video length.")
            raise SystemExit
    return video_length

def split_by_seconds(filename, split_length, vcodec="copy", acodec="copy",
                     extra="", **kwargs):

    split_length = float(split_length)

    if split_length and split_length <= 0:
        print("Split length cannot be 0")
        raise SystemExit

    video_length = get_duration(filename)

    print("Video length in seconds: " + str(video_length))

    split_count = int((video_length - 1) // split_length + 1)

    directory, file = os.path.split(filename)
    fileName, fileext = os.path.splitext(file)
    target_folder = os.path.normpath(os.path.join(directory, fileName))
    if not os.path.exists(target_folder):
        os.mkdir(target_folder)

    if split_count == 1:
        print("Video length is less then the target split length.")
        shutil.copy(filename, os.path.normpath(os.path.join(target_folder, file)))

    split_cmd = "ffmpeg -y -i \"%s\" -vcodec %s -acodec %s -avoid_negative_ts make_zero %s" % (filename, vcodec,
                                                           acodec, extra)

    try:
        filebase = os.path.normpath(os.path.join(target_folder, fileName))
    except IndexError as e:
        raise IndexError("No . in filename. Error: " + str(e))

    for n in range(split_count):
        split_start = split_length * n

        split_str = " -ss " + str(split_start) + " -t " + str(split_length + 10) + \
                    ' "' + filebase + "-" + str(n) + fileext + '"'
        print("About to run: " + split_cmd + split_str)
        output = subprocess.Popen(split_cmd + split_str,
                                  shell = True,
                                  stdout = subprocess.PIPE).stdout.read().decode()

if __name__ == '__main__':
    print()
