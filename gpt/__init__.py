# __init__.py

import os
from .gpt import GPTMagics

def load_ipython_extension(ipython):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable.")
    ipython.register_magics(GPTMagics(ipython, api_key))

