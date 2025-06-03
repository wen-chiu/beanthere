#!/usr/bin/env python3
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database_if_not_exists():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="beanthere_user",
            password="beanthere_pass",
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Checking if database exist
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='beanthere'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE beanthere")
            print("✅ Database 'beanthere' Created")
        else:
            print("ℹ️  Database 'beanthere' Existed")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error while creating Database: {e}")
        sys.exit(1)

def run_migrations():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="beanthere_user",
            password="beanthere_pass",
            database="beanthere"
        )
        cursor = conn.cursor()
        
        # Run and execute schema.sql
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
            cursor.execute(schema)
        
        conn.commit()
        print("✅ Database schema created")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ error while running database migrations : {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔧 Starting Database Configuration...")
    create_database_if_not_exists()
    run_migrations()
    print("✅ Database Configuration Completed！")