"""
Author : Sabbir Ahmed <mail[at]thesabbir.com>

* This module scans specific file type (video) in given paths
* Gets their metadata (Guessit)
* Returns or Insert them into MongoDB
"""

import os
import fnmatch
import time
import urllib
import guessit
import json
from pymongo import MongoClient

config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')

config_file = open(config_file_path)
config = json.load(config_file)
print config['movieDirs']
"""
Configurations
TODO: Get Options from database inputs
"""

VIDEO_EXTS = ['3g2', '3gp', 'avi', 'divx', 'flv', 'm4v', 'mkv',
              'mov', 'mp4', 'mp4a', 'mpeg', 'mpg', 'webm', 'wmv']

PATHS = config['movieDirs']

TYPES = VIDEO_EXTS

# MONGODB
client = MongoClient()
movies_collection = client[config['db']][config['collection']]
movies_collection.drop()
# temp


def find_files(paths, file_types):
    for path in paths:
        for root, dirs, files in os.walk(path):
            for extension in file_types:
                for filename in fnmatch.filter(files, '*.' + extension):
                    movie = get_movies(filename, root, path)
                    movies_collection.insert(movie)


"""
Get the movies
"""


def get_movies(filename, root, path):
    file_path = os.path.join(root, filename)
    # Get some info using guess it
    meta = guessit.guess_movie_info(filename, info=['filename'])
    # Get stat info of the file
    stat = os.stat(file_path)
    data = {
        "title": meta.get('title', 'Unknown'),
        "filename": filename,
        "year": meta.get('year', 'Unknown'),
        "videoCodec": meta.get('videoCodec', 'Unknown'),
        "format": meta.get('format', 'Unknown'),
        "srt_url": get_srt(file_path, path, filename),
        "container": meta.get('container', 'Unknown'),
        "screenSize": meta.get('screenSize', 'Unknown'),
        "size": stat.st_size / 1048576,
        "addedOn": time.ctime(stat.st_mtime),
        "url": urllib.quote(file_path.replace(path, ''))
    }
    return data


# Get the subtitle if available
# TODO: Regexp to find extension

def get_srt(file_path, remove_path, filename):
    ext = os.path.splitext(file_path)[1]
    srt = file_path.replace(ext, '.srt')
    if os.path.exists(srt):
        return urllib.quote(srt.replace(remove_path, ''))
    else:
        return "http://subscene.com/subtitles/title?q=" + filename


find_files(PATHS, TYPES)
