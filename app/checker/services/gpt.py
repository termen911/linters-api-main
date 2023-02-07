import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import getenv
from textwrap import dedent

import openai
from asyncer import asyncify
from openai.error import APIError, ServiceUnavailableError, RateLimitError

logger = logging.getLogger(__name__)


class IGPTService(ABC):
    @abstractmethod
    async def generate_code_report(self, code: str) -> str:
        ...


@dataclass
class GPTService(IGPTService):
    def __post_init__(self):
        openai.api_key = getenv("OPENAI_API_KEY")

    @asyncify
    def generate_code_report(
        self,
        code: str,
    ) -> str:
        prompt = self._generate_prompt(code)

        number_of_retries = 0

        while True:
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=2500,
                    temperature=0.555,
                )
                break
            except ServiceUnavailableError:
                logger.exception("OpenAI service is unavailable")
                return "OpenAI service is unavailable..."
            except RateLimitError as e:
                if number_of_retries <= 3:
                    logger.info("OpenAI rate limit exceeded, retrying...")
                    number_of_retries += 1
                else:
                    raise e
            except APIError:
                logger.exception("OpenAI API error")
                return "OpenAI API error..."

        logger.info("OpenAI response: %s", response)
        return response["choices"][0]["text"]  # type: ignore

    def _generate_prompt(self, code: str) -> str:
        return dedent(
            f"""
            Оцени код по следующим пунктам и опиши их подробно:
            1. Корректность и понятность названных переменных и функций (оценивай только названия, если есть непонятные то по пунктам напиши как переименовать каждую)
            2. Какие ошибки совершены при написание кода (если есть перечисли все ошибки по пунктам и как их исправить)
            3. Читаемость и понятность структуры кода (по пунктам опиши как можно улучшить)
            4. Напиши рекомендации на будущее.
            5. Напиши итоговый код который будет исправлен и улучшен с комментариями.

            Код для анализа в << >>:
            <<
            {code}
            >>
            """
        )
