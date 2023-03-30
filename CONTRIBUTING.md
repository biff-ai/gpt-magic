
## Contributing to GPT-Magic

Thank you for your interest in contributing to GPT-Magic! Before you begin writing code, please read through this document. 
First, it is important that you share your intention to contribute, based on the type of contribution.

Please first search through GPT-Magic [issues](https://github.com/biff-ai/gpt-magic/issues). If the feature is not listed, please create a new issue. 
If you would like to work on any existing issue, please comment and assign yourself to the issue and file a pull request.

This document covers some of the technical aspects of contributing to Babbab.

## Developing GPT-Magic & Set-up

To develop Babbab on your machine, you can follow the set-up instructions. 

### Prerequisites

Python >= 3.6

### Set-up

First clone the repo:

```git clone https://github.com/biff-ai/gpt-magic.git```

Next open the repo and install dependencies in the dev environment:

```cd gpt-magic && pip install -e .[dev]```

### Codebase structure
GPT-magic currently has one file where the magic happens
* gpt.py

### Unit testing

Unit tests use `pytest`.
You will need to create a `.env` file in the root directory containing the following for the unit tests to run:
`OPENAI_API_TOKEN=<your api token>`

This will only run basic health and validation checks (e.g. your token is valid), but will not execute in any queries that cost $. 

### Linting

There is currently no linter.

### Writing documentation

Please make sure you add documentation to your functions. Please use [Google Style docstrings](https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html).
