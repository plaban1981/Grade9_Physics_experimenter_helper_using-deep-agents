"""FastAPI server for Physics Experiment Helper."""

import sys
import os
import asyncio
import json
from typing import Dict, Optional, List
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import zipfile
import io
import markdown
from io import BytesIO

from agent.physics_agent import run_physics_agent
from api.export_utils import create_zip_archive, create_complete_html_report

# Import image generation service
try:
    from api.image_generation import image_service
    IMAGE_GENERATION_AVAILABLE = True
except ImportError:
    IMAGE_GENERATION_AVAILABLE = False

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Physics Experiment Helper API",
    description="AI-powered physics experiment generator for Grade 9 students",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent.parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Store active sessions
sessions: Dict[str, dict] = {}


class ExperimentRequest(BaseModel):
    """Request model for experiment generation."""
    experiment_description: str
    student_name: Optional[str] = None
    grade_level: str = "Grade 9"
    model_name: str = "gpt-4o"
    session_id: Optional[str] = None


class ExperimentResponse(BaseModel):
    """Response model for experiment generation."""
    session_id: str
    status: str
    message: str
    files: Dict[str, str]
    todos: list


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML interface."""
    index_path = static_path / "index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "physics-experiment-helper",
        "message": "Ready to help with physics experiments!"
    }


@app.post("/api/generate-experiment", response_model=ExperimentResponse)
async def generate_experiment(request: ExperimentRequest):
    """Generate a complete physics experiment guide.

    Args:
        request: Experiment generation request

    Returns:
        Complete experiment documentation files
    """
    try:
        # Run the agent
        result = await asyncio.to_thread(
            run_physics_agent,
            request.experiment_description,
            request.model_name
        )

        # Extract results
        files = result.get("files", {})
        todos = result.get("todos", [])
        messages = result.get("messages", [])
        images = result.get("experiment_images", [])

        # Generate session ID
        session_id = request.session_id or f"exp_{len(sessions) + 1}"

        # Store session
        sessions[session_id] = {
            "files": files,
            "todos": todos,
            "images": images,
            "messages": [str(msg) for msg in messages],
            "request": request.dict()
        }

        return ExperimentResponse(
            session_id=session_id,
            status="completed",
            message=f"Successfully generated experiment guide with {len(files)} files",
            files=files,
            todos=todos
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating experiment: {str(e)}")


@app.websocket("/ws/generate-experiment")
async def websocket_generate_experiment(websocket: WebSocket):
    """WebSocket endpoint for streaming experiment generation."""
    await websocket.accept()

    try:
        while True:
            # Receive request
            data = await websocket.receive_text()
            request_data = json.loads(data)

            experiment_description = request_data.get("experiment_description")
            model_name = request_data.get("model_name", "gpt-4o")
            session_id = request_data.get("session_id", f"ws_exp_{id(websocket)}")

            if not experiment_description:
                await websocket.send_json({
                    "type": "error",
                    "message": "Experiment description is required"
                })
                continue

            # Send acknowledgment
            await websocket.send_json({
                "type": "status",
                "message": "Starting experiment generation...",
                "session_id": session_id
            })

            try:
                # Run agent
                result = await asyncio.to_thread(
                    run_physics_agent,
                    experiment_description,
                    model_name
                )

                files = result.get("files", {})
                todos = result.get("todos", [])
                images = result.get("experiment_images", [])

                # Send image updates
                if images:
                    await websocket.send_json({
                        "type": "images_update",
                        "images": images
                    })

                # Send file updates
                for filename, content in files.items():
                    await websocket.send_json({
                        "type": "file_update",
                        "filename": filename,
                        "content": content,
                        "preview": content[:500] + "..." if len(content) > 500 else content
                    })

                # Send TODO updates
                await websocket.send_json({
                    "type": "todos_update",
                    "todos": todos
                })

                # Send completion
                await websocket.send_json({
                    "type": "completion",
                    "message": f"Experiment guide complete! Generated {len(files)} files and {len(images)} images.",
                    "session_id": session_id,
                    "files": files,
                    "todos": todos,
                    "images": images
                })

                # Store session
                sessions[session_id] = {
                    "files": files,
                    "todos": todos,
                    "images": images,
                    "messages": [str(msg) for msg in result.get("messages", [])],
                    "request": request_data
                }

            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error during generation: {str(e)}"
                })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"WebSocket error: {str(e)}"
            })
        except:
            pass


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Retrieve session data by ID."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return sessions[session_id]


@app.get("/api/sessions/{session_id}/files")
async def get_session_files(session_id: str):
    """Get all files from a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return sessions[session_id].get("files", {})


@app.get("/api/sessions/{session_id}/files/{filename}")
async def get_session_file(session_id: str, filename: str):
    """Get a specific file from a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    files = sessions[session_id].get("files", {})
    if filename not in files:
        raise HTTPException(status_code=404, detail="File not found")

    return {
        "filename": filename,
        "content": files[filename],
        "session_id": session_id
    }


@app.get("/api/sessions/{session_id}/download/{filename}")
async def download_file(session_id: str, filename: str):
    """Download a specific file."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    files = sessions[session_id].get("files", {})
    if filename not in files:
        raise HTTPException(status_code=404, detail="File not found")

    # Create temporary file
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    file_path = temp_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(files[filename])

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="text/markdown"
    )


