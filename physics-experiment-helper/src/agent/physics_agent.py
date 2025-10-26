"""Physics Experiment Helper Agent using deepagents library."""

import os
import requests
from typing import Literal
from deepagents import create_deep_agent
from deepagents.sub_agent import SubAgent
from langchain_core.tools import tool
from agent.prompts import (
    PHYSICS_EXPERIMENT_SYSTEM_PROMPT,
    RESEARCH_AGENT_PROMPT,
    CRITIQUE_AGENT_PROMPT,
)
from dotenv import load_dotenv
load_dotenv()

# Import image generation service
try:
    from api.image_generation import image_service
    IMAGE_GENERATION_AVAILABLE = True
except ImportError:
    IMAGE_GENERATION_AVAILABLE = False
    print("Warning: Image generation service not available. Install replicate package.")


@tool
def internet_search(
    query: str,
    max_results: int = 5,
    search_engine: str = "google"
) -> str:
    """Run a web search for physics education resources and experiment information.

    Args:
        query: Search query string
        max_results: Maximum number of results to return
        search_engine: Search engine to use (google, bing, duckduckgo)

    Returns:
        Search results including web pages, images, and educational resources
    """
    try:
        # Try SerpAPI first if available
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        if serpapi_key:
            return _search_with_serpapi(query, max_results, serpapi_key)
        
        # Fallback to DuckDuckGo (free, no API key needed)
        return _search_with_duckduckgo(query, max_results)
        
    except Exception as e:
        # If all else fails, return a mock response to prevent recursion
        return f"Search temporarily unavailable. Query: '{query}'. Error: {str(e)}. Please proceed with general knowledge about physics experiments."


def _search_with_serpapi(query: str, max_results: int, api_key: str) -> str:
    """Search using SerpAPI (most reliable)"""
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": api_key,
        "num": max_results,
        "engine": "google",
        "safe": "active"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    results = []
    if "organic_results" in data:
        for result in data["organic_results"][:max_results]:
            results.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", "")
            })
    
    # Add images if available
    if "images" in data and data["images"]:
        results.append({"type": "images", "count": len(data["images"])})
    
    return f"Search results for '{query}': {results}"


def _search_with_duckduckgo(query: str, max_results: int) -> str:
    """Search using DuckDuckGo (free, no API key needed)"""
    try:
        from ddgs import DDGS
        
        with DDGS() as ddgs:
            results = []
            
            # Get web results
            web_results = list(ddgs.text(query, max_results=max_results))
            for result in web_results:
                results.append({
                    "title": result.get("title", ""),
                    "link": result.get("href", ""),
                    "snippet": result.get("body", "")
                })
            
            # Get image results
            try:
                image_results = list(ddgs.images(query, max_results=3))
                if image_results:
                    results.append({
                        "type": "images", 
                        "count": len(image_results),
                        "samples": [img.get("title", "") for img in image_results[:3]]
                    })
            except:
                pass  # Images are optional
            
            return f"Search results for '{query}': {results}"
            
    except ImportError:
        # If ddgs is not installed, return a basic response
        return f"Search query: '{query}'. Please use general physics knowledge to create the experiment guide."


@tool
def generate_experiment_image(
    experiment_topic: str,
    style: str = "scientific",
    custom_prompt: str = None
) -> str:
    """Generate an image for a physics experiment using AI.
    
    Args:
        experiment_topic: The topic or title of the experiment
        style: Image style - 'scientific' (professional), 'educational' (student-friendly), or 'diagram' (technical)
        custom_prompt: Optional custom prompt for image generation
        
    Returns:
        Information about the generated image including URL and status
    """
    if not IMAGE_GENERATION_AVAILABLE:
        return "Image generation is not available. Please install the replicate package and set REPLICATE_API_TOKEN."
    
    try:
        result = image_service.generate_experiment_image(
            experiment_topic=experiment_topic,
            prompt=custom_prompt,
            style=style
        )
        
        if result["status"] == "success":
            return f"Successfully generated image for '{experiment_topic}'. Image URL: {result['url']}. Style: {result['style']}. Local path: {result['local_path']}"
        else:
            return f"Failed to generate image for '{experiment_topic}'. Error: {result.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"Error generating image for '{experiment_topic}': {str(e)}"


