"""
Claude Sonnet 4.5 Client - Primary AI engine for analysis and generation.

Integrates with Anthropic's Claude API for character analysis, narrative
recognition, and transformation rule generation.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import Optional, List, Any
import os
import logging
from anthropic import Anthropic, AsyncAnthropic

from src.services.ai.base_client import BaseAIClient, AIResponse, AIClientError

logger = logging.getLogger(__name__)


class ClaudeClient(BaseAIClient):
    """
    Claude Sonnet 4.5 API client.
    
    Primary AI engine for DOPPELGANGER STUDIO. Handles character analysis,
    narrative structure recognition, and transformation rule generation.
    
    Features:
    - Anthropic Messages API integration
    - Automatic retry with exponential backoff
    - Token usage tracking
    - Cost calculation
    - Structured JSON responses
    
    Pricing (as of 2025):
    - Input: $3 per million tokens
    - Output: $15 per million tokens
    
    Example:
        >>> import os
        >>> client = ClaudeClient(api_key=os.getenv('ANTHROPIC_API_KEY'))
        >>> response = await client.complete(
        ...     prompt="Analyze Lucy Ricardo's character traits",
        ...     system="You are an expert TV character analyst"
        ... )
        >>> print(response.content)
    """
    
    MODEL = "claude-sonnet-4-20250514"
    INPUT_COST_PER_MTOK = 3.00   # $3 per million input tokens
    OUTPUT_COST_PER_MTOK = 15.00  # $15 per million output tokens
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        timeout_seconds: int = 60
    ):
        """
        Initialize Claude client.
        
        Args:
            api_key: Anthropic API key. If None, loads from ANTHROPIC_API_KEY env var
            max_retries: Maximum retry attempts on failure
            timeout_seconds: Request timeout in seconds
            
        Raises:
            ValueError: If API key not provided and not in environment
        """
        # Get API key
        api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter. Get key at: https://console.anthropic.com/"
            )
        
        super().__init__(
            api_key=api_key,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds
        )
        
        # Initialize Anthropic client
        self.client = AsyncAnthropic(api_key=api_key)
        
        logger.info(f"Claude client initialized (model: {self.MODEL})")
    
    async def _make_api_call(
        self,
        prompt: str,
        system: Optional[str],
        max_tokens: int,
        temperature: float,
        stop_sequences: Optional[List[str]]
    ) -> Any:
        """
        Make API call to Anthropic.
        
        Args:
            prompt: User prompt
            system: System prompt for behavior control
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            stop_sequences: Optional stop sequences
            
        Returns:
            Anthropic Message response
            
        Raises:
            Various Anthropic API exceptions
        """
        try:
            # Build request parameters
            params = {
                "model": self.MODEL,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Add optional parameters
            if system:
                params["system"] = system
            
            if stop_sequences:
                params["stop_sequences"] = stop_sequences
            
            logger.debug(f"Calling Claude API with {len(prompt)} char prompt")
            
            # Make API call
            response = await self.client.messages.create(**params)
            
            logger.debug(
                f"Claude API response: {response.usage.input_tokens} input tokens, "
                f"{response.usage.output_tokens} output tokens"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise
    
    def _parse_response(self, raw_response: Any) -> AIResponse:
        """
        Parse Anthropic Message response to standard format.
        
        Args:
            raw_response: Anthropic Message object
            
        Returns:
            Standardized AIResponse
        """
        # Extract text content
        content = ""
        for block in raw_response.content:
            if block.type == "text":
                content += block.text
        
        # Extract token usage
        input_tokens = raw_response.usage.input_tokens
        output_tokens = raw_response.usage.output_tokens
        
        # Calculate cost
        cost = self.calculate_cost(input_tokens, output_tokens)
        
        return AIResponse(
            content=content,
            model=raw_response.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            latency_ms=0.0,  # Will be set by base class
            metadata={
                "stop_reason": raw_response.stop_reason,
                "id": raw_response.id
            }
        )
    
    async def stream_complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ):
        """
        Stream completion response token by token.
        
        Useful for long responses where you want to show progress.
        
        Args:
            prompt: User prompt
            system: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Yields:
            Text chunks as they arrive
            
        Example:
            >>> async for chunk in client.stream_complete(prompt):
            ...     print(chunk, end='', flush=True)
        """
        params = {
            "model": self.MODEL,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system:
            params["system"] = system
        
        logger.debug(f"Starting Claude streaming response")
        
        async with self.client.messages.stream(**params) as stream:
            async for text in stream.text_stream:
                yield text
        
        # Get final message for token counting
        final_message = await stream.get_final_message()
        
        logger.info(
            f"Claude stream complete: {final_message.usage.input_tokens} input, "
            f"{final_message.usage.output_tokens} output tokens"
        )


# Example usage
async def main():
    """Example usage of Claude client."""
    import asyncio
    
    # Get API key from environment
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Get your API key at: https://console.anthropic.com/")
        return
    
    client = ClaudeClient(api_key=api_key)
    
    # Example 1: Simple completion
    print("Example 1: Simple completion")
    print("=" * 50)
    
    response = await client.complete(
        prompt="In 2-3 sentences, describe Lucy Ricardo's personality from I Love Lucy.",
        system="You are an expert TV character analyst.",
        max_tokens=200,
        temperature=0.7
    )
    
    print(f"Response: {response.content}")
    print(f"Tokens: {response.input_tokens} in, {response.output_tokens} out")
    print(f"Cost: ${response.cost:.4f}")
    print(f"Latency: {response.latency_ms:.0f}ms")
    print()
    
    # Example 2: Structured JSON response
    print("Example 2: Structured JSON")
    print("=" * 50)
    
    schema = {
        "type": "object",
        "properties": {
            "traits": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Core personality traits"
            },
            "catchphrase": {
                "type": "string",
                "description": "Famous catchphrase"
            }
        },
        "required": ["traits", "catchphrase"]
    }
    
    result = await client.complete_json(
        prompt="Analyze Lucy Ricardo from I Love Lucy",
        schema=schema,
        system="You are a TV character analyst. Extract key traits and catchphrases."
    )
    
    print(f"Traits: {', '.join(result['traits'])}")
    print(f"Catchphrase: {result['catchphrase']}")
    print()
    
    # Example 3: Streaming response
    print("Example 3: Streaming response")
    print("=" * 50)
    
    print("Streaming: ", end='', flush=True)
    async for chunk in client.stream_complete(
        prompt="Write a 50-word description of 1950s TV comedy.",
        max_tokens=150
    ):
        print(chunk, end='', flush=True)
    print("\n")
    
    # Show usage statistics
    print("Usage Statistics:")
    print("=" * 50)
    stats = client.get_stats()
    print(f"Total requests: {stats.total_requests}")
    print(f"Successful: {stats.successful_requests}")
    print(f"Failed: {stats.failed_requests}")
    print(f"Total tokens: {stats.total_input_tokens + stats.total_output_tokens}")
    print(f"Total cost: ${stats.total_cost:.4f}")
    print(f"Avg latency: {stats.average_latency_ms:.0f}ms")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
