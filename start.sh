#!/bin/bash

pip install -r requirements.txt &
npm run dev & # Start frontend on port 3000
/nix/store/bry6rrr5m76ygwfjnwjf9c1k6xfw7gsy-python3-wrapper/bin/python backend/app.py # Start backend on port 5000