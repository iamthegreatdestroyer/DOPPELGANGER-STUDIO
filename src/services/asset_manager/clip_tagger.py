"""
CLIP Semantic Tagger - AI-powered visual content tagging system.

This module implements semantic tagging using OpenAI's CLIP model:
1. Extracts keyframes from videos using FFmpeg
2. Generates CLIP embeddings for visual understanding
3. Creates semantic tags from pre-defined vocabularies
4. Supports batch processing for efficiency
5. Caches embeddings for reuse

Copyright (c) 2025. All Rights Reserved. Patent Pending.
"""

from typing import List, Dict, Optional, Tuple
import asyncio
import logging
from pathlib import Path
import tempfile
import subprocess
import numpy as np
from PIL import Image
import torch
import clip

logger = logging.getLogger(__name__)


class CLIPSemanticTagger:
    """
    Semantic tagging engine using CLIP embeddings.
    
    Features:
    - Video keyframe extraction with FFmpeg
    - CLIP ViT-B/32 model for visual understanding
    - Pre-defined tag vocabularies for different domains
    - Batch processing for efficiency
    - Embedding caching for performance
    
    Example:
        >>> tagger = CLIPSemanticTagger()
        >>> await tagger.initialize()
        >>> tags = await tagger.generate_tags(asset)
        >>> print(tags)  # ['nature', 'landscape', 'mountains', 'scenic']
    """
    
    # Comprehensive tag vocabularies
    GENERAL_TAGS = [
        "nature", "landscape", "mountains", "ocean", "forest", "desert",
        "city", "urban", "architecture", "buildings", "street", "skyline",
        "people", "person", "group", "crowd", "portrait", "silhouette",
        "technology", "computer", "phone", "device", "screen", "digital",
        "abstract", "pattern", "texture", "geometric", "colorful", "minimal",
        "sky", "clouds", "sunset", "sunrise", "night", "stars", "space",
        "water", "river", "lake", "beach", "waves", "underwater",
        "animals", "wildlife", "pets", "birds", "fish", "insects",
        "plants", "flowers", "trees", "garden", "vegetation",
        "food", "cooking", "meal", "restaurant", "ingredients",
        "transportation", "car", "train", "plane", "boat", "travel",
        "sports", "fitness", "exercise", "running", "cycling", "gym",
        "art", "painting", "sculpture", "drawing", "creative",
        "music", "instrument", "concert", "performance", "dance",
        "business", "office", "work", "meeting", "professional",
        "education", "school", "learning", "books", "classroom",
        "home", "interior", "furniture", "living room", "bedroom", "kitchen",
        "fashion", "clothing", "style", "accessories", "model",
        "celebration", "party", "holiday", "wedding", "festival",
        "science", "laboratory", "research", "experiment", "medical"
    ]
    
    MOOD_TAGS = [
        "peaceful", "calm", "serene", "relaxing", "tranquil",
        "energetic", "dynamic", "active", "exciting", "vibrant",
        "dramatic", "intense", "powerful", "epic", "cinematic",
        "mysterious", "dark", "moody", "atmospheric", "ethereal",
        "happy", "joyful", "cheerful", "uplifting", "positive",
        "professional", "corporate", "clean", "modern", "sleek"
    ]
    
    TECHNICAL_TAGS = [
        "aerial", "drone", "overhead", "bird's eye view",
        "closeup", "macro", "detail", "zoom",
        "wide angle", "panoramic", "landscape orientation",
        "slow motion", "timelapse", "fast motion",
        "static", "moving", "panning", "tracking",
        "bright", "dark", "high contrast", "low contrast",
        "sharp", "blurred", "bokeh", "depth of field",
        "daytime", "nighttime", "golden hour", "blue hour"
    ]
    
    def __init__(self, model_name: str = "ViT-B/32", device: Optional[str] = None):
        """
        Initialize CLIP tagger.
        
        Args:
            model_name: CLIP model variant (default: ViT-B/32)
            device: Device to run on ('cuda', 'cpu', or None for auto)
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.preprocess = None
        self.tag_embeddings: Dict[str, torch.Tensor] = {}
        self._initialized = False
        
        logger.info(f"CLIP tagger configured for {self.device}")
    
    async def initialize(self):
        """
        Initialize CLIP model and pre-compute tag embeddings.
        
        This is an async wrapper around model loading to avoid blocking.
        """
        if self._initialized:
            return
        
        logger.info(f"Loading CLIP model {self.model_name}...")
        
        # Load model in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._load_model)
        
        # Pre-compute embeddings for all tags
        await self._compute_tag_embeddings()
        
        self._initialized = True
        logger.info("CLIP tagger initialized successfully")
    
    def _load_model(self):
        """Load CLIP model (blocking operation)."""
        self.model, self.preprocess = clip.load(
            self.model_name, 
            device=self.device
        )
        self.model.eval()
    
    async def _compute_tag_embeddings(self):
        """Pre-compute embeddings for all tags."""
        logger.info("Computing tag embeddings...")
        
        all_tags = (
            self.GENERAL_TAGS + 
            self.MOOD_TAGS + 
            self.TECHNICAL_TAGS
        )
        
        # Process in batches for efficiency
        batch_size = 64
        for i in range(0, len(all_tags), batch_size):
            batch = all_tags[i:i + batch_size]
            
            # Create text prompts
            prompts = [f"a photo of {tag}" for tag in batch]
            
            # Tokenize and encode
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                self._encode_text,
                prompts
            )
            
            # Store embeddings
            for tag, embedding in zip(batch, embeddings):
                self.tag_embeddings[tag] = embedding
        
        logger.info(f"Computed {len(self.tag_embeddings)} tag embeddings")
    
    def _encode_text(self, prompts: List[str]) -> torch.Tensor:
        """Encode text prompts (blocking operation)."""
        with torch.no_grad():
            text = clip.tokenize(prompts).to(self.device)
            embeddings = self.model.encode_text(text)
            embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
        return embeddings
    
    async def generate_tags(
        self, 
        video_url: str, 
        local_path: Optional[Path] = None,
        top_k: int = 10,
        threshold: float = 0.25
    ) -> List[str]:
        """
        Generate semantic tags for a video.
        
        Args:
            video_url: URL of video (for remote videos)
            local_path: Local path to video file
            top_k: Number of tags to return
            threshold: Minimum similarity threshold (0.0-1.0)
        
        Returns:
            List of semantic tags ordered by relevance
        
        Example:
            >>> tags = await tagger.generate_tags(
            ...     video_url="https://example.com/video.mp4",
            ...     local_path=Path("/tmp/video.mp4"),
            ...     top_k=10
            ... )
            >>> print(tags)  # ['nature', 'forest', 'trees', ...]
        """
        if not self._initialized:
            await self.initialize()
        
        # Extract keyframes from video
        keyframes = await self._extract_keyframes(local_path or video_url)
        
        if not keyframes:
            logger.warning("No keyframes extracted, using default tags")
            return ["video", "content", "media"]
        
        # Generate embeddings for each keyframe
        all_similarities = []
        
        for keyframe in keyframes:
            similarities = await self._compute_similarities(keyframe)
            all_similarities.append(similarities)
        
        # Average similarities across all keyframes
        avg_similarities = {}
        for tag in self.tag_embeddings.keys():
            scores = [sim.get(tag, 0.0) for sim in all_similarities]
            avg_similarities[tag] = np.mean(scores)
        
        # Filter by threshold and sort
        filtered_tags = {
            tag: score 
            for tag, score in avg_similarities.items() 
            if score >= threshold
        }
        
        sorted_tags = sorted(
            filtered_tags.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Return top k tags
        tags = [tag for tag, score in sorted_tags[:top_k]]
        
        logger.info(f"Generated {len(tags)} tags: {tags}")
        return tags
    
    async def _extract_keyframes(
        self, 
        video_source: str | Path,
        max_frames: int = 5
    ) -> List[Image.Image]:
        """
        Extract keyframes from video using FFmpeg.
        
        Args:
            video_source: Video file path or URL
            max_frames: Maximum number of frames to extract
        
        Returns:
            List of PIL Images
        """
        try:
            # Create temporary directory for frames
            with tempfile.TemporaryDirectory() as tmpdir:
                output_pattern = Path(tmpdir) / "frame_%03d.jpg"
                
                # FFmpeg command to extract frames
                # Extract 1 frame every N seconds (distributed across video)
                cmd = [
                    "ffmpeg",
                    "-i", str(video_source),
                    "-vf", f"select='not(mod(n\\,30))',scale=224:224",  # Every 30th frame
                    "-frames:v", str(max_frames),
                    "-q:v", "2",  # High quality
                    "-y",  # Overwrite
                    str(output_pattern)
                ]
                
                logger.debug(f"Extracting keyframes with: {' '.join(cmd)}")
                
                # Run FFmpeg
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    subprocess.run,
                    cmd,
                    {"capture_output": True, "check": True}
                )
                
                # Load extracted frames
                frames = []
                for frame_path in sorted(Path(tmpdir).glob("frame_*.jpg")):
                    try:
                        img = Image.open(frame_path).convert("RGB")
                        frames.append(img)
                    except Exception as e:
                        logger.warning(f"Failed to load frame {frame_path}: {e}")
                
                logger.info(f"Extracted {len(frames)} keyframes")
                return frames
        
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
            return []
        except Exception as e:
            logger.error(f"Keyframe extraction failed: {e}")
            return []
    
    async def _compute_similarities(
        self, 
        image: Image.Image
    ) -> Dict[str, float]:
        """
        Compute similarity scores between image and all tags.
        
        Args:
            image: PIL Image to analyze
        
        Returns:
            Dictionary mapping tags to similarity scores
        """
        # Preprocess image
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        
        # Encode image
        loop = asyncio.get_event_loop()
        image_embedding = await loop.run_in_executor(
            None,
            self._encode_image,
            image_input
        )
        
        # Compute similarities with all tags
        similarities = {}
        for tag, tag_embedding in self.tag_embeddings.items():
            similarity = float(
                (image_embedding @ tag_embedding.T).squeeze().cpu()
            )
            similarities[tag] = similarity
        
        return similarities
    
    def _encode_image(self, image_input: torch.Tensor) -> torch.Tensor:
        """Encode image (blocking operation)."""
        with torch.no_grad():
            embedding = self.model.encode_image(image_input)
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        return embedding
    
    async def generate_embeddings(
        self,
        video_url: str,
        local_path: Optional[Path] = None
    ) -> Optional[np.ndarray]:
        """
        Generate CLIP embeddings for video (for vector search).
        
        Args:
            video_url: URL of video
            local_path: Local path to video file
        
        Returns:
            Numpy array of embeddings (averaged across keyframes)
        """
        if not self._initialized:
            await self.initialize()
        
        keyframes = await self._extract_keyframes(local_path or video_url)
        
        if not keyframes:
            return None
        
        # Generate embeddings for each keyframe
        embeddings = []
        
        for keyframe in keyframes:
            image_input = self.preprocess(keyframe).unsqueeze(0).to(self.device)
            
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                self._encode_image,
                image_input
            )
            
            embeddings.append(embedding.cpu().numpy())
        
        # Average embeddings
        avg_embedding = np.mean(embeddings, axis=0)
        
        return avg_embedding.flatten()
    
    async def batch_generate_tags(
        self,
        videos: List[Tuple[str, Optional[Path]]],
        top_k: int = 10,
        threshold: float = 0.25
    ) -> List[List[str]]:
        """
        Generate tags for multiple videos in batch.
        
        Args:
            videos: List of (url, local_path) tuples
            top_k: Number of tags per video
            threshold: Minimum similarity threshold
        
        Returns:
            List of tag lists for each video
        """
        tasks = [
            self.generate_tags(url, path, top_k, threshold)
            for url, path in videos
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to empty lists
        return [
            result if not isinstance(result, Exception) else []
            for result in results
        ]
