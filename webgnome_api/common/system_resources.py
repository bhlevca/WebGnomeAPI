"""
    Some common functionality that is dependent upon the computers
    operating environment.
"""
import os
import stat
import platform
import ctypes
import shutil
import errno


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
    if isinstance(file_in, str):
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


def write_bufread_to_file(bf, out_path):
    with open(out_path, 'wb') as output_file:
        output_file.writelines(bf.readlines())


def mkdir(base_path, dir_name, mode=0o775):
    '''
        Create a directory of a specified name inside the specified base path.
        We don't allow multiple level directory creation here.
    '''
    full_path = os.path.join(base_path, os.path.basename(dir_name))

    try:
        os.mkdir(full_path, mode)
    except OSError as e:
        if e.errno != errno.EEXIST:
            print(e)
            raise


def rename_or_move(old_name, new_name):
    '''
        Rename a file or, failing that, move it into a destination directory
    '''
    try:
        os.rename(old_name, new_name)
    except OSError as e:
        if e.errno == errno.EISDIR:
            shutil.move(old_name, new_name)
        else:
            raise


def remove_file_or_dir(file_name):
    '''
        Rename a file or, failing that, move it into a destination directory
    '''
    try:
        os.remove(file_name)
    except OSError as e:
        if e.errno == errno.ENOENT:
            # We are fine, the file didn't exist.
            return
        else:
            os.rmdir(file_name)


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

        files.append(file_info(folder, f))

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

    return {'name': f,
            'size': size,
            'type': file_type}
