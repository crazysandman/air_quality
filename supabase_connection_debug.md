# =====================================
# SUPABASE CONNECTION TROUBLESHOOTING
# =====================================

# Aktuelle (nicht funktionierende) URL:
# postgresql://postgres:Hatschepsut1@db.syqqyhqczajtgsfzigyo.supabase.co:5432/postgres

# Alternative 1: Session Mode (empfohlen für Railway)
# postgresql://postgres.syqqyhqczajtgsfzigyo:Hatschepsut1@aws-0-eu-central-1.pooler.supabase.com:5432/postgres

# Alternative 2: Transaction Mode
# postgresql://postgres.syqqyhqczajtgsfzigyo:Hatschepsut1@aws-0-eu-central-1.pooler.supabase.com:6543/postgres

# Alternative 3: Mit SSL-Modi
# postgresql://postgres:Hatschepsut1@db.syqqyhqczajtgsfzigyo.supabase.co:5432/postgres?sslmode=require

# Alternative 4: IPv4 only
# postgresql://postgres:Hatschepsut1@db.syqqyhqczajtgsfzigyo.supabase.co:5432/postgres?sslmode=require&target_session_attrs=read-write

# ANLEITUNG:
# 1. Gehe zu Supabase Dashboard → Settings → Database
# 2. Kopiere die "Connection pooling" URL (Session mode)
# 3. Ersetze in Railway Environment Variables
# 4. Redeploy

# WICHTIG: 
# - Verwende CONNECTION POOLING URLs, nicht Direct Database URLs
# - Session Mode ist besser für persistente Connections (wie Railway)
# - Transaction Mode ist besser für Serverless (wie Vercel)
