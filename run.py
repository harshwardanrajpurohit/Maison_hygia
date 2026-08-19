"""
Maison Hygia — Ritual Intelligence Prototype
Run this file to start both the backend API and serve the frontend.

Usage:
    python run.py

Then open http://localhost:8000 in your browser.
"""
import sys
import os

# Add parent directory to path so backend package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

if __name__ == "__main__":
    print("\n")
    print("  --- * ---")
    print("  MAISON HYGIA")
    print("  Ritual Intelligence")
    print("  --- * ---")
    print()
    print("  Starting server at http://localhost:8000")
    print("  Press Ctrl+C to stop")
    print()
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
