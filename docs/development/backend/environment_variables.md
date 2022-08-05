# Environment Variables

The dev environment uses a combination of hardcoded and random values for these environment variables.

These environment variables will need to be set by other means if you are running this application in production.

## Database variables

These variables are used by the PostgreSQL server container to initialize the database.

- **POSTGRES_DB**: The name of the database to create. The development environment uses `ace`.
- **POSTGRES_USER**: The user to use to connect to the PostgreSQL server. The development environment uses `ace`.
- **POSTGRES_PASSWORD**: The password to use to connect to the PostgreSQL server. The development environment generates `a random 32 character string`.

## Database API variables

These variables are used by the database API application.

- **DATABASE_URL**: The connection string used to connect to the PostgreSQL server. It should be in the form of `postgresql://user:password@hostname[:port]/dbname`.
- **DEFAULT_ANALYSIS_MODE_ALERT**: The alert analysis mode to use if one is not given when creating a submission.
- **DEFAULT_ANALYSIS_MODE_DETECT**: The detect analysis mode to use if one is not given when creating a submission.
- **DEFAULT_ANALYSIS_MODE_EVENT**: The event analysis mode to use if one is not given when creating a submission.
- **DEFAULT_ANALYSIS_MODE_RESPONSE**: The response analysis mode to use if one is not given when creating a submission.
- **IN_TESTING_MODE**: If set to "yes", the API will allow access to the various test endpoints, such as for inserting alerts or resetting the database.
- **SQL_ECHO**: If set (to anything), SQLAlchemy will be configured to echo all queries to the console. You can view the queries in the Docker logs for the `ace2-ams-api` container. This is enabled by default for the development environment.

## GUI API variables

These variables are used by the GUI API application.

- **COOKIES_SAMESITE**: The `SameSite` value to use when sending cookies. The development environment uses `lax`. Defaults to `lax`.
- **COOKIES_SECURE**: True/False whether or not you want to require HTTPS when sending cookies. The development environment uses `False`. Defaults to `True`.
- **DATABASE_API_URL**: The base URL to reach the database API. The development environment uses `http://db-api/api` by default.
- **JWT_ACCESS_EXPIRE_SECONDS**: The number of seconds after which an access token will expire. The development environment uses `900` (15 minutes) by default.
- **JWT_ALGORITHM**: Sets the algorithm to use for signing the tokens. The development environment uses `HS256` by default.
- **JWT_REFRESH_EXPIRE_SECONDS**: The number of seconds after which a refresh token will expire. The development environment uses `43200` (12 hours) by default.
- **JWT_SECRET**: The secret key/password to use when signing and decoding tokens. The development environment generates `a random 32 character string`.

## GUI variables

These variables are used by the Vue.js frontend application.

- **VITE_BACKEND_URL**: This sets the base URL to reach the GUI API.
- **VITE_TESTING_MODE**: If set to "yes", this will instruct the application to load the static test config instead of the regular production config.
