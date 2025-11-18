"""
Chat Service

Handles AI chat interactions with Ollama.
Provides both streaming and non-streaming chat capabilities.
"""

import httpx
import json
from typing import AsyncIterator, Union

from ..config import settings


class ChatService:
    """Service for AI chat interactions with Ollama"""

    def __init__(self):
        self.ollama_host = settings.ollama_host
        self.model_name = settings.model_name

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        stream: bool = False,
    ) -> Union[dict, AsyncIterator[str]]:
        """
        Send a chat request to Ollama AI model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Sampling temperature (0.0 to 2.0)
            stream: Whether to stream the response
            
        Returns:
            If stream=False: Dictionary with 'response' and 'model' keys
            If stream=True: AsyncIterator of response chunks
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.ollama_host}/api/chat",
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "stream": stream,
                        "options": {
                            "temperature": temperature,
                        },
                    },
                )
                response.raise_for_status()

                if stream:
                    return self._stream_response(response)
                else:
                    data = response.json()
                    ai_response = data.get("message", {}).get("content", "")
                    if not ai_response:
                        ai_response = data.get("response", "Unable to generate response.")
                    
                    return {
                        "response": ai_response,
                        "model": self.model_name,
                    }
            except httpx.HTTPError as e:
                error_msg = f"I apologize, but I'm unable to process your request at this time. Error: {str(e)}"
                if stream:
                    async def error_stream():
                        yield error_msg
                    return error_stream()
                else:
                    return {
                        "response": error_msg,
                        "model": "error",
                    }

    async def _stream_response(self, response: httpx.Response) -> AsyncIterator[str]:
        """
        Stream response chunks from Ollama.
        
        Args:
            response: The HTTP response object
            
        Yields:
            Response text chunks
        """
        async for line in response.aiter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    if content:
                        yield content
                    if chunk.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue