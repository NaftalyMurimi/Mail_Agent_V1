from app.database import supabase

if supabase:
    print('Supabase connected OK')
else:
    print('Supabase not configured - check your .env file')