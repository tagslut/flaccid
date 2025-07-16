#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main entry point for the flaccid CLI.
"""

import sys

def run():
    """
Run the flaccid CLI application.
    """
    try:
        from flaccid.cli.__init__ import main
        return main()
    except ImportError as e:
        print(f"Error importing flaccid: {e}")
        print("Make sure flaccid is installed correctly.")
        return 1
    except Exception as e:
        print(f"Error running flaccid: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run())
