#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import sqlite3
from ..db.database import PerformanceDB

class PerformanceTracker:
    def __init__(self, db_path=None):
        """初始化跟踪器
        
        Args:
            db_path: 可选的数据库路径
        """
        self.db = PerformanceDB(db_path) if db_path else PerformanceDB()
    
    def add_employee(self, name, domain_account, gender, hometown, university, major, phone, id_card, department, position, join_date):
        """添加新员工
        
        Args:
            name: 姓名
            domain_account: 域账号
            gender: 性别
            hometown: 家乡
            university: 毕业院校
            major: 专业
            phone: 电话
            id_card: 身份证号
            department: 部门
            position: 职级
            join_date: 入职日期
        """
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                """INSERT INTO employees 
                   (name, domain_account, gender, hometown, university, major, phone, id_card, department, position, join_date) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, domain_account, gender, hometown, university, major, phone, id_card, department, position, join_date)
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
        """获取所有员工信息"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    id,
                    name,
                    domain_account,
                    gender,
                    hometown,
                    university,
                    major,
                    phone,
                    id_card,
                    department,
                    position,
                    join_date,
                    is_active,
                    created_at
                FROM employees
                ORDER BY position, name
            """)
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
            cursor = conn.execute("""
                SELECT 
                    id,
                    name,
                    domain_account,
                    gender,
                    hometown,
                    university,
                    major,
                    phone,
                    id_card,
                    department,
                    position,
                    join_date,
                    is_active,
                    created_at
                FROM employees
                WHERE id = ?
            """, (employee_id,))
            return cursor.fetchone()
    
    def delete_employee(self, employee_id):
        """删除指定员工"""
        with sqlite3.connect(self.db.db_path) as conn:
            # 检查员工是否存在
            cursor = conn.execute("SELECT id FROM employees WHERE id = ?", (employee_id,))
            if not cursor.fetchone():
                raise ValueError("员工不存在")
            
            # 删除员工相关的所有记录
            conn.execute("DELETE FROM workload_scores WHERE employee_id = ?", (employee_id,))
            conn.execute("DELETE FROM performance_records WHERE employee_id = ?", (employee_id,))
            conn.execute("DELETE FROM promotion_scores WHERE employee_id = ?", (employee_id,))
            conn.execute("DELETE FROM technical_breakthrough_scores WHERE employee_id = ?", (employee_id,))
            conn.execute("DELETE FROM experience_case_scores WHERE employee_id = ?", (employee_id,))
            
            # 删除员工信息
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
        """获取所有表现类别"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    id,
                    name,
                    description,
                    is_active,
                    created_at
                FROM performance_categories
                ORDER BY name
            """)
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

    def toggle_category_status(self, name, active):
        """启用或禁用表现类别
        
        Args:
            name: 类别名称
            active: True 表示启用，False 表示禁用
        """
        with sqlite3.connect(self.db.db_path) as conn:
            # 检查类别是否存在
            cursor = conn.execute("SELECT id FROM performance_categories WHERE name = ?", (name,))
            if not cursor.fetchone():
                raise ValueError(f"类别 '{name}' 不存在")
            
            # 更新类别状态
            conn.execute(
                "UPDATE performance_categories SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
                (1 if active else 0, name)
            )

    def get_category_status(self, name):
        """获取表现类别的当前状态
        
        Args:
            name: 类别名称
            
        Returns:
            bool|None: True表示启用，False表示禁用，None表示类别不存在
        """
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                "SELECT is_active FROM performance_categories WHERE name = ?",
                (name,)
            )
            result = cursor.fetchone()
            return result[0] if result else None

    def get_category_detail(self, name):
        """获取表现类别的详细信息"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    id,
                    name,
                    description,
                    is_active,
                    created_at,
                    updated_at
                FROM performance_categories
                WHERE name = ?
            """, (name,))
            return cursor.fetchone()

    def get_category_record_count(self, name):
        """获取表现类别下的记录数量"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*)
                FROM performance_records pr
                JOIN performance_categories pc ON pr.category_id = pc.id
                WHERE pc.name = ?
            """, (name,))
            return cursor.fetchone()[0]

    def delete_category(self, name):
        """删除表现类别及其关联记录
        
        Args:
            name: 类别名称
        """
        with sqlite3.connect(self.db.db_path) as conn:
            # 检查类别是否存在
            cursor = conn.execute("SELECT id FROM performance_categories WHERE name = ?", (name,))
            category = cursor.fetchone()
            if not category:
                raise ValueError(f"类别 '{name}' 不存在")
            
            category_id = category[0]
            
            # 删除关联的表现记录
            conn.execute("DELETE FROM performance_records WHERE category_id = ?", (category_id,))
            
            # 删除类别
            conn.execute("DELETE FROM performance_categories WHERE id = ?", (category_id,))

    def get_category_by_id(self, category_id):
        """根据ID获取表现类别信息"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    id,
                    name,
                    description,
                    is_active,
                    created_at
                FROM performance_categories
                WHERE id = ?
            """, (category_id,))
            return cursor.fetchone()

    def get_category_by_name(self, name):
        """根据名称获取表现类别信息"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    id,
                    name,
                    description,
                    is_active,
                    created_at
                FROM performance_categories
                WHERE name = ?
            """, (name,))
            return cursor.fetchone()

    def get_all_performance_records(self, start_date=None, end_date=None):
        """获取所有表现记录
        
        Args:
            start_date: 开始日期，可选
            end_date: 结束日期，可选
            
        Returns:
            list: 记录列表，每条记录包含：记录ID、员工姓名、部门、类别、分值、描述、记录日期
        """
        with sqlite3.connect(self.db.db_path) as conn:
            query = """
                SELECT 
                    pr.id,
                    e.name as employee_name,
                    e.department,
                    pc.name as category_name,
                    pr.score,
                    pr.description,
                    pr.record_date
                FROM performance_records pr
                JOIN employees e ON pr.employee_id = e.id
                JOIN performance_categories pc ON pr.category_id = pc.id
            """
            
            params = []
            if start_date and end_date:
                query += " WHERE pr.record_date BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            
            query += " ORDER BY pr.record_date DESC, e.name"
            
            cursor = conn.execute(query, params)
            return cursor.fetchall()