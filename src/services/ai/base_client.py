"""
Base AI Client - Abstract interface for AI service providers.

Provides common interface for Claude, GPT-4, and future AI models with
token tracking, cost calculation, and retry logic.

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """Container for AI completion response."""
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    latency_ms: float
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIUsageStats:
    """Track AI API usage statistics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0
    average_latency_ms: float = 0.0
    
    def record_request(
        self,
        success: bool,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        latency_ms: float
    ):
        """Record a request in statistics."""
        self.total_requests += 1
        
        if success:
            self.successful_requests += 1
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_cost += cost
            
            # Update running average
            total_latency = self.average_latency_ms * (self.successful_requests - 1)
            self.average_latency_ms = (total_latency + latency_ms) / self.successful_requests
        else:
            self.failed_requests += 1


class BaseAIClient(ABC):
    """
    Abstract base class for AI service clients.
    
    Provides common interface for different AI providers (Claude, GPT-4, etc.)
    with standardized retry logic, cost tracking, and error handling.
    
    Subclasses must implement:
    - _make_api_call: Provider-specific API interaction
    - _parse_response: Convert provider response to AIResponse
    - MODEL: Model identifier string
    - INPUT_COST_PER_MTOK: Cost per million input tokens
    - OUTPUT_COST_PER_MTOK: Cost per million output tokens
    
    Example:
        >>> class ClaudeClient(BaseAIClient):
        ...     MODEL = "claude-sonnet-4-20250514"
        ...     INPUT_COST_PER_MTOK = 3.00
        ...     OUTPUT_COST_PER_MTOK = 15.00
        ...     
        ...     async def _make_api_call(self, **kwargs):
        ...         # Anthropic API call
        ...         pass
    """
    
    # Subclasses must define these
    MODEL: str = NotImplemented
    INPUT_COST_PER_MTOK: float = NotImplemented
    OUTPUT_COST_PER_MTOK: float = NotImplemented
    
    def __init__(
        self,
        api_key: str,
        max_retries: int = 3,
        timeout_seconds: int = 60
    ):
        """
        Initialize AI client.
        
        Args:
            api_key: API key for the service
            max_retries: Maximum retry attempts on failure
            timeout_seconds: Request timeout in seconds
        """
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.stats = AIUsageStats()
    
    async def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stop_sequences: Optional[List[str]] = None
    ) -> AIResponse:
        """
        Generate text completion.
        
        Args:
            prompt: User prompt/question
            system: Optional system prompt for behavior
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            stop_sequences: Optional sequences that stop generation
            
        Returns:
            AIResponse with content and metadata
            
        Raises:
            AIClientError: If all retry attempts fail
            
        Example:
            >>> response = await client.complete(
            ...     prompt="Analyze this character: Lucy Ricardo",
            ...     system="You are a TV character analyst",
            ...     temperature=0.7
            ... )
            >>> print(response.content)
        """
        import time
        start_time = time.time()
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"API request attempt {attempt + 1}/{self.max_retries} "
                    f"(model: {self.MODEL})"
                )
                
                # Make API call (implemented by subclass)
                raw_response = await asyncio.wait_for(
                    self._make_api_call(
                        prompt=prompt,
                        system=system,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stop_sequences=stop_sequences
                    ),
                    timeout=self.timeout_seconds
                )
                
                # Parse response (implemented by subclass)
                response = self._parse_response(raw_response)
                
                # Calculate latency
                response.latency_ms = (time.time() - start_time) * 1000
                
                # Record success
                self.stats.record_request(
                    success=True,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    cost=response.cost,
                    latency_ms=response.latency_ms
                )
                
                logger.info(
                    f"AI request successful: {response.output_tokens} tokens, "
                    f"${response.cost:.4f}, {response.latency_ms:.0f}ms"
                )
                
                return response
                
            except asyncio.TimeoutError:
                last_error = AIClientError(f"Request timeout after {self.timeout_seconds}s")
                logger.warning(f"Attempt {attempt + 1} timed out")
                
                if attempt < self.max_retries - 1:
                    await self._exponential_backoff(attempt)
                    
            except Exception as e:
                last_error = AIClientError(f"API request failed: {e}")
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    await self._exponential_backoff(attempt)
        
        # All retries failed
        self.stats.record_request(
            success=False,
            input_tokens=0,
            output_tokens=0,
            cost=0.0,
            latency_ms=0.0
        )
        
        logger.error(f"All {self.max_retries} retry attempts failed")
        raise last_error
    
    async def complete_json(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system: Optional[str] = None,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response.
        
        Args:
            prompt: User prompt requesting structured data
            schema: JSON schema describing expected structure
            system: Optional system prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Parsed JSON dict matching schema
            
        Raises:
            AIClientError: If response is not valid JSON
            
        Example:
            >>> schema = {
            ...     "type": "object",
            ...     "properties": {
            ...         "traits": {"type": "array"},
            ...         "relationships": {"type": "object"}
            ...     }
            ... }
            >>> result = await client.complete_json(
            ...     prompt="Analyze Lucy Ricardo",
            ...     schema=schema
            ... )
            >>> print(result['traits'])
        """
        import json
        
        # Add JSON formatting instructions to prompt
        json_prompt = f"""{prompt}

IMPORTANT: Respond ONLY with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Do not include any text before or after the JSON. Start with {{ and end with }}.
"""
        
        # Use temperature=0.3 for more deterministic JSON
        response = await self.complete(
            prompt=json_prompt,
            system=system,
            max_tokens=max_tokens,
            temperature=0.3
        )
        
        # Parse JSON
        try:
            # Strip markdown code blocks if present
            content = response.content.strip()
            if content.startswith('```'):
                # Remove ```json and ```
                lines = content.split('\n')
                content = '\n'.join(lines[1:-1])
            
            result = json.loads(content)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response content: {response.content[:500]}")
            raise AIClientError(f"Invalid JSON response: {e}")
    
    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost for token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in USD
            
        Example:
            >>> cost = client.calculate_cost(1000, 500)
            >>> print(f"${cost:.4f}")
        """
        input_cost = (input_tokens / 1_000_000) * self.INPUT_COST_PER_MTOK
        output_cost = (output_tokens / 1_000_000) * self.OUTPUT_COST_PER_MTOK
        return input_cost + output_cost
    
    async def _exponential_backoff(self, attempt: int):
        """
        Wait with exponential backoff before retry.
        
        Args:
            attempt: Retry attempt number (0-indexed)
        """
        delay = min(2 ** attempt, 32)  # Max 32 seconds
        logger.debug(f"Backing off for {delay}s before retry")
        await asyncio.sleep(delay)
    
    @abstractmethod
    async def _make_api_call(
        self,
        prompt: str,
        system: Optional[str],
        max_tokens: int,
        temperature: float,
        stop_sequences: Optional[List[str]]
    ) -> Any:
        """
        Make provider-specific API call.
        
        Must be implemented by subclasses.
        
        Args:
            prompt: User prompt
            system: System prompt
            max_tokens: Max tokens to generate
            temperature: Sampling temperature
            stop_sequences: Stop sequences
            
        Returns:
            Provider-specific response object
        """
        pass
    
    @abstractmethod
    def _parse_response(self, raw_response: Any) -> AIResponse:
        """
        Parse provider response to standard format.
        
        Must be implemented by subclasses.
        
        Args:
            raw_response: Provider-specific response
            
        Returns:
            Standardized AIResponse
        """
        pass
    
    def get_stats(self) -> AIUsageStats:
        """
        Get usage statistics.
        
        Returns:
            Current usage statistics
            
        Example:
            >>> stats = client.get_stats()
            >>> print(f"Total cost: ${stats.total_cost:.2f}")
            >>> print(f"Success rate: {stats.successful_requests / stats.total_requests:.1%}")
        """
        return self.stats
    
    def reset_stats(self):
        """Reset usage statistics to zero."""
        self.stats = AIUsageStats()


class AIClientError(Exception):
    """Exception raised for AI client errors."""
    pass
