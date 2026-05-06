"""Vercel serverless entrypoint — re-exports the FastAPI app."""
import sys
import os

# Ensure project root is on sys.path so `app.*` imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: E402, F401
