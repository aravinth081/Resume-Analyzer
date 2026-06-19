-- ═══════════════════════════════════════════════════════════
-- AI Resume Intelligence SaaS Platform — Database Schema
-- PostgreSQL 16+
-- ═══════════════════════════════════════════════════════════

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Tenants (Organizations) ──
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tenants_slug ON tenants(slug);

-- ── Users ──
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'individual'
        CHECK (role IN ('individual', 'recruiter', 'org_admin', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_tenant ON users(tenant_id);

-- ── Subscriptions ──
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    tier VARCHAR(20) NOT NULL DEFAULT 'free'
        CHECK (tier IN ('free', 'pro', 'premium', 'enterprise')),
    resumes_uploaded_this_month INTEGER DEFAULT 0,
    matches_this_month INTEGER DEFAULT 0,
    chat_messages_today INTEGER DEFAULT 0,
    last_usage_reset TIMESTAMPTZ DEFAULT NOW(),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);

-- ── Resumes ──
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID,
    title VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'uploaded'
        CHECK (status IN ('uploaded', 'processing', 'completed', 'failed')),
    version INTEGER DEFAULT 1,
    parsed_data JSONB,
    skills JSONB,
    embedding JSONB,
    overall_score FLOAT,
    section_scores JSONB,
    suggestions JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_resumes_user ON resumes(user_id);
CREATE INDEX idx_resumes_tenant ON resumes(tenant_id);
CREATE INDEX idx_resumes_status ON resumes(status);
CREATE INDEX idx_resumes_score ON resumes(overall_score);
CREATE INDEX idx_resumes_skills ON resumes USING GIN (skills);

-- ── Resume Versions (History Tracking) ──
CREATE TABLE resume_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    overall_score FLOAT,
    section_scores JSONB,
    parsed_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_resume_versions_resume ON resume_versions(resume_id);

-- ── Job Descriptions ──
CREATE TABLE job_descriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    description TEXT NOT NULL,
    required_skills JSONB,
    preferred_skills JSONB,
    experience_years VARCHAR(50),
    embedding JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_jobs_user ON job_descriptions(user_id);
CREATE INDEX idx_jobs_tenant ON job_descriptions(tenant_id);
CREATE INDEX idx_jobs_skills ON job_descriptions USING GIN (required_skills);

-- ── Match Results ──
CREATE TABLE match_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    tenant_id UUID,
    match_percentage FLOAT NOT NULL,
    matching_skills JSONB,
    missing_skills JSONB,
    role_suitability VARCHAR(50),
    recommendations JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_matches_resume ON match_results(resume_id);
CREATE INDEX idx_matches_job ON match_results(job_id);
CREATE INDEX idx_matches_tenant ON match_results(tenant_id);
CREATE INDEX idx_matches_score ON match_results(match_percentage);

-- ── Chat Messages ──
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_user ON chat_messages(user_id);
CREATE INDEX idx_chat_created ON chat_messages(created_at);

-- ── Function: Auto-update updated_at timestamp ──
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_resumes_updated_at
    BEFORE UPDATE ON resumes FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_jobs_updated_at
    BEFORE UPDATE ON job_descriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at();
