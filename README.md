# GPT magic
A Jupyter/IPython magic command for generating code using GPT

## Usage
To use the GPT-3 magic commands, users can run:

```python
%gpt "your_query_here"
```

or for a cell magic
```python 
%%gptcell
your_query_here
```

## Install

Please note that users will need to provide their own OpenAI API key. Set an environment variable called `OPEN_AI_KEY` with your key. Or pass the API key when loading the extension, by running the following line before %load_ext gpt_magic:

```python
import os
os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"
```
