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

from IPython.display import display, Javascript
import base64
import re

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
        self.prefix_system = 'Ignore previous directions. Imagine you are one of the foremost experts on python development. Only respond with a brief explanation and python code block.'
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
        
        extract = extract_code_and_text(feedback['content'])

        cells = process_cells(extract)

        if environment() == 'jupyter':
            return ipynotebook(extract)
        elif environment() == 'jupyter-lab':
            return jupyterlab(extract)
        else:
            raise ValueError(f"Unsupported environment: {program}. Must be run in Jupyter-lab or Jupyter notebook")

        
    
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


def insert_cells_ahead(cells_data, n=0):
    for i, (cell_type, content) in reversed(list(enumerate(cells_data))):
        content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        display(Javascript('''
            function insert_cells() {
                var current_cell_index = Jupyter.notebook.get_cells().indexOf(Jupyter.notebook.get_selected_cell());
                var new_cell = Jupyter.notebook.insert_cell_at_index("''' + cell_type + '''", current_cell_index + ''' + str(n) + ''');
                new_cell.set_text(atob("''' + content_b64 + '''"));
                if("''' + cell_type + '''" === "markdown"){
                    new_cell.render();
                }
                if(''' + str(i) + ''' === 0){
                    new_cell.focus_cell();
                }
            }
            setTimeout(insert_cells, 100);
        '''))

def create_new_cell(contents, cell_type='Code'):
    if cell_type not in ['code', 'markdown']:
        raise ValueError("Invalid cell_type. Choose 'code' or 'markdown'.")

    from IPython.core.getipython import get_ipython
    shell = get_ipython()
    payload = dict(
        source='set_next_input',
        text=contents,
        replace=False,
        cell_type=cell_type,
    )
    shell.payload_manager.write_payload(payload, single=False)

def jupyterlab(extract):
    for i,j in enumerate(extract[:2]):
        if i==0 and j[0]=='markdown':
            display(Markdown(j[1]))
        else:
            create_new_cell(j[1],j[0])

def ipynotebook(extract):
    return insert_cells_ahead(extract)

def environment():
    env = os.environ
    shell = 'shell'
    program = os.path.basename(env['_'])
    return program

def extract_code_and_text(response):
    result = []
    code_start = "```"
    code_end = "```"
    in_code_block = False
    buffer = ""
    code_buffer = ""
    language = ""

    while response:
        if not in_code_block and response.startswith(code_start):
            in_code_block = True
            response = response[len(code_start):]
            language_end = response.find("\n")
            language = response[:language_end].strip()
            response = response[language_end:]
            buffer = buffer.strip()
            if buffer:
                result.append(("markdown", buffer))
                buffer = ""
        elif in_code_block and response.startswith(code_end):
            in_code_block = False
            response = response[len(code_end):]
            code_buffer = code_buffer.strip()
            if code_buffer:
                result.append(("code", code_buffer))
                code_buffer = ""
        else:
            char = response[0]
            response = response[1:]
            if in_code_block:
                code_buffer += char
            else:
                buffer += char

    # Append the remaining text outside of the code blocks
    buffer = buffer.strip()
    if buffer:
        result.append(("markdown", buffer))

    return result

def process_cells(parsed_output):
    cells = []

    for i,j in parsed_output:
        if i == 'text':
            cells.append(('markdown',j))
        if i == 'code':
            cells.append(('code',j))
    cells = cells[::-1]
    return 
