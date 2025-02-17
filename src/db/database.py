#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from datetime import datetime
from pathlib import Path

APP_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = APP_DIR / 'data' / 'performance.db'

class PerformanceDB:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_db()
    
    def init_db(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA encoding = 'UTF-8'")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    domain_account TEXT NOT NULL,
                    gender TEXT,
                    hometown TEXT,
                    university TEXT,
                    major TEXT,
                    phone TEXT NOT NULL,
                    id_card TEXT NOT NULL,
                    department TEXT,
                    position TEXT,
                    join_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(id_card),
                    UNIQUE(phone)
                );
                
                CREATE TABLE IF NOT EXISTS workload_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER,
                    week_number INTEGER,
                    year INTEGER,
                    ranking_percentage REAL,
                    score REAL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees(id)
                );

                CREATE TABLE IF NOT EXISTS promotion_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER,
                    promotion_type TEXT CHECK(promotion_type IN ('level', 'grade')),
                    old_value TEXT,
                    new_value TEXT,
                    score REAL,
                    promotion_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees(id)
                );

                CREATE TABLE IF NOT EXISTS technical_breakthrough_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER,
                    level TEXT CHECK(level IN ('company', 'department')),
                    project_name TEXT,
                    description TEXT,
                    score REAL,
                    completion_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees(id)
                );

                CREATE TABLE IF NOT EXISTS experience_case_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER,
                    level TEXT CHECK(level IN ('company', 'other')),
                    case_title TEXT,
                    description TEXT,
                    score REAL,
                    submission_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees(id)
                );

                CREATE TABLE IF NOT EXISTS performance_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER,
                    total_score REAL,
                    workload_score REAL,
                    promotion_score REAL,
                    technical_score REAL,
                    experience_score REAL,
                    summary_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees(id)
                );
                
                CREATE TABLE IF NOT EXISTS scoring_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    weight REAL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS global_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)