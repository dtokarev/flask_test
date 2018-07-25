import os


def get_disk_usage_perc():
    st = os.statvfs('/')
    return round((st.f_blocks - st.f_bfree) / st.f_blocks * 100, 2)


def get_file_info(path, base_folder):
    """
    {
        'extension': 'avi',
        'file': 'some_movie_DVDRip.avi',
        'folder': '/d/19/19921/season 1',
        'mime': 'video/x-msvideo',
        'parent': 'season 1',
        'path': '/d/19/19921/season 1/some_movie_DVDRip.avi'
    }
    :param path:
    :param base_folder:
    :return:
    """
    from mimetypes import MimeTypes
    mime = MimeTypes()
    info = {}
    info.update({'path': path})
    info.update({'folder': os.path.join(*os.path.split(path)[0:-1])})
    info.update({'file': os.path.split(path)[-1]})

    mime = mime.guess_type(path)
    info.update({'mime': mime[0] if mime and len(mime) > 0 else 'unknown'})

    extension = path.split('.')
    info.update({'extension': extension[-1].lower() if extension and len(extension) > 0 else 'unknown'})

    _ = path.lstrip(base_folder).split('/')
    info.update({'parent': _[0].lower() if _ and len(_) > 1 else ''})

    return info


def get_file_info_recursive(folder):
    files_dict = []
    for _dir, _, _files in os.walk(folder):
        for _file in _files:
            path = os.path.join(_dir, _file)
            files_dict.append(get_file_info(path, folder))

    return files_dict
