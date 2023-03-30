#gpt.py

import os
import openai
import requests
import json
import argparse
from IPython.display import display, Markdown
from IPython.core.magic import line_cell_magic, magics_class, Magics
from IPython.core.getipython import get_ipython
from typing import Optional, Tuple

MODEL_STRING = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

@magics_class
class GPTMagics(Magics):
    """
    A set of magics useful for interacting with OpenAI's GPT-3 API.

    You can ask GPT a query. This to be returned in a JSON with explanation and code keys.
    The explanation is then displayed in markdown, and the code is returned in the cell below.
    
    Attributes:
        api_key (str): The API key for the OpenAI API.
        prefix_system (str): The system message prefix to use when sending queries to the API.
        prefix_user (str): The user message prefix to use when sending queries to the API.
        model (str): The OpenAI GPT model to use for generating responses.
        temperature (float): The temperature for generating responses from the API.
        current_query (str): The current query that the user is working on.
    """
    
    def __init__(self, shell, api_key=None):
        """
        Initializes a GPTMagics instance with the specified IPython shell and optional API key.
        
        Args:
            shell (InteractiveShell): The IPython shell for the current session.
            api_key (str, optional): The API key for the OpenAI API. Defaults to None.
        """

        super().__init__(shell)
        self.api_key = api_key or os.environ['OPENAI_API_KEY']
        openai.api_key = self.api_key
        self.prefix_system = 'Ignore previous directions. Imagine you are one of the foremost experts on python development. Respond ONLY with a valid json object (correctly escaped) with one key called "explanation" with a markdown formatted description of what the code does and another with only the code called "code". All code should be written in the code part of the JSON. None should be outside.'
        self.prefix_user = 'Now please '
        self.model = MODEL_STRING
        self.temperature = 0
        
        #This variable is here to store the full chat log.
        self.current_query = None
    
    ## A chat initialisation if none exists.
    def init_chat(self, query: str) -> list:
        """
        Initializes a chat if none exists.

        Args:
            query (str): The user's query to start the chat.

        Returns:
            list: A list of dictionaries representing the initial chat messages.
        """
        current_chat = [{"role": "system", "content": f"{self.prefix_system}"},\
                     {"role": "user", "content": f"{self.prefix_user} {query}"}]
        return current_chat
    
    #This method initialises a chat (using function above), if no previous chat exists, otherwise it continues the chat.
    def cont_chat(self, query: str, current_chat: Optional[list] = None) -> list:
        """
        Initializes a chat (using the `init_chat` function) if no previous chat exists,
        otherwise continues the chat.

        Args:
            query (str): The user's query to continue the chat.
            current_chat (list, optional): The current chat log. Defaults to None.

        Returns:
            list: An updated list of dictionaries representing the chat messages.
        """
        if current_chat:
            message = {"role": "user", "content": f"{query}"}
            current_chat.append(message)
            return current_chat
        else:
            return self.init_chat(query)
    
    def extract_json_object(self, s: str) -> Optional[str]:
        """
        Extracts the first JSON object from a given string.

        Args:
            s (str): The input string to search for a JSON object.

        Returns:
            Optional[str]: The extracted JSON object as a string, or None if not found.
        """
        open_braces = 0
        start = -1
        end = -1

        for i, c in enumerate(s):
            if c == '{':
                if start == -1:
                    start = i
                open_braces += 1
            elif c == '}':
                open_braces -= 1
                if open_braces == 0:
                    end = i + 1
                    break

        if start != -1 and end != -1:
            return s[start:end]
        else:
            return None

    def parse_response(self, response_content: str, execute_code: bool = False) -> Tuple[str, str]:
        """
        Parses the response from the OpenAI API, extracts the explanation and code, 
        and inserts the generated code into a new code cell.

        Args:
            response_content (str): The JSON-formatted response content from the GPT-3 API.
            execute_code (bool, optional): Whether to execute the generated code. Defaults to False.

        Returns:
            Tuple[str, str]: A tuple containing the explanation and the code.

        Raises:
            JSONDecodeError: If the response content cannot be decoded.
        """
        try:
            response = json.loads(response_content)
            explanation = response['explanation']
            code = response['code']

            # Create a new code cell with the generated code
            ipython = get_ipython()
            ipython.set_next_input(code, replace=False)
            
            if execute_code:
                ipython.run_cell(code)

            return explanation, code
        except json.JSONDecodeError:
            print(f"Failed to decode: {response_content}")
            
    def call_openai(self, data: dict) -> dict:
        """
        Sends a request to the OpenAI API with the given data.

        Args:
            data (dict): The data to be sent as a JSON payload to the OpenAI API.

        Returns:
            dict: The JSON-formatted response from the OpenAI API.

        Raises:
            Exception: If the API returns a non-200 status code.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        resp=requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        
        if resp.status_code == 200:
            return json.loads(resp.text)
        else:
            raise Exception(f"Error: {resp.status_code}, {resp.text}")
        
    def prepare_payload(self, current_query: list) -> dict:
        """
        Prepares the payload to be sent to the OpenAI API.

        Args:
            current_query (list): The current chat log.

        Returns:
            dict: A dictionary containing the prepared payload data.
        """
        payload_data = {
        'model': self.model,
        'temperature': self.temperature,
        'messages': current_query
        }
        return payload_data
    
    def run(self, query: str, chat_memory: bool = False) -> None:
        """
        Assembles the payload, runs the OpenAI API request and processes the response.

        Args:
            query (str): The user's query to send to the GPT-3 API.
            chat_memory (bool, optional): Whether to include chat memory. Defaults to False.
        """
        #Includes the chat memory if set to true (if argument is included).
        if not chat_memory:
            self.current_query = None
        
        #Prepare chat
        self.current_query = self.cont_chat(query=query, current_chat=self.current_query)
        
        #Prepare data payload
        data = self.prepare_payload(self.current_query)
        
        response = self.call_openai(data)
        feedback = response['choices'][0]['message']
        
        self.current_query.append(feedback)
        json_response = self.extract_json_object(feedback['content'])
        exp,code = self.parse_response(json_response)
        display(Markdown(exp))
        
    
    @line_cell_magic
    def gpt(self, line: str, cell: Optional[str] = None) -> None:
        """
        IPython magic function that processes user input and runs the OPENAI API request.

        Args:
            line (str): The line input provided by the user.
            cell (str, optional): The cell input provided by the user. Defaults to None.
        """

        # Create an argument parser for processing command-line options
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", action="store_true")
        parser.add_argument("-t", type=float, default=0)
        parser.add_argument("query", nargs=argparse.REMAINDER)
        args = parser.parse_args(line.split())
        
        # Determine whether chat memory should be enabled
        chat_memory = args.c
        
        # Combine the remainder of the arguments into a single query string
        query = " ".join(args.query)
        
        # Set the temperature if it's within the valid range (0 <= t <= 1)
        if 0 <= args.t <= 1:
            self.temperature = args.t
        else:
            raise ValueError("Temperature must be between 0 and 1.")
        
        # Run the OpenAI API request with the provided query and chat memory option
        self.run(query, chat_memory)
