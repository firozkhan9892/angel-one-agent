#!/usr/bin/env python
"""
Simple wrapper to run the agent from root directory
"""
import sys
import os

# Add angel_agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'angel_agent'))

# Now run the agent
if __name__ == '__main__':
    from agent import main
    main()
