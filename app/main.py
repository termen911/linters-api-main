import logging

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from app.checker.models.dto import RunLintersRequest, RunLintersResponse
from app.checker.use_case import CheckerUseCase

logging.basicConfig(level=logging.INFO, encoding="utf-8")

load_dotenv()
app = FastAPI()

checker_use_case = CheckerUseCase()


@app.get("/")
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.post("/run-linters-parsed")
async def run_linters_parsed(request: RunLintersRequest) -> RunLintersResponse:
    for file_ in request.files:
        file_.content = file_.content.replace("\\n", "\n")

    return await checker_use_case.run_linters(request)


@app.post("/run-linters")
async def run_linters_raw(request: Request) -> RunLintersResponse:
    request_body = await request.body()
    print(f"request_body: {request_body}")
    return await run_linters_parsed(RunLintersRequest.parse_raw(request_body))
