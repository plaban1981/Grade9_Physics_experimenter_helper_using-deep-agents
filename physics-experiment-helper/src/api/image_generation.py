"""Image generation service using Replicate API."""

import os
import replicate
import requests
from typing import List, Optional, Dict, Any
from pathlib import Path
import tempfile
from dotenv import load_dotenv

load_dotenv()


class ImageGenerationService:
    """Service for generating images using Replicate API."""
    
    def __init__(self):
        """Initialize the image generation service."""
        self.replicate_token = os.getenv("REPLICATE_API_TOKEN")
        if not self.replicate_token:
            raise ValueError("REPLICATE_API_TOKEN environment variable is required")
        
        # Set the Replicate API token
        os.environ["REPLICATE_API_TOKEN"] = self.replicate_token
        
        # Initialize the replicate client
        try:
            import replicate
            self.replicate_client = replicate
        except ImportError:
            raise ImportError("replicate package is not installed. Please install it with: pip install replicate")
    
    def generate_experiment_image(
        self, 
        experiment_topic: str, 
        prompt: Optional[str] = None,
        style: str = "scientific",
        aspect_ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """
        Generate an image for a physics experiment.
        
        Args:
            experiment_topic: The topic of the experiment
            prompt: Custom prompt (optional)
            style: Image style (scientific, educational, diagram)
            aspect_ratio: Image aspect ratio
            
        Returns:
            Dictionary containing image URL and metadata
        """
        try:
            # Create a detailed prompt for the experiment
            if not prompt:
                prompt = self._create_experiment_prompt(experiment_topic, style)
            
            # Use the nano-banana model as specified
            output = self.replicate_client.run(
                "google/nano-banana",
                input={
                    "prompt": prompt,
                    "image_input": [
                        "https://replicate.delivery/pbxt/NbYIclp4A5HWLsJ8lF5KgiYSNaLBBT1jUcYcHYQmN1uy5OnN/tmpcqc07f_q.png",
                        "https://replicate.delivery/pbxt/NbYId45yH8s04sptdtPcGqFIhV7zS5GTcdS3TtNliyTAoYPO/Screenshot%202025-08-26%20at%205.30.12%E2%80%AFPM.png"
                    ],
                    "aspect_ratio": "match_input_image",
                    "output_format": "jpg"
                }
            )
            
            # Get the image URL - handle different output types
            if isinstance(output, str):
                image_url = output
            elif hasattr(output, 'url') and callable(getattr(output, 'url')):
                image_url = output.url()
            elif hasattr(output, 'url'):
                image_url = output.url
            else:
                image_url = str(output)
            
            # Download and save the image locally
            local_path = self._download_and_save_image(image_url, experiment_topic)
            
            return {
                "url": image_url,
                "local_path": local_path,
                "prompt": prompt,
                "experiment_topic": experiment_topic,
                "style": style,
                "aspect_ratio": aspect_ratio,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "url": None,
                "local_path": None,
                "prompt": prompt,
                "experiment_topic": experiment_topic,
                "style": style,
                "aspect_ratio": aspect_ratio,
                "status": "error",
                "error": str(e)
            }
    
    def generate_multiple_images(
        self, 
        experiment_topic: str, 
        count: int = 3,
        styles: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple images for an experiment.
        
        Args:
            experiment_topic: The topic of the experiment
            count: Number of images to generate
            styles: List of styles to use
            
        Returns:
            List of image generation results
        """
        if styles is None:
            styles = ["scientific", "educational", "diagram"]
        
        results = []
        for i in range(count):
            style = styles[i % len(styles)]
            result = self.generate_experiment_image(
                experiment_topic=f"{experiment_topic} - Image {i+1}",
                style=style
            )
            results.append(result)
        
        return results
    
    def _create_experiment_prompt(self, experiment_topic: str, style: str) -> str:
        """Create a detailed prompt for the experiment image."""
        base_prompt = f"Generate an image for the science experiment: {experiment_topic}"
        
        style_prompts = {
            "scientific": f"{base_prompt}. Scientific illustration style, clean and professional, showing equipment, setup, or results. High quality, detailed, educational.",
            "educational": f"{base_prompt}. Educational diagram style, clear and simple, suitable for Grade 9 students. Colorful, engaging, easy to understand.",
            "diagram": f"{base_prompt}. Technical diagram style, showing step-by-step process, labeled components, scientific accuracy. Black and white or minimal colors."
        }
        
        return style_prompts.get(style, base_prompt)
    
    def _download_and_save_image(self, image_url: str, experiment_topic: str) -> str:
        """Download and save image to local storage."""
        try:
            # Create temp directory for images
            temp_dir = Path("temp") / "images"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Download the image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Create filename from experiment topic
            safe_topic = "".join(c for c in experiment_topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_topic = safe_topic.replace(' ', '_')[:50]  # Limit length
            
            # Save the image
            filename = f"{safe_topic}_{hash(image_url) % 10000}.jpg"
            file_path = temp_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return str(file_path)
            
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None
    
    def get_image_data(self, local_path: str) -> Optional[bytes]:
        """Get image data from local path."""
        try:
            if local_path and Path(local_path).exists():
                with open(local_path, 'rb') as f:
                    return f.read()
        except Exception as e:
            print(f"Error reading image data: {e}")
        return None


# Global instance
image_service = ImageGenerationService()
