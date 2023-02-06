import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from time import time

from app.checker.models.dto import File

logger = logging.getLogger(__name__)


@dataclass
class TempDir:
    base_dir: str = field(
        default_factory=lambda: os.sep.join(["tmp", str(time())]), init=False
    )

    def join(self, *paths: str) -> str:
        return os.sep.join((self.base_dir, *paths))


class IFileService(ABC):
    @abstractmethod
    def create_files(self, *files: File) -> TempDir:
        ...


class FileService(IFileService):
    def create_files(self, *files: File) -> TempDir:
        temp_dir = TempDir()

        for file_ in files:
            os.makedirs(
                temp_dir.join(file_.directory),
                mode=777,
                exist_ok=True,
            )

            logger.info("Create file: %s", temp_dir.join(file_.path))
            with open(temp_dir.join(file_.path), "w", encoding="utf-8") as f:
                logger.info("Write content to file: %s", temp_dir.join(file_.path))
                logging.info("Content: %s", file_.content)
                f.write(file_.content)
                logger.info("Content written to file: %s", temp_dir.join(file_.path))
        return temp_dir
