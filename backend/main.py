# backend/main.py
"""
Main entry point for the zero-basis-coding-agent Flask application.

Run this file to start the development server.
"""

import os
import sys

# Add the parent directory to the path so we can import the app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.config import Config


def main():
    """Run the Flask application."""
    app = create_app()

    # Run the development server
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )


if __name__ == '__main__':
    main()