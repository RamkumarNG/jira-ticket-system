import httpx
from typing import Optional, Dict, Any


class AsyncHTTPClient:

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url

    def _full_url(self, path: str) -> str:
        if self.base_url and not path.startswith("http"):
            return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        
        return path

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        
        url = self._full_url(path)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        
