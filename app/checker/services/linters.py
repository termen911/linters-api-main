import os
import subprocess
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field

from flake8.main.application import json, Application
from pydantic import ValidationError

from app.checker.models.dto import LinterError
from app.checker.services.files import TempDir


class ILinterService(ABC):
    @abstractmethod
    def lint(self, temp_dir: TempDir) -> Iterable[LinterError]:
        ...


@dataclass
class Flake8Linter(ILinterService):
    result_file: str = field(default="flake8.txt")

    def lint(self, temp_dir: TempDir) -> Iterable[LinterError]:
        errors_list: list[str] = []

        with subprocess.Popen(
            [
                "flake8",
                temp_dir.base_dir,
                "--format",
                "json",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as process:
            output, error = process.communicate()
            output = output.decode().strip()
            error = error.decode().strip()

        if output:
            errors_list.extend(output.split("\n"))
        if error:
            errors_list.extend(error.split("\n"))

        for line in errors_list:
            data = json.loads(line)
            print(f"Data: {data}")

            for errors in data.values():
                print(f"Errors: {errors}")
                for error in errors:
                    print(f"Error: {error}")
                    linter_error = LinterError.parse_obj(error)

                    linter_error.filename = linter_error.filename.replace(
                        temp_dir.base_dir + os.sep, ""
                    ).replace(os.sep, "/")

                    yield linter_error
