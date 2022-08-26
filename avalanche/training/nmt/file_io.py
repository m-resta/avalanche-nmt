################################################################################
# 2022 Copyright (c) Facebook, Inc. and its affiliates.                        #
# Copyrights licensed under the MIT License.                                   #
# Copyright (c) 2022 ContinualAI.                                              #
# See the accompanying LICENSE file for terms.                                 #
#                                                                              #
# Date: 21-06-2020                                                             #
# Author(s): Michele Resta                                                     #
# E-mail: contact@continualai.org                                              #
# Website: continualai.org                                                     #
################################################################################

import logging
import os
import shutil
from typing import List, Optional, Iterable


logger = logging.getLogger(__file__)


class PathManager:
    """
    Wrapper for insulating OSS I/O (using Python builtin operations) from
    iopath's PathManager abstraction (for transparently handling various
    internal backends).
    """

    @staticmethod
    def open(
            path: str,
            mode: str = "r",
            buffering: int = -1,
            encoding: Optional[str] = None,
            errors: Optional[str] = None,
            newline: Optional[str] = None,
    ):
        return open(
            path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    @staticmethod
    def copy(src_path: str, dst_path: str, overwrite: bool = False) -> bool:
        return shutil.copyfile(src_path, dst_path)

    @staticmethod
    def get_local_path(path: str, **kwargs) -> str:
        return path

    @staticmethod
    def exists(path: str) -> bool:
        return os.path.exists(path)

    @staticmethod
    def isfile(path: str) -> bool:
        return os.path.isfile(path)

    @staticmethod
    def ls(path: str) -> List[str]:
        return os.listdir(path)

    @staticmethod
    def mkdirs(path: str) -> None:
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def rm(path: str) -> None:
        os.remove(path)

    @staticmethod
    def chmod(path: str, mode: int) -> None:
        if not PathManager.path_requires_pathmanager(path):
            os.chmod(path, mode)

    @staticmethod
    def register_handler(handler) -> None:
        if IOPathManager:
            return IOPathManager.register_handler(handler=handler)

    @staticmethod
    def copy_from_local(
            local_path: str, dst_path: str, overwrite: bool = False, **kwargs
    ) -> None:
        return shutil.copyfile(local_path, dst_path)

    @staticmethod
    def path_requires_pathmanager(path: str) -> bool:
        """Do we require PathManager to access given path?"""
        return False

    @staticmethod
    def supports_rename(path: str) -> bool:
        # PathManager doesn't yet support renames
        return True

    @staticmethod
    def rename(src: str, dst: str):
        os.rename(src, dst)


def _safe_readline(fd) -> str:
    pos = fd.tell()
    while True:
        try:
            return fd.readline()
        except UnicodeDecodeError:
            pos -= 1
            fd.seek(pos)  # search where this character begins


def find_offsets(filename: str, num_chunks: int) -> List[int]:
    """
    given a file and a number of chuncks, find the offsets in the file
    to be able to chunk around full lines.
    """
    with open(filename, "r", encoding="utf-8") as f:
        size = os.fstat(f.fileno()).st_size
        chunk_size = size // num_chunks
        offsets = [0 for _ in range(num_chunks + 1)]
        for i in range(1, num_chunks):
            f.seek(chunk_size * i)
            _safe_readline(f)
            offsets[i] = f.tell()
        offsets[-1] = size
        return offsets


class ChunkLineIterator:
    """
    Iterator to properly iterate over lines of a file chunck.
    """

    def __init__(self, fd, start_offset: int, end_offset: int):
        self._fd = fd
        self._start_offset = start_offset
        self._end_offset = end_offset

    def __iter__(self) -> Iterable[str]:
        self._fd.seek(self._start_offset)
        # next(f) breaks f.tell(), hence readline() must be used
        line = _safe_readline(self._fd)
        while line:
            pos = self._fd.tell()
            # f.tell() does not always give the byte position in the file
            # sometimes it skips to a very large number
            # it is unlikely that through a normal read we go from
            # end bytes to end + 2**32 bytes (4 GB) and this makes it unlikely
            # that the procedure breaks by the undeterministic behavior of
            # f.tell()
            if (
                    self._end_offset > 0
                    and pos > self._end_offset
                    and pos < self._end_offset + 2**32
            ):
                break
            yield line
            line = self._fd.readline()


class Chunker:
    """
    contextmanager to read a chunk of a file line by line.
    """

    def __init__(self, path: str, start_offset: int, end_offset: int):
        self.path = path
        self.start_offset = start_offset
        self.end_offset = end_offset

    def __enter__(self) -> ChunkLineIterator:
        self.fd = open(self.path, "r", encoding="utf-8")
        return ChunkLineIterator(self.fd, self.start_offset, self.end_offset)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.fd.close()
