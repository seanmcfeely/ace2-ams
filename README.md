# ACE2 Alert Management System - GUI
The ACE2 Alert Management System (AMS) is comprised of three main components: a PostgreSQL database, a FastAPI backend, and a Vue.js frontend.

## Documentation
The GUI project's documentation is available at https://ace-ecosystem.github.io/ace2-ams-gui/.

## Project setup for development
The included `docker-compose.yml` file runs the Vue.js GUI application in development mode. This uses volumes to your local source code directory so the Vue.js application hot-reloads when you make a change:
```
docker-compose build
docker-compose up
```

To get full functionality out of the GUI application, you will also want to ensure you are running the FastAPI backend, which can be found at https://github.com/ace-ecosystem/ace2-ams-api.

Within your cloned `ace2-ams-api` repository, you can build the development environment by running:
```
bin/reset-dev-container.sh
```

This script will generate random passwords for the database user and the secret key used for JWTs. If you need to access these, you can view them in the `$HOME/.ace2.env` file, which configures the environment variables that will be loaded into the database container.

Once the both the frontend and backend development environments are built and started, you can access the components:

* Frontend: http://localhost:9999
* Backend API Swagger documentation: http://localhost:8888/docs
* Backend API ReDoc documentation: http://localhost:8888/redoc