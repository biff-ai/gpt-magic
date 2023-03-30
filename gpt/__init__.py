# __init__.py

import os
from .gpt import GPTMagics
import requests

def check_api_key(api_key):
    """
    This function checks the api_key is valid before loading the extension.
    """
    url = 'https://api.openai.com/v1/engines'
    headers = {'Authorization': f'Bearer {api_key}'}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

def load_ipython_extension(ipython):
    """
    This function is called when the extension is loaded.

    It accepts an IPython InteractiveShell instance.

    Parameters:
        ipython (InteractiveShell): The IPython shell for the current session.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable.")
    else:
        check_api_key(api_key)
    
    ipython.register_magics(GPTMagics(ipython, api_key))



