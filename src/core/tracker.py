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
            # 首先获取category_id
            cursor = conn.execute(
                "SELECT id FROM performance_categories WHERE name = ? AND is_active = 1",
                (category,)
            )
            category_row = cursor.fetchone()
            if not category_row:
                raise ValueError(f"类别 '{category}' 不存在或未启用")
            
            category_id = category_row[0]
            
            # 插入记录
            conn.execute(
                "INSERT INTO performance_records (employee_id, category_id, description, score, record_date) "
                "VALUES (?, ?, ?, ?, ?)",
                (employee_id, category_id, description, score, datetime.now().strftime('%Y-%m-%d'))
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
    
    def get_workload_summary(self, start_date, end_date):
        """获取指定时间段内的工作量评分汇总"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT 
                    employee_id,
                    ROUND(AVG(score), 2) as avg_score
                FROM performance_records pr
                JOIN performance_categories pc ON pr.category_id = pc.id
                WHERE pc.name = '工作量'
                AND pr.record_date BETWEEN ? AND ?
                GROUP BY employee_id
                """,
                (start_date, end_date)
            )
            return cursor.fetchall()
    
    def get_workload_details(self, start_date, end_date):
        """获取指定时间段内的工作量评分详情"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT 
                    week_number,
                    COUNT(DISTINCT employee_id) as employee_count,
                    ROUND(AVG(score), 2) as avg_score,
                    year
                FROM workload_scores
                WHERE (year || '-' || PRINTF('%02d', week_number)) BETWEEN 
                    (strftime('%Y', ?) || '-' || strftime('%W', ?)) 
                    AND 
                    (strftime('%Y', ?) || '-' || strftime('%W', ?))
                GROUP BY year, week_number
                ORDER BY year, week_number
                """,
                (start_date, start_date, end_date, end_date)
            )
            return cursor.fetchall()
    
    def get_performance_summary(self, start_date, end_date):
        """获取指定时间段内的绩效统计"""
        with sqlite3.connect(self.db.db_path) as conn:
            # 首先获取所有激活的表现类别
            cursor = conn.execute(
                "SELECT name FROM performance_categories WHERE is_active = 1 ORDER BY name"
            )
            categories = [row[0] for row in cursor.fetchall()]
            
            # 构建动态SQL查询
            category_columns = ',\n'.join([
                f"COALESCE(MAX(CASE WHEN cs.category = '{cat}' THEN cs.category_score END), 0) as {cat.replace(' ', '_')}_score"
                for cat in categories
            ])
            
            sql = f"""
            WITH WorkloadScores AS (
                -- 计算工作量得分（从workload_scores表获取总分）
                SELECT 
                    employee_id,
                    ROUND(SUM(score), 2) as workload_score  -- 改为SUM而不是AVG
                FROM workload_scores
                WHERE (year || '-' || PRINTF('%02d', week_number)) BETWEEN 
                    (strftime('%Y', ?) || '-' || strftime('%W', ?)) 
                    AND 
                    (strftime('%Y', ?) || '-' || strftime('%W', ?))
                GROUP BY employee_id
            ),
            CategoryScores AS (
                -- 计算各表现类别的总分
                SELECT 
                    pr.employee_id,
                    pc.name as category,
                    ROUND(SUM(pr.score), 2) as category_score
                FROM performance_records pr
                JOIN performance_categories pc ON pr.category_id = pc.id
                WHERE pr.record_date BETWEEN ? AND ?
                GROUP BY pr.employee_id, pc.name
            )
            SELECT 
                e.id,
                e.name,
                e.department,
                COALESCE(ws.workload_score, 0) as workload_score,
                {category_columns},
                ROUND(
                    COALESCE(ws.workload_score, 0) + 
                    COALESCE(SUM(cs.category_score), 0)
                , 2) as total_score
            FROM employees e
            LEFT JOIN WorkloadScores ws ON e.id = ws.employee_id
            LEFT JOIN CategoryScores cs ON e.id = cs.employee_id
            WHERE e.is_active = 1
            GROUP BY e.id, e.name, e.department
            ORDER BY total_score DESC
            """
            
            cursor = conn.execute(sql, (start_date, start_date, end_date, end_date, start_date, end_date))
            return cursor.fetchall(), categories
    
    def get_employee_workload_detail(self, employee_id, start_date, end_date):
        """获取指定员工在指定时间段内的工作承担得分记录"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT 
                    week_number,
                    ranking_percentage,
                    score,
                    year,
                    description
                FROM workload_scores
                WHERE employee_id = ?
                AND (year || '-' || PRINTF('%02d', week_number)) BETWEEN 
                    (strftime('%Y', ?) || '-' || strftime('%W', ?)) 
                    AND 
                    (strftime('%Y', ?) || '-' || strftime('%W', ?))
                ORDER BY year DESC, week_number DESC
                """,
                (employee_id, start_date, start_date, end_date, end_date)
            )
            return cursor.fetchall()
    
    def get_employee_performance_detail(self, employee_id, start_date, end_date):
        """获取指定员工在指定时间段内的表现得分记录"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT 
                    pc.name as category,
                    pr.description,
                    pr.score,
                    pr.record_date
                FROM performance_records pr
                JOIN performance_categories pc ON pr.category_id = pc.id
                WHERE pr.employee_id = ? 
                AND pr.record_date BETWEEN ? AND ?
                ORDER BY pr.record_date DESC
                """,
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

    def get_active_categories(self):
        """获取所有启用的表现类别"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                "SELECT name, description FROM performance_categories WHERE is_active = 1"
            )
            return cursor.fetchall()

    def add_category(self, name, description):
        """添加新的表现类别"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                "INSERT INTO performance_categories (name, description) VALUES (?, ?)",
                (name, description)
            )

    def toggle_category(self, name, active):
        """启用或禁用表现类别"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                "UPDATE performance_categories SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
                (active, name)
            )

    def get_all_categories(self):
        """获取所有表现类别（包括已禁用的）"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                "SELECT name, description, is_active FROM performance_categories ORDER BY name"
            )
            return cursor.fetchall()

    def update_category(self, old_name, new_name, description, is_active):
        """更新表现类别信息"""
        with sqlite3.connect(self.db.db_path) as conn:
            # 检查新名称是否已存在（如果名称有变化）
            if old_name != new_name:
                cursor = conn.execute(
                    "SELECT id FROM performance_categories WHERE name = ? AND name != ?",
                    (new_name, old_name)
                )
                if cursor.fetchone():
                    raise ValueError(f"类别名称 '{new_name}' 已存在")
            
            # 更新类别信息
            conn.execute(
                """
                UPDATE performance_categories 
                SET name = ?, description = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE name = ?
                """,
                (new_name, description, is_active, old_name)
            )

    def get_performance_record(self, record_id):
        """获取特定表现记录的详细信息"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT 
                    pr.id,
                    e.name as employee_name,
                    pc.name as category_name,
                    pr.score,
                    pr.description,
                    pr.record_date
                FROM performance_records pr
                JOIN employees e ON pr.employee_id = e.id
                JOIN performance_categories pc ON pr.category_id = pc.id
                WHERE pr.id = ?
                """,
                (record_id,)
            )
            return cursor.fetchone()

    def update_performance_record(self, record_id, new_score, new_description):
        """更新表现记录"""
        with sqlite3.connect(self.db.db_path) as conn:
            # 检查记录是否存在
            cursor = conn.execute("SELECT id FROM performance_records WHERE id = ?", (record_id,))
            if not cursor.fetchone():
                raise ValueError("记录不存在")
            
            # 更新记录
            conn.execute(
                """
                UPDATE performance_records 
                SET score = ?, description = ?
                WHERE id = ?
                """,
                (new_score, new_description, record_id)
            )

    def get_employee_performance_records(self, employee_id, start_date, end_date):
        """获取指定员工在指定时间段内的所有表现记录"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT 
                    pr.id,
                    e.name as employee_name,
                    pc.name as category_name,
                    pr.score,
                    pr.description,
                    pr.record_date
                FROM performance_records pr
                JOIN employees e ON pr.employee_id = e.id
                JOIN performance_categories pc ON pr.category_id = pc.id
                WHERE pr.employee_id = ? 
                AND pr.record_date BETWEEN ? AND ?
                ORDER BY pr.record_date DESC
                """,
                (employee_id, start_date, end_date)
            )
            return cursor.fetchall()

    def delete_performance_record(self, record_id):
        """删除表现记录"""
        with sqlite3.connect(self.db.db_path) as conn:
            # 检查记录是否存在
            cursor = conn.execute("SELECT id FROM performance_records WHERE id = ?", (record_id,))
            if not cursor.fetchone():
                raise ValueError("记录不存在")
            
            # 删除记录
            conn.execute("DELETE FROM performance_records WHERE id = ?", (record_id,))