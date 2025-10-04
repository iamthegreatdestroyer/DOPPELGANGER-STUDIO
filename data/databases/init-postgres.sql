-- DOPPELGANGER STUDIO - PostgreSQL Database Schema
-- Initial schema for relational data storage

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =======================
-- SHOWS & RESEARCH
-- =======================

CREATE TABLE shows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    original_air_date_start DATE,
    original_air_date_end DATE,
    genre VARCHAR(100),
    network VARCHAR(100),
    total_episodes INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB,
    UNIQUE(title)
);

CREATE INDEX idx_shows_title ON shows USING gin(title gin_trgm_ops);

-- =======================
-- CHARACTERS
-- =======================

CREATE TABLE characters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    show_id UUID REFERENCES shows(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    personality_traits JSONB,
    relationships JSONB,
    signature_behaviors JSONB,
    catchphrases TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_characters_show_id ON characters(show_id);
CREATE INDEX idx_characters_name ON characters USING gin(name gin_trgm_ops);

-- =======================
-- DOPPELGANGER PROJECTS
-- =======================

CREATE TABLE doppelganger_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_show_id UUID REFERENCES shows(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    new_setting_type VARCHAR(100) NOT NULL, -- space, medieval, underwater, etc.
    new_setting_year INTEGER,
    new_setting_location VARCHAR(255),
    new_setting_description TEXT,
    status VARCHAR(50) DEFAULT 'planning', -- planning, in_progress, completed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX idx_doppelganger_projects_show ON doppelganger_projects(source_show_id);
CREATE INDEX idx_doppelganger_projects_status ON doppelganger_projects(status);

-- =======================
-- TRANSFORMED CHARACTERS
-- =======================

CREATE TABLE transformed_characters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES doppelganger_projects(id) ON DELETE CASCADE,
    original_character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    new_name VARCHAR(255) NOT NULL,
    new_form VARCHAR(255), -- human, alien, robot, etc.
    preserved_traits JSONB,
    adaptations JSONB,
    visual_description TEXT,
    voice_profile JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_transformed_characters_project ON transformed_characters(project_id);
CREATE INDEX idx_transformed_characters_original ON transformed_characters(original_character_id);

-- =======================
-- EPISODES & SCRIPTS
-- =======================

CREATE TABLE episodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES doppelganger_projects(id) ON DELETE CASCADE,
    episode_number INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    synopsis TEXT,
    script TEXT,
    duration_seconds INTEGER,
    status VARCHAR(50) DEFAULT 'draft', -- draft, scripted, animated, completed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX idx_episodes_project ON episodes(project_id);
CREATE INDEX idx_episodes_status ON episodes(status);

-- =======================
-- ASSETS
-- =======================

CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_type VARCHAR(50) NOT NULL, -- video, audio, font
    source VARCHAR(100) NOT NULL,
    source_url TEXT,
    local_path TEXT,
    title VARCHAR(255),
    tags TEXT[],
    quality_score DECIMAL(3,2),
    perceptual_hash VARCHAR(64),
    file_size_bytes BIGINT,
    duration_seconds DECIMAL(10,2),
    resolution VARCHAR(20),
    bitrate INTEGER,
    metadata JSONB,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_assets_type ON assets(asset_type);
CREATE INDEX idx_assets_source ON assets(source);
CREATE INDEX idx_assets_tags ON assets USING gin(tags);
CREATE INDEX idx_assets_perceptual_hash ON assets(perceptual_hash);
CREATE INDEX idx_assets_quality ON assets(quality_score DESC);

-- =======================
-- ASSET USAGE TRACKING
-- =======================

CREATE TABLE asset_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
    episode_id UUID REFERENCES episodes(id) ON DELETE CASCADE,
    usage_type VARCHAR(50), -- background, character, sound_effect, music
    start_time_seconds DECIMAL(10,2),
    duration_seconds DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_asset_usage_asset ON asset_usage(asset_id);
CREATE INDEX idx_asset_usage_episode ON asset_usage(episode_id);

-- =======================
-- RENDER JOBS
-- =======================

CREATE TABLE render_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    episode_id UUID REFERENCES episodes(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'queued', -- queued, processing, completed, failed
    progress_percent INTEGER DEFAULT 0,
    output_path TEXT,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX idx_render_jobs_episode ON render_jobs(episode_id);
CREATE INDEX idx_render_jobs_status ON render_jobs(status);

-- =======================
-- USER FEEDBACK
-- =======================

CREATE TABLE user_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    episode_id UUID REFERENCES episodes(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    feedback_type VARCHAR(50), -- quality, humor, accuracy, etc.
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_feedback_episode ON user_feedback(episode_id);
CREATE INDEX idx_user_feedback_rating ON user_feedback(rating);

-- =======================
-- AI GENERATIONS LOG
-- =======================

CREATE TABLE ai_generations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    generation_type VARCHAR(100) NOT NULL, -- character, script, dialogue, description
    model VARCHAR(100) NOT NULL, -- claude-sonnet-4.5, gpt-4, etc.
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    tokens_used INTEGER,
    cost_usd DECIMAL(10,4),
    quality_rating INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX idx_ai_generations_type ON ai_generations(generation_type);
CREATE INDEX idx_ai_generations_model ON ai_generations(model);
CREATE INDEX idx_ai_generations_created ON ai_generations(created_at DESC);

-- =======================
-- FUNCTIONS & TRIGGERS
-- =======================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables with updated_at
CREATE TRIGGER update_shows_updated_at BEFORE UPDATE ON shows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_characters_updated_at BEFORE UPDATE ON characters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_doppelganger_projects_updated_at BEFORE UPDATE ON doppelganger_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transformed_characters_updated_at BEFORE UPDATE ON transformed_characters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_episodes_updated_at BEFORE UPDATE ON episodes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assets_updated_at BEFORE UPDATE ON assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =======================
-- INITIAL DATA
-- =======================

-- Insert sample show for testing
INSERT INTO shows (title, genre, network, metadata) VALUES
    ('Test Show', 'Comedy', 'Test Network', '{"sample": true}');

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO doppelganger;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO doppelganger;
