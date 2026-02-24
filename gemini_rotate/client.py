import logging
from typing import Any
from google import genai
from google.genai.errors import ClientError, ServerError
from .utils import get_gemini_api_keys, get_gemini_models
from .exceptions import AllClientsFailed
import ast
import re

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _format_error(e: Exception) -> str:
    s = str(e)
    match = re.search(r"^(\d+)\s+([A-Z_]+)\.\s+(.*)$", s, re.DOTALL)

    if match:
        code, status, details_str = match.groups()
        try:
            details = ast.literal_eval(details_str)
            if isinstance(details, dict) and "error" in details:
                message = details["error"].get("message", "Unknown error")
                return f"{code} {status}. {message}"
        except:
            pass

    return s


class GeminiRotationClient:
    def __init__(self):
        self.api_keys = get_gemini_api_keys()
        if not self.api_keys:
            raise ValueError("No Gemini API keys found in environment variables.")

        self.clients = [genai.Client(api_key=key) for key in self.api_keys]
        self.models = get_gemini_models()

    async def generate_content(
        self,
        contents: Any,
        config: Any = None,
    ):
        """
        Generates content using rotated clients and model pairs.
        Iterates through models in pairs (Primary, Secondary).
        For each pair, iterates through all available API keys.
        """
        model_groups = [self.models[i : i + 2] for i in range(0, len(self.models), 2)]

        total_groups = len(model_groups)

        for group_idx, group in enumerate(model_groups):
            primary_model = group[0]
            secondary_model = group[1] if len(group) > 1 else None

            logger.info(
                f"Processing Model Group {group_idx + 1}/{total_groups}: Primary='{primary_model}', Secondary='{secondary_model}'"
            )

            for client_idx, client in enumerate(self.clients):
                client_id = f"Client-{client_idx + 1}"

                try:
                    logger.debug(f"[{client_id}] Attempting Primary: {primary_model}")
                    response = await client.aio.models.generate_content(
                        model=primary_model, contents=contents, config=config
                    )
                    logger.info(f"[{client_id}] Primary ({primary_model}) succeeded")
                    return response

                except (ClientError, ServerError) as e:
                    logger.warning(
                        f"[{client_id}] Primary ({primary_model}) failed: {_format_error(e)}"
                    )

                    if secondary_model:
                        try:
                            logger.debug(
                                f"[{client_id}] Attempting Secondary: {secondary_model}"
                            )
                            response = await client.aio.models.generate_content(
                                model=secondary_model, contents=contents, config=config
                            )
                            logger.info(
                                f"[{client_id}] Secondary ({secondary_model}) succeeded"
                            )
                            return response
                        except (ClientError, ServerError) as e2:
                            logger.warning(
                                f"[{client_id}] Secondary ({secondary_model}) failed: {_format_error(e2)}"
                            )

        raise AllClientsFailed(
            f"All {len(self.clients)} agents failed across all {len(self.models)} models."
        )


    def generate_content_sync(
        self,
        contents: Any,
        config: Any = None,
    ):
        """
        Generates content synchronously using rotated clients and model pairs.
        Iterates through models in pairs (Primary, Secondary).
        For each pair, iterates through all available API keys.
        """
        model_groups = [self.models[i : i + 2] for i in range(0, len(self.models), 2)]

        total_groups = len(model_groups)

        for group_idx, group in enumerate(model_groups):
            primary_model = group[0]
            secondary_model = group[1] if len(group) > 1 else None

            logger.info(
                f"Processing Model Group {group_idx + 1}/{total_groups}: Primary='{primary_model}', Secondary='{secondary_model}'"
            )

            for client_idx, client in enumerate(self.clients):
                client_id = f"Client-{client_idx + 1}"

                try:
                    logger.debug(f"[{client_id}] Attempting Primary: {primary_model}")
                    response = client.models.generate_content(
                        model=primary_model, contents=contents, config=config
                    )
                    logger.info(f"[{client_id}] Primary ({primary_model}) succeeded")
                    return response

                except (ClientError, ServerError) as e:
                    logger.warning(
                        f"[{client_id}] Primary ({primary_model}) failed: {_format_error(e)}"
                    )

                    if secondary_model:
                        try:
                            logger.debug(
                                f"[{client_id}] Attempting Secondary: {secondary_model}"
                            )
                            response = client.models.generate_content(
                                model=secondary_model, contents=contents, config=config
                            )
                            logger.info(
                                f"[{client_id}] Secondary ({secondary_model}) succeeded"
                            )
                            
                            return response
                            
                        except (ClientError, ServerError) as e2:
                            logger.warning(
                                f"[{client_id}] Secondary ({secondary_model}) failed: {_format_error(e2)}"
                            )

        raise AllClientsFailed(
            f"All {len(self.clients)} agents failed across all {len(self.models)} models."
        )
