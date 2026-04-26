#!/bin/bash
CURRENT_USER=$(whoami)
python3 /home/$CURRENT_USER/git/datatool/mp.py $1
