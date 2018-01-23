# Author: Michael Winterspacher
# Date created: 2018-01-23
# Date last modified: 2018-01-23
# Python Version: >2.7
# Version 1.0.0

import os
import struct
from hashlib import md5
from time import time


class Cache:
    """ Light Cache

    Available functions:
        * set(name, content, expiry)
        * get(name)
        * remove(name, force)
        * clean(force)

    Usage:
        >>> cache = Cache()
        >>> cache.set('c1', b'Hello World', 600)  # expiring time of 10 minutes
        >>> print(cache.get('c1'))
        ... b'Hello World'
    """

    """ Cache Version """
    __version = 2

    def __init__(self, default_expiration=60, directory=None):
        """
        :param default_expiration: default expiration time in seconds
        :param directory: path to the cache directory
        """

        """ Cache directory """
        self.__directory = os.path.join(os.getcwd(), './cache')

        """ File Extension of the cache files """
        self.__extension = '.tmp'

        """ Expiring time """
        self.__default_expiration = default_expiration

        if directory:
            self.__directory = directory

        if not os.path.isdir(self.__directory):
            os.makedirs(self.__directory)

    def set(self, name, content, expiration=None):
        """ Creates a new cache file. If a file with the same name exists, it will be overwritten.

        :param name: identifier
        :param content: byte content
        :param expiration: expiration time in seconds
        :return: file path of cache file
        """

        if not expiration and expiration != 0:
            expiration = self.__default_expiration

        file = self.get_filename(name)

        return self.__write(file, content, version=self.__version, expiration=expiration)

    def get(self, name):
        """ Returns the content of the cache file. If the cache file is expired then returns false and deletes the file.

        :param name: identifier
        :return: byte content or false if not found or invalid
        """

        file = self.get_filename(name)

        cache = self.__valid(file)
        if not cache:
            self.__remove(file)
            return False

        return cache['content']

    def remove(self, name, force=True):
        """ Deletes the cache file immediately.

        :param name: identifier
        :param force: ignores the expiry time
        :return: True|False
        """

        file = self.get_filename(name)

        if force:
            return self.__remove(file)

        cache = self.__valid(file)
        if not cache:
            return self.__remove(file)

        return False

    def clear(self, force=False):
        """ Deletes all expired cache files! With force true, all cache files will be deleted!

        :param force: ignores the expiry time
        :return: count of deleted files
        """

        count = 0
        for f in os.listdir(self.__directory):
            f = os.path.join(self.__directory, f)

            if force:
                if self.__remove(f):
                    count += 1
            else:
                cache = self.__valid(f)
                if not cache:
                    if self.__remove(f):
                        count += 1

        return count

    def get_filename(self, name):
        """ Returns the path of the cache file according to the name

        :param name: identifier
        :return: path
        """

        return os.path.join(self.__directory, md5(str(name).encode('utf-8')).hexdigest() + self.__extension)

    def __valid(self, file):
        """ Checks whether the file is valid. If valid then returns the cache object

        :param file: file path
        :return: cache object
        """

        cache = self.__read(file)

        if not cache:
            return None

        if cache['expire'] <= 0 \
                or cache['version'] != self.__version \
                or int(time() - cache['creation_time']) > cache['expire']:
            return False

        return cache

    def __remove(self, file):
        """ Deletes the valid cache file

        :param file: file path
        :return:
        """

        if self.__exist(file):
            try:
                os.remove(file)
            except (IOError, OSError,):
                raise CacheError("cache file is'nt deletable!")
            return True
        else:
            return False

    def __exist(self, file):
        """ Checks whether the cache file is existing. Ignores the expiring time

        :param file: file path
        :return:
        """

        if self.__read(file):
            return True
        else:
            return False

    def __write(self, file, content, version, expiration):
        """ Creates a new cache file. Existing file will be overwritten

        :param file: file path
        :param content: byte content
        :param version: cache version
        :param expiration: expiration time in seconds
        :return: file path of cache file
        """

        try:
            with open(file, 'w+b') as f:
                header = struct.pack(
                    'bdd',
                    version,
                    expiration,
                    int(time())
                )
                f.write(header)
                f.write(content)
        except (IOError, OSError,):
            raise CacheError("cache file is'nt writeable!")

        return file

    def __read(self, file):
        """ Reads a cache file

        :param file: file path
        :return:
        """

        if not os.path.isfile(file):
            return False

        try:
            with open(file, 'r+b') as f:
                try:
                    header = struct.unpack('bdd', f.read(8*3))
                except struct.error:
                    return False
                content = f.read()
        except IOError:
            raise CacheError("cache file is'nt readable!")

        version = header[0]
        expiration = header[1]
        creation_time = header[2]

        return {
            "version": int(version),
            "expire": int(expiration),
            "creation_time": int(creation_time),
            "content": content
        }


class CacheError(Exception):
    pass
