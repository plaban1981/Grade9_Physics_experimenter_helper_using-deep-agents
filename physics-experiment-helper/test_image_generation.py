#!/usr/bin/env python3
"""Test script for image generation functionality."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_image_generation():
    """Test the image generation service."""
    print("🔬 Testing Physics Experiment Helper - Image Generation")
    print("=" * 60)
    
    # Check if Replicate API token is set
    if not os.getenv("REPLICATE_API_TOKEN"):
        print("❌ REPLICATE_API_TOKEN not found in environment variables")
        print("   Please set your Replicate API token:")
        print("   export REPLICATE_API_TOKEN=your_token_here")
        return False
    
    try:
        from api.image_generation import image_service
        print("✅ Image generation service imported successfully")
        
        # Test image generation
        print("\n🎨 Testing image generation...")
        result = image_service.generate_experiment_image(
            experiment_topic="Simple pendulum experiment setup",
            style="scientific"
        )
        
        if result["status"] == "success":
            print("✅ Image generated successfully!")
            print(f"   URL: {result['url']}")
            print(f"   Local path: {result['local_path']}")
            print(f"   Style: {result['style']}")
            return True
        else:
            print(f"❌ Image generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import image generation service: {e}")
        print("   Make sure to install replicate: pip install replicate")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def test_agent_tools():
    """Test the agent tools."""
    print("\n🤖 Testing agent tools...")
    
    try:
        from agent.physics_agent import IMAGE_GENERATION_AVAILABLE
        if IMAGE_GENERATION_AVAILABLE:
            print("✅ Image generation tools available in agent")
            return True
        else:
            print("❌ Image generation tools not available in agent")
            return False
    except Exception as e:
        print(f"❌ Error testing agent tools: {e}")
        return False

if __name__ == "__main__":
    print("Starting tests...\n")
    
    # Test image generation
    image_test = test_image_generation()
    
    # Test agent tools
    agent_test = test_agent_tools()
    
    print("\n" + "=" * 60)
    if image_test and agent_test:
        print("🎉 All tests passed! Image generation is ready to use.")
        print("\nTo use the application:")
        print("1. Set your API keys in .env file")
        print("2. Run: python run.py")
        print("3. Open: http://localhost:8000")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
