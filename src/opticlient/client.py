from __future__ import annotations

from typing import Optional

from .config import _get_default_api_token, _get_default_base_url
from .http import HttpClient
from .tools import SingleMachineSchedulingClient

class OptiClient:
    """
    Main entry point for interacting with the Opti API.
    """

    def __init__(
        self,
        api_token: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        if api_token is None:
            api_token = _get_default_api_token()
        if base_url is None:
            base_url = _get_default_base_url()
        
        if api_token is None:
            raise ValueError(
                "API token is required. Set OPTICLIENT_API_TOKEN env var "
                "or pass api_token=... to OptiClient()."
            )

        self.api_token = api_token
        self.base_url = base_url
        self._http = HttpClient(
            base_url=self.base_url,
            api_token=self.api_token,
            timeout=timeout,
        )

        self.sms: SingleMachineSchedulingClient = SingleMachineSchedulingClient(self._http)

    def __close(self) -> None:
        self._http._close()

    def __enter__(self) -> "OptiClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.__close()
