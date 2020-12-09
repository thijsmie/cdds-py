#!/bin/bash

make clean && make html
PORT="$(shuf -i 2000-65000 -n 1)"
python -c "import time;import webbrowser;time.sleep(0.3);webbrowser.open('http://localhost:$PORT');" &
cd _build/html && python -m http.server $PORT