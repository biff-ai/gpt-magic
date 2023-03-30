# tests/test_gpt.py

import pytest
import os
from dotenv import load_dotenv
from requests_mock import Mocker
from requests.exceptions import HTTPError

from gpt import load_ipython_extension, GPTMagics, check_api_key

#Test calls with a mocker
def test_valid_api_key():
    api_key = 'VALID_API_KEY'

    with Mocker() as mock:
        # Mock the response from the API
        mock.get('https://api.openai.com/v1/engines', status_code=200)

        # Call the function with a valid API key
        check_api_key(api_key)

        # Ensure that the API was called with the correct headers
        assert mock.last_request.headers['Authorization'] == f'Bearer {api_key}'

def test_invalid_api_key():
    api_key = 'INVALID_API_KEY'

    with Mocker() as mock:
        # Mock the response from the API
        mock.get('https://api.openai.com/v1/engines', status_code=401)

        # Call the function with an invalid API key
        with pytest.raises(HTTPError):
            check_api_key(api_key)

        # Ensure that the API was called with the correct headers
        assert mock.last_request.headers['Authorization'] == f'Bearer {api_key}'


def test_load_ipython_extension(ip):
    load_dotenv()
    # Set the OPENAI_API_KEY environment variable
    api_key=os.environ['OPENAI_API_KEY']

    # Call the function with the parent object
    load_ipython_extension(ip)

    # Ensure ip is not None
    assert ip is not None
    
