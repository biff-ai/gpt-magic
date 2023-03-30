# GPT magic
A Jupyter/IPython magic command for generating code using GPT

## Example
Generating code with GPT by loading the extension and prefixing your line with `%gpt`.

![Alt text](GPTMagic.gif)

## Install

Install with pip
```python
pip install gpt-magic
````

Please note that users will need to provide their own OpenAI API key. Set an environment variable called `OPEN_AI_KEY` with your key. Or pass the API key when loading the extension, by running the following line before %load_ext gpt_magic:

```python
import os
os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"
```

## Usage
```python
%load_ext gpt
%gpt "Your request here"
```

## Model

The current default is the gpt-3-turbo model, but can be changed using `OPENAI_MODEL` environmental variable. 

Using GPT-4 example
```python
import os
os.environ["OPENAI_MODEL"] = "gpt-4"
```

## Arguments

### Chat

You can enable memory of all previous requests and responses with the `-c` argument. By default it's memory-less.

```python
%gpt -c "Write a function which calculates the average of a numpy array"
```

### Temperature

You can set the temperature with `-t` argument. The default is 0.

```python

%gpt -t 0.5  "Write a function which calculates the average of a numpy array"
```

