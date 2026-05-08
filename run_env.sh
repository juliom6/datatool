#!/bin/bash
CURRENT_USER=$(whoami)
echo $CURRENT_USER
source /home/julio/git/datatool/.venv/bin/activate
python3 /home/julio/git/datatool/mp.py $1
