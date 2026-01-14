"""LLM client for API interactions."""

import openai
import asyncio
from typing import List, Dict, Optional, Any
import tiktoken
import os

from .config import ModelConfig


class LLMClient:
    """
    Unified client for LLM API interactions.
    
    Supports multiple providers:
    - OpenAI (GPT-3.5, GPT-4)
    - Anthropic (Claude)
    - Custom providers
    """
    
    def __init__(self, config: ModelConfig):
        """
        Initialize LLM client.
        
        Args:
            config: Model configuration
        """
        self.config = config
        self.provider = config.provider
        self.model = config.model
        
        if self.provider == "openai":
            openai.api_key = config.api_key
            try:
                self.encoding = tiktoken.encoding_for_model(self.model)
            except:
                # Fallback encoding
                self.encoding = tiktoken.get_encoding("cl100k_base")
    
    async def generate(self, 
                      prompt: str, 
                      system_message: Optional[str] = None,
                      temperature: Optional[float] = None,
                      max_tokens: Optional[int] = None) -> str:
        """
        Generate text from prompt.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            temperature: Sampling temperature (overrides config)
            max_tokens: Max tokens (overrides config)
            
        Returns:
            Generated text
        """
        temp = temperature if temperature is not None else self.config.temperature
        max_tok = max_tokens if max_tokens is not None else self.config.max_tokens
        
        if self.provider == "openai":
            return await self._openai_generate(prompt, system_message, temp, max_tok)
        elif self.provider == "anthropic":
            return await self._anthropic_generate(prompt, system_message, temp, max_tok)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _openai_generate(self, prompt: str, system_message: Optional[str],
                              temperature: float, max_tokens: int) -> str:
        """
        OpenAI-specific generation.
        
        Args:
            prompt: User prompt
            system_message: System message
            temperature: Temperature
            max_tokens: Max tokens
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    async def _anthropic_generate(self, prompt: str, system_message: Optional[str],
                                 temperature: float, max_tokens: int) -> str:
        """
        Anthropic-specific generation.
        
        Args:
            prompt: User prompt
            system_message: System message
            temperature: Temperature
            max_tokens: Max tokens
            
        Returns:
            Generated text
        """
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package required for Anthropic provider")
        
        client = anthropic.AsyncAnthropic(api_key=self.config.api_key)
        
        full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
        
        response = await client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        return response.content[0].text
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count
            
        Returns:
            Token count
        """
        if self.provider == "openai":
            return len(self.encoding.encode(text))
        # Rough estimate for other providers
        return len(text.split())
    
    async def generate_structured(self, 
                                 prompt: str,
                                 schema: Dict,
                                 **kwargs) -> Dict:
        """
        Generate structured output matching schema.
        
        Args:
            prompt: Generation prompt
            schema: JSON schema for output
            **kwargs: Additional generation parameters
            
        Returns:
            Structured output
        """
        # Implementation would use function calling or JSON mode
        # For now, return placeholder
        return {}