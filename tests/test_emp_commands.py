import pytest
from click.testing import CliRunner

def test_emp_add(runner, test_db):
    """测试添加员工命令"""
    result = runner.invoke(cli, ['emp', 'add'], input='张三\nzhangsan\n男\n北京\n清华大学\n计算机\n13800138000\n研发部\nP3-2\n2023-01-01\n')
    assert result.exit_code == 0
    assert '成功添加员工' in result.output

def test_emp_show(runner, sample_data):
    """测试显示员工详情命令"""
    result = runner.invoke(cli, ['emp', 'show', '1'])
    assert result.exit_code == 0
    assert '张三' in result.output
    assert '研发部' in result.output
    assert '在职' in result.output

def test_emp_toggle(runner, sample_data):
    """测试激活/禁用员工命令"""
    result = runner.invoke(cli, ['emp', 'toggle', '--employee-id', '1', '--active', 'false'])
    assert result.exit_code == 0
    assert '成功禁用员工' in result.output

def test_emp_list(runner, sample_data):
    """测试显示员工列表命令"""
    result = runner.invoke(cli, ['emp', 'list'])
    assert result.exit_code == 0
    assert '张三' in result.output
    assert '研发部' in result.output
    assert '在职' in result.output

def test_emp_list_all(runner, sample_data):
    """测试显示所有员工列表命令（包括已禁用的）"""
    # 先禁用一个员工
    runner.invoke(cli, ['emp', 'toggle', '--employee-id', '1', '--active', 'false'])
    # 然后查看所有员工
    result = runner.invoke(cli, ['emp', 'list', '--all'])
    assert result.exit_code == 0
    assert '张三' in result.output
    assert '已离职' in result.output

def test_emp_del(runner, sample_data):
    """测试删除员工命令"""
    result = runner.invoke(cli, ['emp', 'del', '1', '--force'])
    assert result.exit_code == 0
    assert '成功删除员工' in result.output

def test_emp_del_nonexistent(runner, sample_data):
    """测试删除不存在的员工"""
    result = runner.invoke(cli, ['emp', 'del', '999', '--force'])
    assert result.exit_code == 0
    assert '未找到' in result.output

def test_emp_show_nonexistent(runner, sample_data):
    """测试显示不存在的员工详情"""
    result = runner.invoke(cli, ['emp', 'show', '999'])
    assert result.exit_code == 0
    assert '未找到' in result.output 