-- AI Workflow Automation Hub - Initial Schema

CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_name VARCHAR(255) NOT NULL,
    workflow_type VARCHAR(50) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(50) DEFAULT 'success',
    execution_time_ms INTEGER,
    tokens_used INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 4) DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    template_type VARCHAR(50),
    content TEXT NOT NULL,
    variables JSONB,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workflow_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    n8n_workflow_id VARCHAR(255),
    enabled BOOLEAN DEFAULT TRUE,
    config JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_we_created ON workflow_executions(created_at);
CREATE INDEX IF NOT EXISTS idx_we_type    ON workflow_executions(workflow_type);

-- Seed default workflow configs
INSERT INTO workflow_configs (name, description, n8n_workflow_id, enabled) VALUES
  ('Lead Qualification Pipeline',  'AI lead scoring and routing',         'lead-qualification',  true),
  ('Email Intelligence & Routing', 'Smart email classification',           'email-routing',       true),
  ('Content Generation Pipeline',  'Daily AI content creation',            'content-generation',  true),
  ('Document Processing',          'Automated PDF analysis',               'document-processing', true)
ON CONFLICT DO NOTHING;
