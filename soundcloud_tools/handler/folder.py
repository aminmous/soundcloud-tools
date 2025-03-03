from datetime import datetime
from pathlib import Path
from typing import Callable

from pydantic import BaseModel, field_validator

from soundcloud_tools.handler.track import FILETYPE_MAP


class FolderHandler(BaseModel):
    folder: Path

    @field_validator("folder", mode="before")
    @classmethod
    def check_folder(cls, v) -> Path:
        if isinstance(v, str):
            v = Path(v)
        if not v.is_dir():
            raise ValueError(f"Path {v} is not a directory")
        return v

    def move_all_audio_files(self, target: Path, *filters: Callable[[Path], bool]):
        for file in self.collect_audio_files(*filters):
            file.rename(target.joinpath(file.name))

    def collect_audio_files(self, *filters: Callable[[Path], bool], use_default: bool = True) -> list[Path]:
        if use_default:
            filters += (lambda f: f.suffix in FILETYPE_MAP,)
        return [file for file in self.folder.glob("*.*") if all(f(file) for f in filters)]

    @property
    def has_audio_files(self) -> bool:
        return self.folder.is_dir() and any(self.collect_audio_files())

    @staticmethod
    def last_modified(path: Path) -> datetime:
        return datetime.fromtimestamp(path.lstat().st_atime)