@app.get("/api/experiment-examples")
async def get_experiment_examples():
    """Get example experiment topics for inspiration."""
    examples = [
        {
            "title": "Simple Pendulum Period",
            "description": "Investigate how the length of a pendulum affects its period of oscillation",
            "category": "Mechanics",
            "difficulty": "Beginner"
        },
        {
            "title": "Projectile Motion",
            "description": "Study the trajectory of projectiles launched at different angles",
            "category": "Mechanics",
            "difficulty": "Intermediate"
        },
        {
            "title": "Friction on Different Surfaces",
            "description": "Compare the coefficient of friction for various surface materials",
            "category": "Mechanics",
            "difficulty": "Beginner"
        },
        {
            "title": "Ohm's Law Verification",
            "description": "Verify the relationship between voltage, current, and resistance",
            "category": "Electricity",
            "difficulty": "Intermediate"
        },
        {
            "title": "Heat Transfer and Insulation",
            "description": "Test the insulating properties of different materials",
            "category": "Thermal Physics",
            "difficulty": "Beginner"
        },
        {
            "title": "Sound Frequency and Pitch",
            "description": "Explore the relationship between frequency and perceived pitch",
            "category": "Waves",
            "difficulty": "Intermediate"
        },
        {
            "title": "Mirror Reflection Angles",
            "description": "Verify the law of reflection using plane mirrors",
            "category": "Optics",
            "difficulty": "Beginner"
        },
        {
            "title": "Lens Focal Length",
            "description": "Determine the focal length of convex and concave lenses",
            "category": "Optics",
            "difficulty": "Intermediate"
        }
    ]
    return {"examples": examples}


@app.get("/api/sessions/{session_id}/images")
async def get_session_images(session_id: str):
    """Get all images from a session.

    Args:
        session_id: Session identifier

    Returns:
        List of image URLs
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"images": sessions[session_id].get("images", [])}


@app.get("/api/sessions/{session_id}/download-zip")
async def download_zip(session_id: str):
    """Download all experiment files as a ZIP archive.

    Args:
        session_id: Session identifier

    Returns:
        ZIP file containing all experiment files
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    files = session.get("files", {})
    images = session.get("images", [])

    # Create ZIP archive
    zip_buffer = create_zip_archive(files, images, session_id)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=physics_experiment_{session_id}.zip"
        }
    )


@app.get("/api/sessions/{session_id}/download-html")
async def download_html_report(session_id: str):
    """Download complete experiment as a single HTML file.

    Args:
        session_id: Session identifier

    Returns:
        HTML file with all experiment content
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    files = session.get("files", {})
    images = session.get("images", [])

    # Create HTML report
    html_content = create_complete_html_report(files, images, session_id)

    # Create temporary file
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    html_path = temp_dir / f"experiment_report_{session_id}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return FileResponse(
        path=str(html_path),
        filename=f"physics_experiment_{session_id}.html",
        media_type="text/html"
    )


class ImageGenerationRequest(BaseModel):
    """Request model for image generation."""
    experiment_topic: str
    style: str = "scientific"
    custom_prompt: Optional[str] = None


class ImageGenerationResponse(BaseModel):
    """Response model for image generation."""
    success: bool
    image_url: Optional[str] = None
    local_path: Optional[str] = None
    message: str
    experiment_topic: str
    style: str


@app.post("/api/generate-image", response_model=ImageGenerationResponse)
async def generate_experiment_image(request: ImageGenerationRequest):
    """Generate an image for a physics experiment.

    Args:
        request: Image generation request

    Returns:
        Generated image information
    """
    if not IMAGE_GENERATION_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Image generation service not available. Please install replicate package and set REPLICATE_API_TOKEN."
        )

    try:
        result = image_service.generate_experiment_image(
            experiment_topic=request.experiment_topic,
            prompt=request.custom_prompt,
            style=request.style
        )

        if result["status"] == "success":
            return ImageGenerationResponse(
                success=True,
                image_url=result["url"],
                local_path=result["local_path"],
                message=f"Successfully generated {request.style} image for '{request.experiment_topic}'",
                experiment_topic=request.experiment_topic,
                style=request.style
            )
        else:
            return ImageGenerationResponse(
                success=False,
                message=f"Failed to generate image: {result.get('error', 'Unknown error')}",
                experiment_topic=request.experiment_topic,
                style=request.style
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating image: {str(e)}")


@app.post("/api/generate-multiple-images")
async def generate_multiple_experiment_images(
    experiment_topic: str,
    count: int = 3,
    styles: List[str] = None
):
    """Generate multiple images for a physics experiment.

    Args:
        experiment_topic: The topic of the experiment
        count: Number of images to generate
        styles: List of styles to use

    Returns:
        List of generated images
    """
    if not IMAGE_GENERATION_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Image generation service not available. Please install replicate package and set REPLICATE_API_TOKEN."
        )

    if styles is None:
        styles = ["scientific", "educational", "diagram"]

    try:
        results = image_service.generate_multiple_images(
            experiment_topic=experiment_topic,
            count=count,
            styles=styles
        )

        return {
            "success": True,
            "experiment_topic": experiment_topic,
            "generated_count": len([r for r in results if r["status"] == "success"]),
            "total_requested": count,
            "images": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating images: {str(e)}")


@app.get("/api/sessions/{session_id}/images/{image_index}")
async def get_session_image(session_id: str, image_index: int):
    """Get a specific image from a session.

    Args:
        session_id: Session identifier
        image_index: Index of the image (0-based)

    Returns:
        Image file
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    images = sessions[session_id].get("images", [])
    if image_index >= len(images):
        raise HTTPException(status_code=404, detail="Image not found")

    image_url = images[image_index]
    
    try:
        # Download the image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Return the image
        return StreamingResponse(
            io.BytesIO(response.content),
            media_type="image/jpeg",
            headers={"Content-Disposition": f"inline; filename=image_{image_index}.jpg"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading image: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("🔬 Physics Experiment Helper - Starting Server")
    print("=" * 70)
    print("\nAccess the application at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
