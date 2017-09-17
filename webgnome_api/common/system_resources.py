"""
    Some common functionality that is dependent upon the computers
    operating environment.
"""
import os
import platform
import ctypes
import shutil


def get_free_space(path):
    if platform.system() == 'Windows':
        fb = ctypes.c_ulonglong(0)
        (ctypes.windll.kernel32
         .GetDiskFreeSpaceExW(ctypes.c_wchar_p(path),
                              None, None,
                              ctypes.pointer(fb)))
        free_bytes = fb.value
    else:
        stat_vfs = os.statvfs(path)
        free_bytes = stat_vfs.f_bavail * stat_vfs.f_frsize

    return free_bytes


def get_size_of_open_file(fd):
    curr_position = fd.tell()

    # check the size of our incoming file
    fd.seek(0, 2)
    size = fd.tell()

    # Set file to original position so we don't produce any side effects.
    fd.seek(curr_position, 0)

    return size


def write_to_file(fd, out_path):
    curr_position = fd.tell()

    fd.seek(0)
    with open(out_path, 'wb') as output_file:
        shutil.copyfileobj(fd, output_file)

    # Set file to original position so we don't produce any side effects.
    fd.seek(curr_position)
