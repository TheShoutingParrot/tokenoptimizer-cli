"""API client for The Token Company."""

import requests
from dataclasses import dataclass

API_URL = "https://api.thetokencompany.com/v1/compress"
DEFAULT_MODEL = "bear-1"
DEFAULT_TIMEOUT = 60


@dataclass
class CompressionResult:
    """Result of a compression operation."""
    output: str
    output_tokens: int
    original_input_tokens: int
    compression_time: float

    @property
    def tokens_saved(self) -> int:
        """Number of tokens saved by compression."""
        return self.original_input_tokens - self.output_tokens

    @property
    def compression_ratio(self) -> float:
        """Compression ratio as a percentage (0-100)."""
        if self.original_input_tokens == 0:
            return 0.0
        return (1 - self.output_tokens / self.original_input_tokens) * 100


class TokenOptimizerError(Exception):
    """Base exception for Token Optimizer errors."""
    pass


class AuthenticationError(TokenOptimizerError):
    """Raised when authentication fails."""
    pass


class APIError(TokenOptimizerError):
    """Raised when the API returns an error."""
    pass


class TokenOptimizerClient:
    """Client for The Token Company API."""

    def __init__(self, api_key: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize the client.

        Args:
            api_key: Your API key for The Token Company
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout

    def compress(
        self,
        text: str,
        aggressiveness: float = 0.5,
        max_output_tokens: int | None = None,
        min_output_tokens: int | None = None,
        model: str = DEFAULT_MODEL,
    ) -> CompressionResult:
        """
        Compress text using The Token Company API.

        Args:
            text: The text to compress
            aggressiveness: Compression intensity (0.0-1.0)
            max_output_tokens: Maximum output token count
            min_output_tokens: Minimum output token count
            model: Model to use (default: bear-1)

        Returns:
            CompressionResult with compressed output and statistics

        Raises:
            AuthenticationError: If API key is invalid
            APIError: If the API returns an error
        """
        if not 0.0 <= aggressiveness <= 1.0:
            raise ValueError("Aggressiveness must be between 0.0 and 1.0")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": model,
            "input": text,
            "compression_settings": {
                "aggressiveness": aggressiveness,
                "max_output_tokens": max_output_tokens,
                "min_output_tokens": min_output_tokens,
            },
        }

        try:
            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            raise APIError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise APIError("Failed to connect to API")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}")

        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")

        if response.status_code == 403:
            raise AuthenticationError("API key does not have access to this resource")

        if not response.ok:
            try:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", response.text)
            except Exception:
                error_msg = response.text
            raise APIError(f"API error ({response.status_code}): {error_msg}")

        try:
            data = response.json()
        except Exception:
            raise APIError("Invalid JSON response from API")

        return CompressionResult(
            output=data["output"],
            output_tokens=data["output_tokens"],
            original_input_tokens=data["original_input_tokens"],
            compression_time=data["compression_time"],
        )
