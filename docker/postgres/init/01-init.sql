-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE pcm_startlist TO pcm_user;

-- Create indexes for better performance
-- These will be created after tables are created by the app
