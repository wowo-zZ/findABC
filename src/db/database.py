#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from datetime import datetime
from pathlib import Path

# 获取项目根目录的绝对路径
APP_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEFAULT_DB_PATH = APP_DIR / 'data' / 'performance.db'

class PerformanceDB:
    def __init__(self, db_path=None):
        """初始化数据库连接
        
        Args:
            db_path: 数据库文件路径，默认为项目根目录下的 data/performance.db
        """
        self.db_path = db_path if db_path else DEFAULT_DB_PATH
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(str(self.db_path)), exist_ok=True)
        
        # 初始化数据库
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA encoding = 'UTF-8'")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    domain_account TEXT UNIQUE,
                    gender TEXT,
                    hometown TEXT,
                    university TEXT,
                    major TEXT,
                    id_card TEXT,
                    phone TEXT,
                    department TEXT,
                    position TEXT,
                    join_date TEXT,
                    is_active INTEGER DEFAULT 1,
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