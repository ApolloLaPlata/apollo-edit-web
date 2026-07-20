-- -------------------------------------------------------------
-- SCRIPT DE INICIALIZAÇÃO: APOLLO EDIT WEB (SUPABASE)
-- -------------------------------------------------------------

-- 1. EXTENSÃO PARA UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. TABELA DE USUÁRIOS (PILOTOS)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    username TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. TABELA DE CARTEIRAS (CRÉDITOS / COMBUSTÍVEL)
CREATE TABLE IF NOT EXISTS public.wallets (
    user_id UUID PRIMARY KEY REFERENCES public.users(id) ON DELETE CASCADE,
    credits_balance INTEGER DEFAULT 0 NOT NULL,
    free_tier_used INTEGER DEFAULT 0 NOT NULL,
    custom_api_keys JSONB DEFAULT '{}'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. TABELA DA GARAGEM (GAMIFICAÇÃO / NÍVEL)
CREATE TABLE IF NOT EXISTS public.garage (
    user_id UUID PRIMARY KEY REFERENCES public.users(id) ON DELETE CASCADE,
    current_car_tier TEXT DEFAULT 'Fusquinha' NOT NULL,
    total_videos_rendered INTEGER DEFAULT 0 NOT NULL,
    unlocked_cars JSONB DEFAULT '["Fusquinha"]'::jsonb
);

-- 5. TABELA DE JOBS (CORRIDAS / HISTÓRICO DE VÍDEOS)
CREATE TABLE IF NOT EXISTS public.jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'rendering' NOT NULL,
    cost_in_credits INTEGER DEFAULT 0 NOT NULL,
    video_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. CONFIGURAÇÃO DE SEGURANÇA (RLS - ROW LEVEL SECURITY)
-- Habilita a segurança para que um usuário não veja os dados do outro
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.garage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;

-- Políticas de Acesso
CREATE POLICY "Users can view their own data" ON public.users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can view their own wallet" ON public.wallets FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can view their own garage" ON public.garage FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can view their own jobs" ON public.jobs FOR SELECT USING (auth.uid() = user_id);
