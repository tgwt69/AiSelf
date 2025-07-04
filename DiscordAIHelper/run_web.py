#!/usr/bin/env python3
"""
Simple web server launcher for Discord AI Selfbot dashboard
"""

import os
import sys
import logging
from web_interface import run_web_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Main function to start the web server"""
    try:
        print("Starting Discord AI Selfbot Web Dashboard...")
        print("Access the dashboard at: http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        
        # Run the web server
        run_web_server(host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\nShutting down web server...")
    except Exception as e:
        print(f"Error starting web server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()