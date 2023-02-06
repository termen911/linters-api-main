from enum import StrEnum, auto

from pydantic import BaseModel


class Linters(StrEnum):
    FLAKE8 = auto()


class File(BaseModel):
    path: str
    content: str

    @property
    def directory(self) -> str:
        return "/".join(self.path.split("/")[:-1])

    @property
    def filename(self) -> str:
        return self.path.split("/")[-1]


class LinterError(BaseModel):
    code: str
    filename: str
    line_number: int
    column_number: int
    text: str
    physical_line: str

    linter: Linters = Linters.FLAKE8


class GPTComment(BaseModel):
    path: str
    comment: str


class RunLintersRequest(BaseModel):
    linters: list[Linters]

    files: list[File]


class RunLintersResponse(BaseModel):
    errors: list[LinterError]
    gpt_comments: list[GPTComment]
