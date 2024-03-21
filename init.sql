CREATE USER jopa WITH PASSWORD 'botPass';
-- Create the database and grant privileges to the user
CREATE DATABASE jopaDb;
GRANT ALL PRIVILEGES ON DATABASE jopaDb TO jopa;

