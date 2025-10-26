"""Convenience script to run the Physics Experiment Helper server."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

if __name__ == "__main__":
    import uvicorn
    from api.main import app

    print("=" * 70)
    print("🔬 Physics Experiment Helper - Starting Server")
    print("=" * 70)
    print("\n📚 Grade 9 Physics Experiment Guide Generator")
    print("\nAccess the application at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
