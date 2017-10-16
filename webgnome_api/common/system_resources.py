"""
    Some common functionality that is dependent upon the computers
    operating environment.
"""
import os
import stat
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


def write_to_file(file_in, out_path):
    if isinstance(file_in, (str, unicode)):
        with open(file_in, 'rb') as openfile:
            write_fd_to_file(openfile, out_path)
    else:
        write_fd_to_file(file_in, out_path)


def write_fd_to_file(fd, out_path):
    curr_position = fd.tell()

    fd.seek(0)
    with open(out_path, 'wb') as output_file:
        shutil.copyfileobj(fd, output_file)

    # Set file to original position so we don't produce any side effects.
    fd.seek(curr_position)


def list_files(folder, show_hidden=False):
    '''
        List the files of a directory.
        - the up-directory '..' is always filtered out
        - Hidden files are filtered out by default, but can be optionally
          shown.
    '''
    files = []

    for f in os.listdir(folder):
        if f == '..':
            continue
        if f.startswith('.') and not show_hidden:
            continue

        size, file_type = file_info(folder, f)
        files.append({'name': f,
                      'size': size,
                      'type': file_type})

    return files


def file_info(folder, f):
    file_path = os.path.join(folder, f)
    file_stat = os.stat(file_path)
    size = file_stat.st_size
    mode = file_stat.st_mode

    if stat.S_ISDIR(mode):
        # It's a directory
        file_type = 'd'
    elif stat.S_ISREG(mode):
        # It's a file
        file_type = 'f'
    else:
        # Unknown file type
        file_type = 'u'

    return size, file_type






