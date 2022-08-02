# Create the database
echo "SELECT 'CREATE DATABASE ${POSTGRES_DB:-ace}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB:-ace}')\gexec" | psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER"

# Enable the required extensions
# The btree_gist extension is needed for the Analysis table ExcludeConstraint functionality since UUID cannot work with gist.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d ${POSTGRES_DB:-ace} -c "CREATE EXTENSION IF NOT EXISTS btree_gist"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d ${POSTGRES_DB:-ace} -c "CREATE EXTENSION IF NOT EXISTS pg_trgm"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d ${POSTGRES_DB:-ace} -c "CREATE EXTENSION IF NOT EXISTS pgcrypto"
