#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import sqlite3
from ..db.database import PerformanceDB

class PerformanceTracker:
    def __init__(self):
        self.db = PerformanceDB()
    
    def add_employee(self, name, domain_account, gender, hometown, university, major, phone, department, position, join_date):
        """添加新员工"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                "INSERT INTO employees (name, domain_account, gender, hometown, university, major, phone, department, position, join_date) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (name, domain_account, gender, hometown, university, major, phone, department, position, join_date)
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
        """获取所有员工的详细信息"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, name, domain_account, gender, hometown, university, major, id_card, phone, department, position, join_date FROM employees ORDER BY id"
            )
            return cursor.fetchall()
    
    def get_employee_by_name(self, name):
        """根据姓名获取员工的详细信息"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM employees WHERE name = ?",
                (name,)
            )
            return cursor.fetchone()
    
    def get_employee_detail(self, employee_id):
        """获取特定员工的详细信息"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM employees WHERE id = ?",
                (employee_id,)
            )
            return cursor.fetchone()
    
    def delete_employee(self, employee_id):
        """删除指定员工及其相关记录"""
        with sqlite3.connect(self.db.db_path) as conn:
            # 检查员工是否存在
            cursor = conn.execute("SELECT id FROM employees WHERE id = ?", (employee_id,))
            if not cursor.fetchone():
                raise ValueError("员工不存在")
            
            # 删除员工相关的所有记录
            tables = [
                'workload_scores',
                'promotion_scores',
                'technical_breakthrough_scores',
                'experience_case_scores',
                'performance_summary'
            ]
            
            # 删除关联表中的记录
            for table in tables:
                conn.execute(f"DELETE FROM {table} WHERE employee_id = ?", (employee_id,))
            
            # 删除员工记录
            conn.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    
    def update_global_setting(self, key, value, description):
        """更新全局设置"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO global_settings (key, value, description) VALUES (?, ?, ?)",
                (key, value, description)
            )
    
    def get_workload_record(self, week, year):
        """获取指定周的工作量记录"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM workload_scores WHERE week_number = ? AND year = ?",
                (week, year)
            )
            return cursor.fetchone()
    
    def add_workload_score(self, employee_id, week, year, ranking_percentage, score, description):
        """添加工作量评分记录"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                "INSERT INTO workload_scores (employee_id, week_number, year, ranking_percentage, score, description) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (employee_id, week, year, ranking_percentage, score, description)
            )
    
    def get_performance_summary(self, start_date, end_date):
        """获取指定时间段内的绩效统计汇总"""
        with sqlite3.connect(self.db.db_path) as conn:
            # 获取所有员工的绩效记录
            cursor = conn.execute(
                """SELECT e.id, e.name, e.department,
                          COALESCE(SUM(ws.score), 0) as workload_score,
                          SUM(CASE WHEN pr.category = 'technical' THEN pr.score * sr.weight ELSE 0 END) as technical_score,
                          SUM(CASE WHEN pr.category = 'responsibility' THEN pr.score * sr.weight ELSE 0 END) as responsibility_score,
                          SUM(CASE WHEN pr.category = 'experience' THEN pr.score * sr.weight ELSE 0 END) as experience_score,
                          COALESCE(SUM(ws.score), 0) + 
                          COALESCE(SUM(pr.score * sr.weight), 0) as total_score
                   FROM employees e
                   LEFT JOIN workload_scores ws ON e.id = ws.employee_id
                   LEFT JOIN performance_records pr ON e.id = pr.employee_id
                   LEFT JOIN scoring_rules sr ON pr.category = sr.category
                   WHERE (ws.created_at BETWEEN ? AND ?) OR (pr.record_date BETWEEN ? AND ?)
                   GROUP BY e.id
                   ORDER BY total_score DESC""",
                (start_date, end_date, start_date, end_date)
            )
            return cursor.fetchall()
    
    def get_employee_performance_detail(self, employee_id, start_date, end_date):
        """获取指定员工在指定时间段内的详细绩效记录"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                """SELECT pr.category, pr.description, pr.score, sr.weight, pr.record_date
                   FROM performance_records pr
                   LEFT JOIN scoring_rules sr ON pr.category = sr.category
                   WHERE pr.employee_id = ? AND pr.record_date BETWEEN ? AND ?
                   ORDER BY pr.record_date DESC""",
                (employee_id, start_date, end_date)
            )
            return cursor.fetchall()
    
    def get_current_performance_cycle(self):
        """获取当前绩效周期的起止日期"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                "SELECT value FROM global_settings WHERE key = 'performance_cycle'"
            )
            cycle = cursor.fetchone()
            
            if not cycle:
                return None, None
            
            today = datetime.now()
            if cycle[0] == 'monthly':
                # 月度绩效：当月1号到月末
                start_date = today.replace(day=1).strftime('%Y-%m-%d')
                if today.month == 12:
                    end_date = today.replace(year=today.year + 1, month=1, day=1)
                else:
                    end_date = today.replace(month=today.month + 1, day=1)
                end_date = (end_date - timedelta(days=1)).strftime('%Y-%m-%d')
            else:
                # 季度绩效：当季度第一天到最后一天
                quarter = (today.month - 1) // 3
                start_date = today.replace(month=quarter * 3 + 1, day=1).strftime('%Y-%m-%d')
                if quarter == 3:
                    end_date = today.replace(year=today.year + 1, month=1, day=1)
                else:
                    end_date = today.replace(month=(quarter + 1) * 3 + 1, day=1)
                end_date = (end_date - timedelta(days=1)).strftime('%Y-%m-%d')
                
            return start_date, end_date