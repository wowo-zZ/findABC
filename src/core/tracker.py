#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import sqlite3
from ..db.database import PerformanceDB

class PerformanceTracker:
    def __init__(self):
        self.db = PerformanceDB()
    
    def add_employee(self, name, domain_account, gender, hometown, university, major, phone, department, position):
        """添加新员工"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                "INSERT INTO employees (name, domain_account, gender, hometown, university, major, phone, department, position, join_date) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (name, domain_account, gender, hometown, university, major, phone, department, position, 
                 datetime.now().strftime('%Y-%m-%d'))
            )
    
    def add_performance_record(self, employee_id, category, description, score):
        """记录员工表现"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                "INSERT INTO performance_records (employee_id, category, description, score, record_date) "
                "VALUES (?, ?, ?, ?, ?)",
                (employee_id, category, description, score, datetime.now().strftime('%Y-%m-%d'))
            )
    
    def update_scoring_rule(self, category, weight, description):
        """更新评分规则"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO scoring_rules (category, weight, description) VALUES (?, ?, ?)",
                (category, weight, description)
            )
    
    def get_all_employees(self):
        """获取所有员工的基本信息"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, name, department, position FROM employees ORDER BY id"
            )
            return cursor.fetchall()
    
    def get_employee_detail(self, employee_id):
        """获取特定员工的详细信息"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM employees WHERE id = ?",
                (employee_id,)
            )
            return cursor.fetchone()
    
    def update_global_setting(self, key, value, description):
        """更新全局设置"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO global_settings (key, value, description) VALUES (?, ?, ?)",
                (key, value, description)
            )