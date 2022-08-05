#!/usr/bin/env bash

# Stop any running version of the GUI
bin/stop-dev-gui.sh

cd frontend/
./test-e2e.sh