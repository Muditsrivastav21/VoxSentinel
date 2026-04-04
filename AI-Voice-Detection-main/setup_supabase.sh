#!/bin/bash

# VoxSentinel - Supabase Setup Script
# This script will help you set up the Supabase database

echo "🚀 VoxSentinel Supabase Setup"
echo "================================"
echo ""

# Check if Supabase URL and key are set
if grep -q "YOUR_PROJECT" .env; then
    echo "⚠️  WARNING: Supabase credentials not configured!"
    echo ""
    echo "Please update .env with your Supabase credentials:"
    echo "1. Go to https://supabase.com/dashboard"
    echo "2. Select your project (or create one)"
    echo "3. Go to Settings > API"
    echo "4. Copy the URL and anon key to .env"
    echo ""
    exit 1
fi

echo "✅ Environment variables loaded"
echo ""

# Load environment variables
source .env

echo "📊 Database Setup"
echo "================================"
echo ""
echo "Now you need to run the SQL schema in Supabase:"
echo ""
echo "1. Open https://supabase.com/dashboard/project/YOUR_PROJECT/editor"
echo "2. Click 'New query'"
echo "3. Copy the contents of supabase_schema.sql"
echo "4. Paste and execute"
echo ""
echo "The schema includes:"
echo "  • call_analyses table"
echo "  • api_keys table (optional)"
echo "  • api_usage table (optional)"
echo "  • Dashboard stats views"
echo "  • Helpful indexes for performance"
echo ""

# Test connection
echo "🔌 Testing Supabase connection..."
python3 << EOF
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from supabase import create_client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if url and key:
        client = create_client(url, key)
        print("✅ Supabase connection successful!")
    else:
        print("❌ Supabase credentials not found in .env")
except ImportError:
    print("⚠️  Supabase package not installed. Run: pip install supabase")
except Exception as e:
    print(f"❌ Connection failed: {e}")
EOF

echo ""
echo "================================"
echo "Setup complete! Next steps:"
echo ""
echo "1. Run the SQL schema in Supabase (if not done)"
echo "2. Start the backend: uvicorn app:app --reload"
echo "3. Visit http://localhost:8000/docs to test"
echo ""
