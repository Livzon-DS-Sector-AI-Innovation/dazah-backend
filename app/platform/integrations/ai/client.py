"""AI client for vision model integration."""
import os
import json
import base64
from typing import List, Dict, Any
import httpx


class AIService:
    """AI service for calling vision models."""
    
    def __init__(self, api_key: str, base_url: str, model: str, timeout: int = 180):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
    
    async def chat_vision(self, prompt: str, images: List[str]) -> str:
        """
        Call vision model with text prompt and images.
        
        Args:
            prompt: Text prompt for the model
            images: List of base64 encoded images (data:image/jpeg;base64,...)
        
        Returns:
            Model response as string
        """
        # Build message content
        content = [{"type": "text", "text": prompt}]
        
        # Add images
        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {"url": img}
            })
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": 4096
        }
        
        # Call API
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
        return result["choices"][0]["message"]["content"]
    
    async def close(self):
        """Close the client (no-op for httpx)."""
        pass
