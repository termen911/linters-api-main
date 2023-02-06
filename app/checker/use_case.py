from dataclasses import dataclass, field

from app.checker.models.dto import (
    GPTComment,
    LinterError,
    Linters,
    RunLintersRequest,
    RunLintersResponse,
)
from app.checker.services.files import FileService, IFileService
from app.checker.services.gpt import GPTService, IGPTService
from app.checker.services.linters import Flake8Linter, ILinterService


@dataclass
class CheckerUseCase:
    files_service: IFileService = field(default_factory=FileService)
    gpt_service: IGPTService = field(default_factory=GPTService)

    linters_mappping: dict[Linters, ILinterService] = field(
        default_factory=lambda: {
            Linters.FLAKE8: Flake8Linter(),
        }
    )

    async def run_linters(self, request: RunLintersRequest) -> RunLintersResponse:
        response = RunLintersResponse(errors=[], gpt_comments=[])

        temp_dir = self.files_service.create_files(*request.files)

        for file in request.files:
            comment = await self.gpt_service.generate_code_report(file.content)
            response.gpt_comments.append(GPTComment(path=file.path, comment=comment))

        for linter_type in request.linters:
            linter = self.linters_mappping[linter_type]
            response.errors.extend(linter.lint(temp_dir))

        return response
