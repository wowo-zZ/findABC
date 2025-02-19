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
        """添加工作量评分记录并更新绩效汇总"""
        with sqlite3.connect(self.db.db_path) as conn:
            # 添加工作量评分记录
            conn.execute(
                "INSERT INTO workload_scores (employee_id, week_number, year, ranking_percentage, score, description) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (employee_id, week, year, ranking_percentage, score, description)
            )
            
            # 获取当前绩效周期
            start_date, end_date = self.get_current_performance_cycle()
            if not start_date or not end_date:
                return
            
            # 计算该员工在当前周期内的各项得分
            cursor = conn.execute(
                """SELECT 
                    AVG(ws.score) as workload_score,
                    COALESCE((SELECT AVG(score) FROM technical_breakthrough_scores 
                             WHERE employee_id = ? AND completion_date BETWEEN ? AND ?), 0) as technical_score,
                    COALESCE((SELECT AVG(score) FROM promotion_scores 
                             WHERE employee_id = ? AND promotion_date BETWEEN ? AND ?), 0) as promotion_score,
                    COALESCE((SELECT AVG(score) FROM experience_case_scores 
                             WHERE employee_id = ? AND submission_date BETWEEN ? AND ?), 0) as experience_score
                FROM workload_scores ws
                WHERE ws.employee_id = ? AND ws.created_at BETWEEN ? AND ?""",
                (employee_id, start_date, end_date,
                 employee_id, start_date, end_date,
                 employee_id, start_date, end_date,
                 employee_id, start_date, end_date)
            )
            scores = cursor.fetchone()
            
            if scores:
                workload_score = scores[0] or 0
                technical_score = scores[1] or 0
                promotion_score = scores[2] or 0
                experience_score = scores[3] or 0
                
                # 计算总分（这里假设各项权重相等）
                total_score = round((workload_score + technical_score + promotion_score + experience_score) / 4, 2)
                
                # 更新或插入绩效汇总记录
                conn.execute(
                    """INSERT OR REPLACE INTO performance_summary 
                       (employee_id, workload_score, technical_score, promotion_score, 
                        experience_score, total_score, summary_date)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (employee_id, round(workload_score, 2), round(technical_score, 2), round(promotion_score, 2),
                     round(experience_score, 2), total_score, datetime.now().strftime('%Y-%m-%d'))
                )
    
    def get_performance_summary(self, start_date, end_date):
        """获取指定时间段内的绩效统计汇总"""
        with sqlite3.connect(self.db.db_path) as conn:
            # 获取所有员工的绩效记录，使用窗口函数获取每个员工最新的记录
            cursor = conn.execute(
                """WITH WorkloadSum AS (
                    SELECT employee_id,
                           SUM(score) as total_workload_score
                    FROM workload_scores
                    WHERE created_at BETWEEN ? AND ?
                    GROUP BY employee_id
                ),
                RankedPerformance AS (
                    SELECT employee_id,
                           technical_score,
                           promotion_score,
                           experience_score,
                           total_score,
                           summary_date,
                           ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY summary_date DESC) as rn
                    FROM performance_summary
                    WHERE summary_date BETWEEN ? AND ?
                )
                SELECT e.id, e.name, e.department,
                       COALESCE(ROUND(ws.total_workload_score, 2), 0) as workload_score,
                       ROUND(ps.technical_score, 2) as technical_score,
                       ROUND(ps.promotion_score, 2) as promotion_score,
                       ROUND(ps.experience_score, 2) as experience_score,
                       ROUND((COALESCE(ws.total_workload_score, 0) + COALESCE(ps.technical_score * 4, 0) + 
                             COALESCE(ps.promotion_score * 4, 0) + COALESCE(ps.experience_score * 4, 0)) / 4, 2) as total_score
                FROM employees e
                LEFT JOIN WorkloadSum ws ON e.id = ws.employee_id
                LEFT JOIN RankedPerformance ps ON e.id = ps.employee_id AND ps.rn = 1
                WHERE e.is_active = 1
                ORDER BY total_score DESC NULLS LAST""",
                (start_date, end_date,
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