#!/bin/bash
python -m venv fastapi_env
source fastapi_env/bin/activate
python -m pip install --upgrade -r requirements.txt

# source my_script.sh tells the current shell to execute the script, but it runs in the current shell rather than a subshell.