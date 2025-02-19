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
    
    def toggle_employee_status(self, employee_id, active):
        """激活或取消激活员工"""
        with sqlite3.connect(self.db.db_path) as conn:
            # 检查员工是否存在
            cursor = conn.execute("SELECT id FROM employees WHERE id = ?", (employee_id,))
            if not cursor.fetchone():
                raise ValueError("员工不存在")
            
            # 更新员工状态
            conn.execute(
                "UPDATE employees SET is_active = ? WHERE id = ?",
                (1 if active else 0, employee_id)
            )

    def get_all_employees(self):
        """获取所有员工的详细信息，按激活状态、职级职等从高到低排序"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, name, domain_account, gender, hometown, university, major, id_card, phone, department, position, join_date, is_active "
                "FROM employees "
                "ORDER BY "
                "is_active DESC, "
                "CASE "
                "  WHEN position LIKE 'P4%' THEN 1 "
                "  WHEN position LIKE 'P3%' THEN 2 "
                "  WHEN position LIKE 'P2%' THEN 3 "
                "END, "
                "CASE "
                "  WHEN position LIKE '%-3' THEN 1 "
                "  WHEN position LIKE '%-2' THEN 2 "
                "  WHEN position LIKE '%-1' THEN 3 "
                "END"
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
            # 添加工作量评分记录
            conn.execute(
                "INSERT INTO workload_scores (employee_id, week_number, year, ranking_percentage, score, description) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (employee_id, week, year, ranking_percentage, score, description)
            )
    
    def get_performance_summary(self, start_date, end_date):
        """获取指定时间段内的绩效统计汇总"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                """WITH WorkloadScores AS (
                    SELECT employee_id,
                           COALESCE(ROUND(AVG(score), 2), 0) as workload_score
                    FROM workload_scores
                    WHERE created_at BETWEEN ? AND ?
                    GROUP BY employee_id
                ),
                TechnicalScores AS (
                    SELECT employee_id,
                           COALESCE(ROUND(AVG(score), 2), 0) as technical_score
                    FROM technical_breakthrough_scores
                    WHERE completion_date BETWEEN ? AND ?
                    GROUP BY employee_id
                ),
                PromotionScores AS (
                    SELECT employee_id,
                           COALESCE(ROUND(AVG(score), 2), 0) as promotion_score
                    FROM promotion_scores
                    WHERE promotion_date BETWEEN ? AND ?
                    GROUP BY employee_id
                ),
                ExperienceScores AS (
                    SELECT employee_id,
                           COALESCE(ROUND(AVG(score), 2), 0) as experience_score
                    FROM experience_case_scores
                    WHERE submission_date BETWEEN ? AND ?
                    GROUP BY employee_id
                )
                SELECT e.id, e.name, e.department,
                       COALESCE(ws.workload_score, 0) as workload_score,
                       COALESCE(ts.technical_score, 0) as technical_score,
                       COALESCE(ps.promotion_score, 0) as promotion_score,
                       COALESCE(es.experience_score, 0) as experience_score,
                       ROUND((COALESCE(ws.workload_score, 0) + 
                             COALESCE(ts.technical_score, 0) + 
                             COALESCE(ps.promotion_score, 0) + 
                             COALESCE(es.experience_score, 0)) / 4, 2) as total_score
                FROM employees e
                LEFT JOIN WorkloadScores ws ON e.id = ws.employee_id
                LEFT JOIN TechnicalScores ts ON e.id = ts.employee_id
                LEFT JOIN PromotionScores ps ON e.id = ps.employee_id
                LEFT JOIN ExperienceScores es ON e.id = es.employee_id
                WHERE e.is_active = 1
                ORDER BY total_score DESC NULLS LAST""",
                (start_date, end_date,
                 start_date, end_date,
                 start_date, end_date,
                 start_date, end_date)
            )
            return cursor.fetchall()
    
    def get_employee_performance_detail(self, employee_id, start_date, end_date):
        """获取指定员工在指定时间段内的详细绩效记录"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                """SELECT 'workload' as category, description, score, 1 as weight, created_at as record_date
                   FROM workload_scores
                   WHERE employee_id = ? AND created_at BETWEEN ? AND ?
                   UNION ALL
                   SELECT 'promotion' as category, new_value as description, score, 1 as weight, promotion_date as record_date
                   FROM promotion_scores
                   WHERE employee_id = ? AND promotion_date BETWEEN ? AND ?
                   UNION ALL
                   SELECT 'technical' as category, description, score, 1 as weight, completion_date as record_date
                   FROM technical_breakthrough_scores
                   WHERE employee_id = ? AND completion_date BETWEEN ? AND ?
                   UNION ALL
                   SELECT 'experience' as category, description, score, 1 as weight, submission_date as record_date
                   FROM experience_case_scores
                   WHERE employee_id = ? AND submission_date BETWEEN ? AND ?
                   ORDER BY record_date DESC""",
                (employee_id, start_date, end_date,
                 employee_id, start_date, end_date,
                 employee_id, start_date, end_date,
                 employee_id, start_date, end_date)
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