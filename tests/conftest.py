import os
import pytest
import sqlite3
from click.testing import CliRunner
from src.cli.commands import cli
from src.core.tracker import PerformanceTracker
from src.db.database import PerformanceDB

@pytest.fixture(scope="function")
def test_db():
    """创建测试用的临时数据库"""
    # 使用临时目录存放测试数据库
    test_dir = "tests/temp"
    os.makedirs(test_dir, exist_ok=True)
    test_db_path = os.path.join(test_dir, "test.db")
    
    # 确保测试开始前数据库不存在
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # 初始化测试数据库
    db = PerformanceDB(test_db_path)
    db.init_database()
    
    yield test_db_path
    
    # 测试结束后清理数据库和临时目录
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    if os.path.exists(test_dir):
        os.rmdir(test_dir)

@pytest.fixture
def runner():
    """创建CLI测试运行器"""
    return CliRunner()

@pytest.fixture
def tracker(test_db):
    """创建测试用的PerformanceTracker实例"""
    return PerformanceTracker(test_db)

@pytest.fixture
def sample_data(tracker):
    """添加测试用的样例数据"""
    # 添加测试员工
    tracker.add_employee(
        name="张三",
        domain_account="zhangsan",
        gender="男",
        hometown="北京",
        university="清华大学",
        major="计算机科学",
        phone="13800138000",
        id_card="110101199001011234",
        department="研发部",
        position="P3-2",
        join_date="2023-01-01"
    )
    
    # 添加测试类别
    tracker.add_category("技术能力", "技术实现质量与效率")
    
    # 设置绩效周期
    tracker.update_global_setting("performance_cycle", "monthly", "绩效统计周期")
    
    return tracker 