@tool
def generate_multiple_experiment_images(
    experiment_topic: str,
    count: int = 3,
    styles: list = None
) -> str:
    """Generate multiple images for a physics experiment.
    
    Args:
        experiment_topic: The topic or title of the experiment
        count: Number of images to generate (default: 3)
        styles: List of styles to use (default: ['scientific', 'educational', 'diagram'])
        
    Returns:
        Information about all generated images
    """
    if not IMAGE_GENERATION_AVAILABLE:
        return "Image generation is not available. Please install the replicate package and set REPLICATE_API_TOKEN."
    
    if styles is None:
        styles = ["scientific", "educational", "diagram"]
    
    try:
        results = image_service.generate_multiple_images(
            experiment_topic=experiment_topic,
            count=count,
            styles=styles
        )
        
        successful_images = [r for r in results if r["status"] == "success"]
        failed_images = [r for r in results if r["status"] == "error"]
        
        response = f"Generated {len(successful_images)} out of {count} images for '{experiment_topic}':\n"
        
        for i, result in enumerate(successful_images, 1):
            response += f"{i}. Style: {result['style']}, URL: {result['url']}\n"
        
        if failed_images:
            response += f"\nFailed to generate {len(failed_images)} images due to errors."
        
        return response
        
    except Exception as e:
        return f"Error generating multiple images for '{experiment_topic}': {str(e)}"


def _search_with_tavily(query: str, max_results: int) -> str:
    """Fallback to Tavily if API key is available"""
    try:
        from tavily import TavilyClient
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        search_docs = tavily_client.search(
            query,
            max_results=max_results,
            include_raw_content=True,
            include_images=True,
        )
        return str(search_docs)
    except:
        return f"Search query: '{query}'. Please use general physics knowledge."


# Define sub-agents
research_sub_agent = SubAgent(
    name="research-agent",
    description="Expert educational researcher specializing in physics and Grade 9 science curriculum. Use for researching physics concepts, experiment procedures, safety guidelines, and educational resources. Call with specific, focused queries (e.g., 'Grade 9 pendulum experiment procedures and materials', 'safety guidelines for electricity experiments', 'simple explanations of Newton's laws for students').",
    prompt=RESEARCH_AGENT_PROMPT,
)

critique_sub_agent = SubAgent(
    name="critique-agent",
    description="Experienced physics teacher reviewing experiment guides for Grade 9 students. Use after creating experiment files to check for safety, accuracy, age-appropriateness, and completeness. Specify focus if needed (e.g., 'review for safety concerns', 'check if suitable for Grade 9 level').",
    prompt=CRITIQUE_AGENT_PROMPT,
)


# Create the main physics experiment agent
def create_physics_experiment_agent(model_name: str = "gpt-4o"):
    """Create a physics experiment helper agent.

    Args:
        model_name: Name of the model to use (default: gpt-4o)

    Returns:
        Configured deep agent for physics experiments
    """
    # Define tools based on availability
    tools = [internet_search]
    
    if IMAGE_GENERATION_AVAILABLE:
        tools.extend([generate_experiment_image, generate_multiple_experiment_images])
    
    agent = create_deep_agent(
        tools=tools,
        instructions=PHYSICS_EXPERIMENT_SYSTEM_PROMPT,
        subagents=[research_sub_agent, critique_sub_agent],
        model=model_name,
    ).with_config({"recursion_limit": 50})

    return agent


def run_physics_agent(experiment_request: str, model_name: str = "gpt-4o"):
    """Run the physics experiment agent with a student request.

    Args:
        experiment_request: Description of the experiment the student wants to create
        model_name: Model to use for generation

    Returns:
        Agent execution result with generated files and images
    """
    agent = create_physics_experiment_agent(model_name=model_name)

    result = agent.invoke({
        "messages": [{"role": "user", "content": experiment_request}]
    })

    # Extract images from search results if available
    images = []
    if "images" in result:
        images = result["images"]

    # Extract generated images from agent messages
    generated_images = []
    if "messages" in result:
        for message in result["messages"]:
            if hasattr(message, 'content') and isinstance(message.content, str):
                # Look for image URLs in the content
                if "Image URL:" in message.content:
                    # Extract URLs from the message content
                    lines = message.content.split('\n')
                    for line in lines:
                        if "Image URL:" in line:
                            url = line.split("Image URL:")[-1].strip()
                            if url.startswith('http'):
                                generated_images.append(url)

    # Combine all images
    all_images = images + generated_images

    # Add images to result if not already present
    if "experiment_images" not in result:
        result["experiment_images"] = all_images
    else:
        result["experiment_images"].extend(generated_images)

    return result
