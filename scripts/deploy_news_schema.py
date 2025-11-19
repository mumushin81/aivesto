#!/usr/bin/env python3
"""
Deploy news collection database schema to Supabase
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from loguru import logger

load_dotenv()

def deploy_schema():
    """Deploy news tables schema to Supabase"""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("SUPABASE_URL and SUPABASE_KEY must be set")
        return False

    supabase = create_client(supabase_url, supabase_key)

    # Read SQL schema file
    schema_file = Path("/Users/jinxin/dev/aivesto/database/news_tables_schema.sql")

    if not schema_file.exists():
        logger.error(f"Schema file not found: {schema_file}")
        return False

    logger.info(f"Reading schema from {schema_file}")
    sql_content = schema_file.read_text()

    # Split SQL into individual statements
    statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]

    logger.info(f"Found {len(statements)} SQL statements to execute")

    # Execute each statement
    success_count = 0
    error_count = 0

    for i, statement in enumerate(statements, 1):
        if not statement or statement.startswith('--'):
            continue

        try:
            # Get statement type for logging
            stmt_type = statement.split()[0].upper()

            logger.info(f"[{i}/{len(statements)}] Executing {stmt_type}...")

            # Execute via RPC (Supabase doesn't support direct SQL execution via REST API)
            # We need to create tables manually via Supabase dashboard or use SQL editor

            # For now, just log what would be executed
            if 'CREATE TABLE' in statement:
                table_name = statement.split('CREATE TABLE')[1].split('(')[0].strip().split()[0]
                logger.warning(f"  Table: {table_name} - Must be created via Supabase SQL Editor")
            elif 'CREATE VIEW' in statement:
                view_name = statement.split('CREATE')[1].split('VIEW')[1].split('AS')[0].strip()
                logger.warning(f"  View: {view_name} - Must be created via Supabase SQL Editor")
            elif 'CREATE POLICY' in statement:
                logger.warning(f"  RLS Policy - Must be created via Supabase SQL Editor")

            success_count += 1

        except Exception as e:
            logger.error(f"  ❌ Error executing statement {i}: {e}")
            logger.debug(f"  Statement: {statement[:100]}...")
            error_count += 1

    logger.info("\n" + "=" * 60)
    logger.info("⚠️  MANUAL DEPLOYMENT REQUIRED")
    logger.info("=" * 60)
    logger.info("Supabase REST API doesn't support DDL operations.")
    logger.info("Please execute the SQL manually:")
    logger.info("")
    logger.info("1. Go to: https://supabase.com/dashboard")
    logger.info("2. Select your project")
    logger.info("3. Go to SQL Editor")
    logger.info("4. Copy and paste the contents of:")
    logger.info(f"   {schema_file}")
    logger.info("5. Click 'Run'")
    logger.info("=" * 60)

    return True


if __name__ == "__main__":
    deploy_schema()
