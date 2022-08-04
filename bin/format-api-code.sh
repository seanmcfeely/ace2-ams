#!/usr/bin/env bash

cd db/app
black db/crud
black db/schemas
cd ..

cd db_api/app
black .
cd ..

cd gui_api/app
black .