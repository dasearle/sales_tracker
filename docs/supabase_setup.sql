-- Supabase Setup SQL for Sales Tracker
-- Run these commands in the Supabase SQL Editor in order

-- ============================================================================
-- 1. Create user_roles table
-- ============================================================================

CREATE TYPE user_role AS ENUM ('admin', 'sales', 'marketing', 'management');

CREATE TABLE public.user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role user_role NOT NULL DEFAULT 'sales',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(user_id)
);

CREATE INDEX idx_user_roles_user_id ON public.user_roles(user_id);

ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 2. Create trigger for default role assignment on signup
-- ============================================================================

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_roles (user_id, role) VALUES (NEW.id, 'sales');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================================
-- 3. Create RLS policies
-- ============================================================================

-- Users can view their own role
CREATE POLICY "Users can view own role" ON public.user_roles
    FOR SELECT USING (auth.uid() = user_id);

-- Admins can view all roles
CREATE POLICY "Admins can view all roles" ON public.user_roles
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM public.user_roles WHERE user_id = auth.uid() AND role = 'admin')
    );

-- Admins can update roles
CREATE POLICY "Admins can update roles" ON public.user_roles
    FOR UPDATE USING (
        EXISTS (SELECT 1 FROM public.user_roles WHERE user_id = auth.uid() AND role = 'admin')
    );

-- ============================================================================
-- 4. Create Auth Hook for JWT claims
-- ============================================================================
-- After running this, go to Supabase Dashboard:
-- Authentication > Hooks > Enable "Customize Access Token" > Select custom_access_token_hook

CREATE OR REPLACE FUNCTION public.custom_access_token_hook(event JSONB)
RETURNS JSONB AS $$
DECLARE
    claims JSONB;
    user_role_value TEXT;
BEGIN
    SELECT role::TEXT INTO user_role_value
    FROM public.user_roles WHERE user_id = (event->>'user_id')::UUID;

    IF user_role_value IS NULL THEN user_role_value := 'sales'; END IF;

    claims := event->'claims';
    claims := jsonb_set(claims, '{app_metadata}',
        COALESCE(claims->'app_metadata', '{}'::JSONB) || jsonb_build_object('role', user_role_value));
    event := jsonb_set(event, '{claims}', claims);
    RETURN event;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permissions for the auth hook
GRANT USAGE ON SCHEMA public TO supabase_auth_admin;
GRANT EXECUTE ON FUNCTION public.custom_access_token_hook TO supabase_auth_admin;
GRANT SELECT ON public.user_roles TO supabase_auth_admin;
REVOKE EXECUTE ON FUNCTION public.custom_access_token_hook FROM authenticated, anon, public;

-- ============================================================================
-- 5. Bootstrap first admin (run after your first login)
-- ============================================================================
-- Replace <your-user-id> with your actual user ID from auth.users

-- To find your user ID:
-- SELECT id, email FROM auth.users;

-- Then run:
-- UPDATE public.user_roles SET role = 'admin' WHERE user_id = '<your-user-id>';
