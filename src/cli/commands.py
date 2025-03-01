#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from src.core.tracker import PerformanceTracker
import subprocess
import os
from pathlib import Path
from tabulate import tabulate
from datetime import datetime, timedelta
import sqlite3

@click.group()
def cli():
    """员工绩效跟踪系统

    主要功能：

    \b
    1. 员工管理 (emp)
       - 添加、修改、删除员工信息
       - 查看员工列表和详情

    \b
    2. 表现类别管理 (cat)
       - 添加、修改、删除表现类别
       - 查看类别列表

    \b
    3. 表现记录管理 (rec)
       - 添加、修改、删除表现记录
       - 查看表现记录列表
       - 记录团队事件

    \b
    4. 工作量管理 (work)
       - 记录每周工作量排名
       - 查看工作量记录
       - 删除工作量记录

    \b
    5. 绩效统计 (show)
       - 查看绩效统计
       - 查看详细记录

    \b
    6. 系统设置 (set)
       - 设置默认部门
       - 设置绩效周期
       - 设置评分规则
    """
    pass

@cli.group('emp')
def employee():
    """员工管理相关命令
    
    \b
    emp add    : 添加新员工
    emp del    : 删除员工
    emp list   : 显示员工列表
    emp show   : 显示员工详情
    emp toggle : 激活/禁用员工
    """
    pass

@cli.group('cat')
def category():
    """表现类别管理相关命令"""
    pass

@cli.group('rec')
def record():
    """表现记录管理相关命令"""
    pass

@cli.group('show')
def show():
    """绩效查看相关命令"""
    pass

@cli.group('set')
def settings():
    """系统设置相关命令"""
    pass

@cli.group()
def work():
    """工作量管理"""
    pass

@employee.command('add')
@click.option('--name', prompt='员工姓名', help='员工姓名')
@click.option('--domain-account', prompt='域账号', help='域账号（字母+数字的字符串）')
@click.option('--gender', prompt='性别', help='性别')
@click.option('--hometown', prompt='家乡', help='家乡')
@click.option('--university', prompt='毕业院校', help='毕业院校')
@click.option('--major', prompt='专业', help='专业')
@click.option('--phone', prompt='联系电话', help='联系电话（11位手机号）')
@click.option('--id-card', prompt='身份证号', help='18位身份证号码')
@click.option('--department', help='所属部门（可选）')
@click.option('--position', prompt='职级', type=click.Choice(['P2-1', 'P2-2', 'P2-3', 'P3-1', 'P3-2', 'P3-3', 'P4-1', 'P4-2', 'P4-3']), help='职级（P2-1至P4-3）')
@click.option('--join-date', prompt='入职日期', help='入职日期（格式：YYYY-MM-DD）')
def add_employee(name, domain_account, gender, hometown, university, major, phone, id_card, department, position, join_date):
    """添加新员工信息 (add_employee)"""
    tracker = PerformanceTracker()
    tracker.add_employee(name, domain_account, gender, hometown, university, major, phone, id_card, department, position, join_date)
    click.echo(f'成功添加员工: {name}')

@employee.command('toggle')
@click.option('--employee-id', prompt='员工ID', type=int, help='员工ID')
@click.option('--active/--inactive', prompt='是否激活', help='激活或取消激活员工')
def toggle_employee_status(employee_id, active):
    """激活或取消激活员工 """
    tracker = PerformanceTracker()
    try:
        tracker.toggle_employee_status(employee_id, active)
        status = '激活' if active else '取消激活'
        click.echo(f'成功{status}员工')
    except ValueError as e:
        click.echo(f'错误：{str(e)}')

@employee.command('list')
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
@click.option('--all', '-a', is_flag=True, help='显示所有员工（包括已禁用的）')
def list_employees(format, all):
    """列出所有员工的基本信息"""
    tracker = PerformanceTracker()
    
    # 获取员工列表
    employees = tracker.get_all_employees()
    if not employees:
        click.echo('暂无员工信息')
        return
    
    # 过滤非激活员工（除非指定显示所有）
    if not all:
        employees = [emp for emp in employees if emp[12]]  # is_active 字段
    
    if not employees:
        click.echo('暂无' + ('员工信息' if all else '在职员工'))
        return
    
    # 显示员工列表
    headers = ['ID', '姓名', '部门', '职级', '状态']
    table_data = []
    
    for emp in employees:
        status = click.style('在职', fg='green') if emp[12] else click.style('已离职', fg='red')
        table_data.append([
            emp[0],  # ID
            emp[1],  # 姓名
            emp[9],  # 部门
            emp[10], # 职级
            status
        ])
    
    click.echo(click.style('\n员工列表：', fg='blue', bold=True))
    click.echo(tabulate(table_data, headers=headers, tablefmt=format))

@employee.command('del')
@click.argument('employee_id', type=int)
@click.option('--force', '-f', is_flag=True, help='强制删除，不进行确认')
def delete_employee(employee_id, force):
    """删除指定员工"""
    tracker = PerformanceTracker()
    
    # 获取员工信息
    employee = tracker.get_employee_detail(employee_id)
    if not employee:
        click.echo(f'未找到ID为 {employee_id} 的员工')
        return
    
    # 显示员工信息并确认
    click.echo(click.style('\n要删除的员工信息：', fg='yellow'))
    click.echo(f'ID: {employee[0]}')
    click.echo(f'姓名: {employee[1]}')
    click.echo(f'部门: {employee[9]}')
    click.echo(f'职级: {employee[10]}')
    click.echo(f'状态: {"在职" if employee[12] else "已离职"}')
    
    # 确认删除
    if not force and not click.confirm('\n确定要删除该员工吗？此操作不可恢复'):
        click.echo('操作已取消')
        return
    
    try:
        tracker.delete_employee(employee_id)
        click.echo(click.style(f'\n成功删除员工：{employee[1]}', fg='green'))
    except Exception as e:
        click.echo(f'删除失败：{str(e)}')

@employee.command('show')
@click.argument('employee_id', type=int)
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def show_employee(employee_id, format):
    """显示员工的详细信息"""
    tracker = PerformanceTracker()
    
    # 获取员工信息
    employee = tracker.get_employee_detail(employee_id)
    if not employee:
        click.echo(f'未找到ID为 {employee_id} 的员工')
        return
    
    # 准备显示数据
    info = [
        ['ID', employee[0]],
        ['姓名', employee[1]],
        ['域账号', employee[2]],
        ['性别', employee[3]],
        ['家乡', employee[4]],
        ['毕业院校', employee[5]],
        ['专业', employee[6]],
        ['联系电话', employee[7]],
        ['身份证号', employee[8]],
        ['部门', employee[9]],
        ['职级', employee[10]],
        ['入职日期', employee[11]],
        ['状态', click.style('在职', fg='green') if employee[12] else click.style('已离职', fg='red')],
        ['创建时间', employee[13]]
    ]
    
    # 显示信息
    click.echo(click.style(f'\n员工详细信息：', fg='blue', bold=True))
    click.echo(tabulate(info, tablefmt=format))

@category.command('list')
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
@click.option('--all', '-a', is_flag=True, help='显示所有类别（包括已禁用的）')
def show_categories(format, all):
    """显示表现类别列表"""
    tracker = PerformanceTracker()
    
    # 获取类别信息
    if all:
        categories = tracker.get_all_categories()
        title = '所有表现类别'
    else:
        categories = [(name, desc, True) for name, desc in tracker.get_active_categories()]
        title = '已启用的表现类别'
    
    if not categories:
        click.echo('暂无表现类别信息')
        return
    
    # 显示类别信息
    click.echo(click.style(f'\n{title}：', fg='green', bold=True))
    headers = ['序号', '类别名称', '描述', '状态']
    category_list = []
    
    for i, (name, description, is_active) in enumerate(categories, 1):
        # 根据状态使用不同的颜色
        if is_active:
            status = click.style('已启用', fg='green')
            row = [
                click.style(str(i), fg='green'),
                click.style(name, fg='green'),
                click.style(description, fg='green'),
                status
            ]
        else:
            status = click.style('已禁用', fg='red')
            row = [
                click.style(str(i), fg='red'),
                click.style(name, fg='red'),
                click.style(description, fg='red'),
                status
            ]
        category_list.append(row)
    
    click.echo(tabulate(category_list, headers=headers, tablefmt=format))

@category.command('add')
@click.option('--name', prompt='类别名称', help='表现类别名称')
@click.option('--description', prompt='类别描述', help='表现类别描述')
def add_category(name, description):
    """添加新的表现类别"""
    tracker = PerformanceTracker()
    try:
        tracker.add_category(name, description)
        click.echo(f'成功添加表现类别: {name}')
    except sqlite3.IntegrityError:
        click.echo(f'错误：类别 {name} 已存在')
    except Exception as e:
        click.echo(f'添加类别失败：{str(e)}')

@category.command('toggle')
@click.option('--name', type=str, help='类别名称')
def toggle_category_status(name):
    """切换表现类别的启用/禁用状态"""
    tracker = PerformanceTracker()
    
    # 如果没有提供类别名称，显示可选列表
    if not name:
        categories = tracker.get_all_categories()
        if not categories:
            click.echo('暂无表现类别')
            return
        
        # 显示类别列表供选择
        click.echo(click.style('\n现有表现类别：', fg='blue'))
        for i, cat in enumerate(categories, 1):
            status = click.style('启用', fg='green') if cat[3] else click.style('禁用', fg='red')
            click.echo(f'{i}. {cat[1]} [{status}] - {cat[2]}')
        
        # 让用户选择类别
        cat_index = click.prompt('请选择要操作的类别序号', type=int)
        if cat_index < 1 or cat_index > len(categories):
            click.echo('无效的序号')
            return
        
        # 获取选中的类别信息
        category = categories[cat_index - 1]
        name = category[1]
        current_status = category[3]
        
        # 确认操作
        new_status = not current_status
        status_str = '启用' if new_status else '禁用'
        if not click.confirm(f'是否{status_str}类别 "{name}"？'):
            click.echo('操作已取消')
            return
        
        try:
            tracker.toggle_category_status(name, new_status)
            click.echo(f'成功{status_str}类别：{name}')
        except ValueError as e:
            click.echo(f'操作失败：{str(e)}')
    else:
        # 如果提供了类别名称，先获取当前状态
        try:
            current_status = tracker.get_category_status(name)
            if current_status is None:
                click.echo(f'未找到类别：{name}')
                return
            
            # 切换状态
            new_status = not current_status
            tracker.toggle_category_status(name, new_status)
            status_str = '启用' if new_status else '禁用'
            click.echo(f'成功{status_str}类别：{name}')
        except ValueError as e:
            click.echo(f'操作失败：{str(e)}')

@category.command('change')
@click.argument('name', type=str, required=False)
def change_category(name):
    """修改表现类别信息"""
    tracker = PerformanceTracker()
    
    # 如果没有提供类别名称，显示可选列表
    if not name:
        categories = tracker.get_all_categories()
        if not categories:
            click.echo('暂无表现类别')
            return
        
        click.echo(click.style('\n当前所有表现类别：', fg='blue'))
        for i, cat in enumerate(categories, 1):
            status = click.style('启用', fg='green') if cat[3] else click.style('禁用', fg='red')
            click.echo(f'{i}. {cat[1]} [{status}] - {cat[2]}')
        
        # 让用户选择类别
        cat_index = click.prompt('请选择要修改的类别序号', type=int)
        if cat_index < 1 or cat_index > len(categories):
            click.echo('无效的序号')
            return
        
        # 获取选中的类别信息
        category = categories[cat_index - 1]
        name = category[1]
        old_description = category[2]
        old_status = category[3]
    else:
        # 获取类别信息
        category = tracker.get_category_by_name(name)
        if not category:
            click.echo(f'未找到类别：{name}')
            return
        old_description = category[2]
        old_status = category[3]
    
    # 获取新的信息
    new_name = click.prompt('新名称', default=name)
    new_description = click.prompt('新描述', default=old_description)
    new_status = click.confirm('是否启用', default=old_status)
    
    if not click.confirm('确认修改？'):
        click.echo('操作已取消')
        return
    
    try:
        tracker.update_category(name, new_name, new_description, new_status)
        click.echo(click.style('\n成功更新类别信息', fg='green'))
    except ValueError as e:
        click.echo(f'修改失败：{str(e)}')

@category.command('del')
@click.argument('category', type=str, required=False)
@click.option('--force', '-f', is_flag=True, help='强制删除，不进行确认')
def delete_category(category, force):
    """删除表现类别"""
    tracker = PerformanceTracker()
    
    # 如果没有提供类别，显示可选列表
    if not category:
        categories = tracker.get_all_categories()
        if not categories:
            click.echo('暂无表现类别')
            return
        
        # 显示类别列表供选择
        click.echo(click.style('\n现有表现类别：', fg='blue'))
        for i, cat in enumerate(categories, 1):
            status = click.style('启用', fg='green') if cat[3] else click.style('禁用', fg='red')
            click.echo(f'{i}. {cat[1]} [{status}] - {cat[2]}')
        
        # 让用户选择类别
        cat_index = click.prompt('请选择要删除的类别序号', type=int)
        if cat_index < 1 or cat_index > len(categories):
            click.echo('无效的序号')
            return
        
        # 获取选中的类别信息
        category_info = categories[cat_index - 1]
    else:
        # 尝试将输入解析为ID或名称
        category_info = None
        try:
            category_id = int(category)
            category_info = tracker.get_category_by_id(category_id)
        except ValueError:
            # 如果不是数字，则按名称查找
            category_info = tracker.get_category_by_name(category)
        
        if not category_info:
            click.echo(f'未找到类别：{category}')
            return
    
    # 显示类别信息
    click.echo(click.style('\n要删除的类别信息：', fg='yellow'))
    click.echo(f'ID: {category_info[0]}')
    click.echo(f'名称: {category_info[1]}')
    click.echo(f'描述: {category_info[2]}')
    click.echo(f'状态: {"启用" if category_info[3] else "禁用"}')
    
    # 检查是否有关联的表现记录
    record_count = tracker.get_category_record_count(category_info[1])
    if record_count > 0:
        click.echo(click.style(f'\n警告：该类别下有 {record_count} 条表现记录', fg='red'))
    
    # 确认删除
    if not force and not click.confirm('\n确定要删除该类别吗？此操作不可恢复'):
        click.echo('操作已取消')
        return
    
    try:
        tracker.delete_category(category_info[1])
        click.echo(click.style(f'\n成功删除类别：{category_info[1]}', fg='green'))
    except ValueError as e:
        click.echo(f'删除失败：{str(e)}')

@record.command('add')
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def add_record(format):
    """记录员工表现"""
    tracker = PerformanceTracker()
    
    # 获取当前绩效周期
    start_date, end_date = tracker.get_current_performance_cycle()
    if not start_date or not end_date:
        click.echo('请先设置绩效周期（使用 set-perf 命令）')
        return
    
    # 获取并显示所有激活状态的员工
    employees = tracker.get_all_employees()
    if not employees:
        click.echo('暂无员工信息')
        return
        
    active_employees = [emp for emp in employees if emp[12]]
    if not active_employees:
        click.echo('暂无激活状态的员工')
        return
    
    # 显示员工列表供选择
    click.echo(click.style("\n当前激活员工列表：", fg='green'))
    for emp in active_employees:
        click.echo(f"{emp[0]}: {emp[1]} ({emp[9]})")  # ID: 姓名 (部门)
    
    # 选择员工
    while True:
        employee_id = click.prompt('请输入员工ID', type=int)
        employee = next((emp for emp in active_employees if emp[0] == employee_id), None)
        if employee:
            break
        click.echo('无效的员工ID，请重新输入')
    
    # 获取并显示所有可用的表现类别
    categories = tracker.get_active_categories()
    if not categories:
        click.echo('错误：未找到任何可用的表现类别')
        return
    
    click.echo(click.style('\n可选的表现类别：', fg='green'))
    for i, (name, description) in enumerate(categories, 1):
        click.echo(f'{i}. {name} - {description}')
    
    # 选择表现类别
    while True:
        category_input = click.prompt('请选择表现类别(输入序号或类别名称)')
        try:
            # 尝试通过序号选择
            idx = int(category_input) - 1
            if 0 <= idx < len(categories):
                category = categories[idx][0]
                break
        except ValueError:
            # 通过名称选择
            if category_input in [cat[0] for cat in categories]:
                category = category_input
                break
        click.echo('无效的选择，请重新输入')
    
    # 获取分值
    while True:
        score_str = click.prompt('请输入分值（需要带+/-符号，如：+5 或 -3）')
        try:
            if score_str[0] not in ('+', '-'):
                click.echo('错误：分值必须带有+或-符号')
                continue
            score = float(score_str)
            break
        except ValueError:
            click.echo('错误：请输入有效的数字')
    
    # 获取描述
    description = click.prompt('请输入表现描述')
    
    # 确认添加
    click.echo(click.style('\n请确认以下信息：', fg='yellow'))
    click.echo(f'员工：{employee[1]}')
    click.echo(f'类别：{category}')
    click.echo(f'分值：{score:>+6.2f}')
    click.echo(f'描述：{description}')
    
    if not click.confirm('\n是否确认添加？'):
        click.echo('操作已取消')
        return
    
    # 执行添加
    try:
        tracker.add_performance_record(employee_id, category, description, score)
        click.echo(click.style('\n记录添加成功！', fg='green'))
    except Exception as e:
        click.echo(f'添加失败：{str(e)}')

@record.command('change')
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def change_record(format):
    """修改表现记录"""
    tracker = PerformanceTracker()
    
    # 获取当前绩效周期
    start_date, end_date = tracker.get_current_performance_cycle()
    if not start_date or not end_date:
        click.echo('请先设置绩效周期（使用 set-perf 命令）')
        return
    
    # 获取并显示所有激活状态的员工
    employees = tracker.get_all_employees()
    if not employees:
        click.echo('暂无员工信息')
        return
        
    active_employees = [emp for emp in employees if emp[12]]
    if not active_employees:
        click.echo('暂无激活状态的员工')
        return
    
    # 显示员工列表供选择
    click.echo(click.style("\n当前激活员工列表：", fg='green'))
    for emp in active_employees:
        click.echo(f"{emp[0]}: {emp[1]} ({emp[9]})")  # ID: 姓名 (部门)
    
    # 选择员工
    while True:
        employee_id = click.prompt('请输入员工ID', type=int)
        employee = next((emp for emp in active_employees if emp[0] == employee_id), None)
        if employee:
            break
        click.echo('无效的员工ID，请重新输入')
    
    # 获取该员工在当前周期内的所有表现记录
    records = tracker.get_employee_performance_records(employee_id, start_date, end_date)
    if not records:
        click.echo(f'在当前周期（{start_date} 至 {end_date}）内未找到该员工的表现记录')
        return
    
    # 显示所有记录
    click.echo(click.style(f'\n{employee[1]}的表现记录：', fg='yellow'))
    headers = ['序号', '记录ID', '类别', '分值', '描述', '记录日期']
    records_list = []
    for i, record in enumerate(records, 1):
        records_list.append([
            i,
            record[0],  # record_id
            record[2],  # category_name
            click.style(f"{record[3]:>+6.2f}", fg='green' if record[3] > 0 else 'red'),  # score
            record[4],  # description
            record[5]   # record_date
        ])
    click.echo(tabulate(records_list, headers=headers, tablefmt=format))
    
    # 选择要修改的记录
    while True:
        idx = click.prompt('\n请选择要修改的记录序号', type=int)
        if 1 <= idx <= len(records):
            record = records[idx - 1]
            break
        click.echo('无效的序号，请重新输入')
    
    # 获取新的分值
    while True:
        score_str = click.prompt('\n请输入新的分值（需要带+/-符号，如：+5 或 -3）')
        try:
            if score_str[0] not in ('+', '-'):
                click.echo('错误：分值必须带有+或-符号')
                continue
            new_score = float(score_str)
            break
        except ValueError:
            click.echo('错误：请输入有效的数字')
    
    # 获取新的描述
    new_description = click.prompt('请输入新的描述（直接回车保持不变）', default=record[4])
    
    # 确认修改
    click.echo(click.style('\n请确认以下修改：', fg='yellow'))
    if new_score != record[3]:
        click.echo(f'分值：{record[3]:>+6.2f} -> {new_score:>+6.2f}')
    if new_description != record[4]:
        click.echo(f'描述：{record[4]} -> {new_description}')
    
    if not click.confirm('\n是否确认执行以上修改？'):
        click.echo('操作已取消')
        return
    
    # 执行修改
    try:
        tracker.update_performance_record(record[0], new_score, new_description)
        click.echo(click.style('\n记录修改成功！', fg='green'))
    except Exception as e:
        click.echo(f'修改失败：{str(e)}')

@record.command('del')
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def delete_record(format):
    """删除表现记录"""
    tracker = PerformanceTracker()
    
    # 获取当前绩效周期
    start_date, end_date = tracker.get_current_performance_cycle()
    if not start_date or not end_date:
        click.echo('请先设置绩效周期（使用 set-perf 命令）')
        return
    
    # 获取并显示所有激活状态的员工
    employees = tracker.get_all_employees()
    if not employees:
        click.echo('暂无员工信息')
        return
        
    active_employees = [emp for emp in employees if emp[12]]
    if not active_employees:
        click.echo('暂无激活状态的员工')
        return
    
    # 显示员工列表供选择
    click.echo(click.style("\n当前激活员工列表：", fg='green'))
    for emp in active_employees:
        click.echo(f"{emp[0]}: {emp[1]} ({emp[9]})")  # ID: 姓名 (部门)
    
    # 选择员工
    while True:
        employee_id = click.prompt('请输入员工ID', type=int)
        employee = next((emp for emp in active_employees if emp[0] == employee_id), None)
        if employee:
            break
        click.echo('无效的员工ID，请重新输入')
    
    # 获取该员工在当前周期内的所有表现记录
    records = tracker.get_employee_performance_records(employee_id, start_date, end_date)
    if not records:
        click.echo(f'在当前周期（{start_date} 至 {end_date}）内未找到该员工的表现记录')
        return
    
    # 显示所有记录
    click.echo(click.style(f'\n{employee[1]}的表现记录：', fg='yellow'))
    headers = ['序号', '记录ID', '类别', '分值', '描述', '记录日期']
    records_list = []
    for i, record in enumerate(records, 1):
        records_list.append([
            i,
            record[0],  # record_id
            record[2],  # category_name
            click.style(f"{record[3]:>+6.2f}", fg='green' if record[3] > 0 else 'red'),  # score
            record[4],  # description
            record[5]   # record_date
        ])
    click.echo(tabulate(records_list, headers=headers, tablefmt=format))
    
    # 选择要删除的记录
    while True:
        idx = click.prompt('\n请选择要删除的记录序号', type=int)
        if 1 <= idx <= len(records):
            record = records[idx - 1]
            break
        click.echo('无效的序号，请重新输入')
    
    # 确认删除
    click.echo(click.style('\n请确认要删除以下记录：', fg='yellow'))
    click.echo(f'员工：{employee[1]}')
    click.echo(f'类别：{record[2]}')
    click.echo(f'分值：{record[3]:>+6.2f}')
    click.echo(f'描述：{record[4]}')
    click.echo(f'记录日期：{record[5]}')
    
    if not click.confirm('\n是否确认删除？', abort=True):
        click.echo('操作已取消')
        return
    
    # 执行删除
    try:
        tracker.delete_performance_record(record[0])
        click.echo(click.style('\n记录删除成功！', fg='green'))
    except Exception as e:
        click.echo(f'删除失败：{str(e)}')

@record.command('env')
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def add_event_score(format):
    """记录团队事件相关表现"""
    tracker = PerformanceTracker()
    
    # 获取当前绩效周期
    start_date, end_date = tracker.get_current_performance_cycle()
    if not start_date or not end_date:
        click.echo('请先设置绩效周期（使用 set-perf 命令）')
        return
    
    # 获取事件描述
    event = click.prompt('请输入事件描述')
    
    # 获取并显示所有可用的表现类别
    categories = tracker.get_active_categories()
    if not categories:
        click.echo('错误：未找到任何可用的表现类别')
        return
    
    click.echo(click.style('\n可选的表现类别：', fg='green'))
    for i, (name, description) in enumerate(categories, 1):
        click.echo(f'{i}. {name} - {description}')
    
    # 选择表现类别
    while True:
        category_input = click.prompt('请选择表现类别(输入序号或类别名称)')
        try:
            # 尝试通过序号选择
            idx = int(category_input) - 1
            if 0 <= idx < len(categories):
                category = categories[idx][0]
                break
        except ValueError:
            # 通过名称选择
            if category_input in [cat[0] for cat in categories]:
                category = category_input
                break
        click.echo('无效的选择，请重新输入')
    
    # 获取并显示所有激活状态的员工
    employees = tracker.get_all_employees()
    if not employees:
        click.echo('暂无员工信息')
        return
        
    active_employees = [emp for emp in employees if emp[12]]
    if not active_employees:
        click.echo('暂无激活状态的员工')
        return
    
    # 显示员工列表供选择
    click.echo(click.style("\n当前激活员工列表：", fg='green'))
    for emp in active_employees:
        click.echo(f"{emp[0]}: {emp[1]} ({emp[9]})")  # ID: 姓名 (部门)
    
    # 选择加分模式
    mode = click.prompt(
        '请选择加分模式',
        type=click.Choice(['1', '2']),
        show_choices=False,
        prompt_suffix='\n1. 统一加分（为多名员工统一加分）\n2. 单独加分（为每名员工单独设置分值）\n请输入(1/2)：'
    )
    
    employee_scores = []
    if mode == '1':
        # 统一加分模式
        while True:
            try:
                # 获取统一分值
                score_str = click.prompt('请输入统一分值（需要带+/-符号，如：+5 或 -3）')
                if score_str[0] not in ('+', '-'):
                    click.echo('错误：分值必须带有+或-符号')
                    continue
                score = float(score_str)
                
                # 获取员工ID列表
                ids_input = click.prompt('请输入员工ID列表（多个ID用逗号分隔，如：1,2,3）')
                employee_ids = [int(id.strip()) for id in ids_input.split(',')]
                
                # 验证所有ID是否有效
                invalid_ids = [id for id in employee_ids if not any(emp[0] == id and emp[12] for emp in employees)]
                if invalid_ids:
                    click.echo(f'错误：以下ID无效或对应员工未激活：{invalid_ids}')
                    continue
                
                # 为每个员工添加相同的分值
                employee_scores = [(eid, score) for eid in employee_ids]
                break
                
            except ValueError:
                click.echo('错误：请输入有效的分值和ID列表')
    else:
        # 单独加分模式
        while True:
            score_input = click.prompt('请输入员工ID和分值（格式：ID1,分值1;ID2,分值2 例如：1,+5;2,-3）')
            try:
                # 解析输入
                pairs = score_input.strip().split(';')
                employee_scores = []
                invalid_ids = []
                
                for pair in pairs:
                    if not pair.strip():
                        continue
                    id_str, score_str = pair.strip().split(',')
                    employee_id = int(id_str.strip())
                    
                    # 验证员工ID是否有效
                    if not any(emp[0] == employee_id and emp[12] for emp in employees):
                        invalid_ids.append(employee_id)
                        continue
                    
                    # 解析分值（支持+/-符号）
                    score_str = score_str.strip()
                    if score_str[0] not in ('+', '-'):
                        click.echo('错误：分值必须带有+或-符号')
                        employee_scores = []
                        break
                    score = float(score_str)
                    
                    employee_scores.append((employee_id, score))
                
                if invalid_ids:
                    click.echo(f'错误：以下ID无效或对应员工未激活：{invalid_ids}')
                    continue
                    
                if employee_scores:
                    break
                    
            except ValueError:
                click.echo('错误：输入格式不正确，请使用正确的格式（ID1,分值1;ID2,分值2）')
    
    # 确认操作
    click.echo(click.style('\n请确认以下操作：', fg='yellow'))
    click.echo(f'事件描述：{event}')
    click.echo(f'表现类别：{category}')
    click.echo(f'加分模式：{"统一加分" if mode == "1" else "单独加分"}')
    click.echo('\n参与员工及分值：')
    
    # 显示详细的加分信息
    headers = ['姓名', '部门', '分值']
    details = []
    for emp_id, score in employee_scores:
        emp = next(emp for emp in active_employees if emp[0] == emp_id)
        score_str = click.style(f"{score:>+6.2f}", fg='green' if score > 0 else 'red')
        details.append([emp[1], emp[9], score_str])
    click.echo(tabulate(details, headers=headers))
    
    if not click.confirm('\n是否确认执行以上操作？'):
        click.echo('操作已取消')
        return
    
    # 执行加分操作
    success_count = 0
    for employee_id, score in employee_scores:
        try:
            description = f'团队事件：{event}'
            tracker.add_performance_record(
                employee_id=employee_id,
                category=category,
                description=description,
                score=score
            )
            success_count += 1
        except Exception as e:
            click.echo(f'为员工ID {employee_id} 添加记录时出错：{str(e)}')
    
    # 显示执行结果
    if success_count > 0:
        click.echo(click.style(f'\n成功为 {success_count} 名员工添加得分记录：', fg='green'))
        click.echo(f'类别：{category}')
        click.echo(f'事件：{event}')
        click.echo(f'记录时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    else:
        click.echo('操作失败：未能成功添加任何记录')

@show.command('perf')
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def show_performance_summary(format):
    """显示当前绩效周期内所有员工的绩效统计"""
    tracker = PerformanceTracker()
    
    # 获取当前绩效周期
    start_date, end_date = tracker.get_current_performance_cycle()
    if not start_date or not end_date:
        click.echo('请先设置绩效周期（使用 set-perf 命令）')
        return
    
    # 获取绩效统计数据
    summary_data, categories = tracker.get_performance_summary(start_date, end_date)
    if not summary_data:
        click.echo('当前周期内暂无绩效数据')
        return
    
    # 显示统计信息
    click.echo(click.style(f'\n当前绩效周期（{start_date} 至 {end_date}）统计：', fg='green', bold=True))
    
    # 准备表格数据
    headers = ['员工ID', '姓名', '部门', '工作承担', *categories, '总分']
    table_data = []
    
    for row in summary_data:
        emp_id = row[0]
        name = row[1]
        department = row[2]
        workload_score = click.style(f"{row[3]:>6.2f}", fg='blue')
        category_scores = []
        for i, cat in enumerate(categories):
            score = row[4 + i]
            score_str = click.style(f"{score:>6.2f}", fg='green' if score > 0 else 'red')
            category_scores.append(score_str)
        total_score = click.style(f"{row[-1]:>6.2f}", fg='yellow', bold=True)
        
        table_data.append([emp_id, name, department, workload_score, *category_scores, total_score])
    
    click.echo(tabulate(table_data, headers=headers, tablefmt=format))

@show.command('detail')
@click.argument('employee_id', type=int)
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def show_performance_detail(employee_id, format):
    """显示特定员工的详细绩效记录"""
    tracker = PerformanceTracker()
    
    # 获取当前绩效周期
    start_date, end_date = tracker.get_current_performance_cycle()
    if not start_date or not end_date:
        click.echo('请先设置绩效周期（使用 set-perf 命令）')
        return
    
    # 获取员工信息
    employee = tracker.get_employee_detail(employee_id)
    if not employee:
        click.echo(f'未找到ID为 {employee_id} 的员工')
        return
    
    click.echo(click.style(f'\n{employee[1]}的绩效详情（{start_date} 至 {end_date}）：', fg='green', bold=True))
    
    # 获取工作承担得分记录
    workload_details = tracker.get_employee_workload_detail(employee_id, start_date, end_date)
    if workload_details:
        click.echo(click.style('\n工作承担得分：', fg='yellow'))
        workload_headers = ['年份', '周数', '得分', '描述']
        formatted_workload = []
        for detail in workload_details:
            score = detail[2]
            score_str = click.style(f"{score:>6.2f}", fg='green' if score > 0 else 'red')
            formatted_workload.append([
                detail[3],  # 年份
                detail[0],  # 周数
                score_str, # 得分
                detail[4]  # 描述
            ])
        click.echo(tabulate(formatted_workload, headers=workload_headers, tablefmt=format))
    
    # 获取表现得分记录
    performance_details = tracker.get_employee_performance_detail(employee_id, start_date, end_date)
    if performance_details:
        click.echo(click.style('\n表现得分：', fg='yellow'))
        perf_headers = ['评分类别', '描述', '得分', '记录日期']
        formatted_perf = []
        for detail in performance_details:
            score = detail[2]
            score_str = click.style(f"{score:>6.2f}", fg='green' if score > 0 else 'red')
            formatted_perf.append([
                detail[0],  # 类别
                detail[1],  # 描述
                score_str, # 得分
                detail[3]  # 日期
            ])
        click.echo(tabulate(formatted_perf, headers=perf_headers, tablefmt=format))
    
    if not workload_details and not performance_details:
        click.echo('当前周期内暂无评分记录')

@settings.command('dept')
@click.argument('department')
def set_department(department):
    """设置默认部门"""
    tracker = PerformanceTracker()
    try:
        tracker.update_global_setting('default_department', department, '默认部门')
        click.echo(f'成功设置默认部门为：{department}')
    except Exception as e:
        click.echo(f'设置失败：{str(e)}')

@settings.command('perf')
@click.option('--cycle', type=click.Choice(['monthly', 'quarterly']), prompt='请选择绩效周期类型', help='monthly: 月度, quarterly: 季度')
def set_performance_cycle(cycle):
    """设置绩效统计周期"""
    tracker = PerformanceTracker()
    try:
        tracker.update_global_setting('performance_cycle', cycle, '绩效统计周期')
        click.echo(f'成功设置绩效周期为：{"月度" if cycle == "monthly" else "季度"}')
    except Exception as e:
        click.echo(f'设置失败：{str(e)}')

@settings.command('rule')
@click.option('--category', prompt='评分类别', help='评分类别')
@click.option('--weight', prompt='权重', type=float, help='权重值')
@click.option('--description', prompt='规则描述', help='规则描述')
def set_scoring_rule(category, weight, description):
    """设置评分规则"""
    tracker = PerformanceTracker()
    try:
        tracker.update_scoring_rule(category, weight, description)
        click.echo(f'成功更新评分规则：{category}')
    except Exception as e:
        click.echo(f'设置失败：{str(e)}')

@record.command('list')
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
@click.option('--all', '-a', is_flag=True, help='显示所有记录（不限制在当前绩效周期内）')
def list_records(format, all):
    """列出表现记录"""
    tracker = PerformanceTracker()
    
    # 获取当前绩效周期
    start_date, end_date = tracker.get_current_performance_cycle()
    if not start_date or not end_date:
        click.echo('请先设置绩效周期（使用 set perf 命令）')
        return
    
    # 获取记录
    records = tracker.get_all_performance_records(None if all else start_date, None if all else end_date)
    if not records:
        click.echo('暂无表现记录')
        return
    
    # 显示记录
    click.echo(click.style(f'\n表现记录列表（{start_date} 至 {end_date}）：', fg='blue'))
    
    headers = ['记录ID', '员工', '部门', '类别', '分值', '描述', '记录日期']
    table_data = []
    
    for record in records:
        score_str = click.style(f"{record[4]:>+6.2f}", fg='green' if record[4] > 0 else 'red')
        table_data.append([
            record[0],  # 记录ID
            record[1],  # 员工姓名
            record[2],  # 部门
            record[3],  # 类别
            score_str,  # 分值
            record[5],  # 描述
            record[6]   # 记录日期
        ])
    
    click.echo(tabulate(table_data, headers=headers, tablefmt=format))

@record.command('work')
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
@click.option('--all', '-a', is_flag=True, help='显示所有记录（不限制在当前绩效周期内）')
@click.option('--week', '-w', type=int, help='查看指定周的记录')
@click.option('--year', '-y', type=int, default=lambda: datetime.now().year, help='查看指定年份的记录')
def list_workload_records(format, all, week, year):
    """列出工作量记录"""
    tracker = PerformanceTracker()
    
    if week:
        # 查看指定周的记录
        if not 1 <= week <= 53:
            click.echo('无效的周数，请输入1-53之间的数字')
            return
        
        # 获取指定周的起止日期
        first_day = datetime(year, 1, 1)
        week_start = first_day - timedelta(days=first_day.isoweekday() - 1)
        week_start = week_start + timedelta(weeks=week-1)
        week_end = week_start + timedelta(days=6)
        
        # 验证周数是否属于指定年份
        if week_start.isocalendar()[0] != year:
            click.echo(f'第{week}周不属于{year}年')
            return
        
        # 获取指定周的记录
        records = tracker.get_workload_records_by_week(week, year)
        if not records:
            click.echo(f'{year}年第{week}周暂无工作量记录')
            return
        
        # 显示记录
        click.echo(click.style(
            f'\n{year}年第{week}周工作量记录（{week_start.strftime("%m.%d")}-{week_end.strftime("%m.%d")}）：',
            fg='blue'
        ))
    else:
        # 获取当前绩效周期
        start_date, end_date = tracker.get_current_performance_cycle()
        if not start_date or not end_date:
            click.echo('请先设置绩效周期（使用 set perf 命令）')
            return
        
        # 获取记录
        records = tracker.get_all_workload_records(None if all else start_date, None if all else end_date)
        if not records:
            click.echo('暂无工作量记录')
            return
        
        # 显示记录
        click.echo(click.style(f'\n工作量记录列表（{start_date} 至 {end_date}）：', fg='blue'))
    
    headers = ['员工', '部门', '年份', '周数', '排名百分比', '得分', '描述']
    table_data = []
    
    for record in records:
        score_str = click.style(f"{record[5]:>+6.2f}", fg='green' if record[5] > 0 else 'red')
        percentage_str = f"{record[4]:>6.2f}%"
        table_data.append([
            record[1],  # 员工姓名
            record[2],  # 部门
            record[3],  # 年份
            record[0],  # 周数
            percentage_str,  # 排名百分比
            score_str,  # 得分
            record[6]   # 描述
        ])
    
    click.echo(tabulate(table_data, headers=headers, tablefmt=format))

def get_week_prompt():
    """获取周数提示信息"""
    now = datetime.now()
    # 使用 isocalendar() 获取 ISO 周数
    year, week, _ = now.isocalendar()
    return f'输入第几周（1-53）或输入"all"查看所有周 [当前第{week}周]'

@work.command('add')
@click.option('--week', prompt=get_week_prompt(), type=str, help='输入第几周（1-53）或输入"all"查看所有周')
def add_workload(week):
    """记录每周工作量排名"""
    now = datetime.now()
    year = now.year
    
    if week.lower() == 'all':
        # 显示所有周的信息
        all_weeks_info = []
        # 获取本年第一天和最后一天
        first_day = datetime(year, 1, 1)
        last_day = datetime(year, 12, 31)
        
        # 获取本年第一周的开始日期
        first_week_start = first_day - timedelta(days=first_day.isoweekday() - 1)
        
        current_date = first_week_start
        while current_date <= last_day:
            iso_year, iso_week, _ = current_date.isocalendar()
            if iso_year == year:
                week_start = current_date
                week_end = current_date + timedelta(days=6)
                all_weeks_info.append(
                    f'{iso_week}. 第{iso_week}周：{week_start.strftime("%m.%d")}-{week_end.strftime("%m.%d")}'
                )
            current_date += timedelta(days=7)
        
        click.echo(click.style('\n本年度所有周：', fg='green', bold=True))
        click.echo('\n'.join(all_weeks_info))
        
        # 让用户重新选择周数
        week = click.prompt('请输入要记录的周数', type=int)
    else:
        try:
            week = int(week)
        except ValueError:
            click.echo('请输入有效的周数或"all"')
            return
    
    if not 1 <= week <= 53:
        click.echo('无效的周数，请输入1-53之间的数字')
        return
    
    # 验证周数是否属于当前年份
    test_date = datetime(year, 1, 1) + timedelta(weeks=week-1)
    if test_date.isocalendar()[0] != year:
        click.echo(f'第{week}周不属于{year}年')
        return

    tracker = PerformanceTracker()
    
    # 检查是否已有记录
    existing_record = tracker.get_workload_record(week, year)
    if existing_record:
        if not click.confirm('该周已有工作量记录，是否要修改？'):
            return
    
    # 获取所有员工列表
    employees = tracker.get_all_employees()
    if not employees:
        click.echo('暂无员工信息')
        return
    
    # 过滤出激活状态的员工
    active_employees = [emp for emp in employees if emp[12]]  # emp[12]是is_active字段
    if not active_employees:
        click.echo('暂无激活状态的员工')
        return
    
    click.echo(click.style('\n当前激活员工列表：', fg='green', bold=True))
    headers = ['ID', '姓名', '部门', '职位']
    click.echo(tabulate([(emp[0], emp[1], emp[9], emp[10]) for emp in active_employees], headers=headers))
    
    click.echo('\n请输入员工姓名，按工作量从高到低排序（空格分隔）：')
    while True:
        try:
            input_names = click.prompt('员工姓名').strip().split()
            
            # 验证输入的姓名是否都有效，并获取对应的员工ID
            employee_dict = {emp[1]: emp[0] for emp in active_employees}  # 建立姓名到ID的映射
            invalid_names = [name for name in input_names if name not in employee_dict]
            
            if invalid_names:
                click.echo(f'以下姓名无效：{"、".join(invalid_names)}，请重新输入')
                continue
            
            if len(input_names) != len(active_employees):
                missing_names = set(emp[1] for emp in active_employees) - set(input_names)
                click.echo(f'请输入所有激活状态员工的姓名，当前缺少：{", ".join(missing_names)}')
                continue
            
            if len(input_names) != len(set(input_names)):
                # 找出重复的姓名
                duplicate_names = [name for name in input_names if input_names.count(name) > 1]
                duplicate_names = list(set(duplicate_names))  # 去重，每个重复姓名只显示一次
                click.echo(f'以下员工姓名有重复：{"、".join(duplicate_names)}，请重新输入')
                continue
            
            # 将姓名转换为ID
            employee_ids = [employee_dict[name] for name in input_names]
            break
        except ValueError:
            click.echo('输入格式错误，请输入有效的员工姓名（用空格分隔）')
    
    # 计算每个员工的得分
    total_employees = len(employee_ids)
    top_30_count = int(total_employees * 0.3)
    mid_30_count = int(total_employees * 0.3)
    
    scores = []
    for i, eid in enumerate(employee_ids):
        if i < top_30_count:
            score = 10
        elif i < top_30_count + mid_30_count:
            score = 8
        else:
            score = 7
        scores.append((eid, score))
    
    # 显示评分结果
    click.echo('\n评分结果：')
    result_data = []
    for eid, score in scores:
        emp = next(emp for emp in employees if emp[0] == eid)
        result_data.append([emp[1], score])
    
    click.echo(tabulate(result_data, headers=['姓名', '得分']))
    
    if click.confirm('确认保存以上评分结果？'):
        # 保存到数据库
        for eid, score in scores:
            emp = next(emp for emp in employees if emp[0] == eid)
            ranking_percentage = employee_ids.index(eid) / total_employees * 100
            tracker.add_workload_score(eid, week, year, ranking_percentage, score, 
                                     f'{year}年第{week}周工作量评分')
        
        click.echo('评分结果已保存')

@work.command('list')
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
@click.option('--all', '-a', is_flag=True, help='显示所有记录（不限制在当前绩效周期内）')
@click.option('--week', '-w', type=int, help='查看指定周的记录')
@click.option('--year', '-y', type=int, default=lambda: datetime.now().year, help='查看指定年份的记录')
def list_workload(format, all, week, year):
    """列出工作量记录"""
    tracker = PerformanceTracker()
    
    if week:
        # 查看指定周的记录
        if not 1 <= week <= 53:
            click.echo('无效的周数，请输入1-53之间的数字')
            return
        
        # 获取指定周的起止日期
        first_day = datetime(year, 1, 1)
        week_start = first_day - timedelta(days=first_day.isoweekday() - 1)
        week_start = week_start + timedelta(weeks=week-1)
        week_end = week_start + timedelta(days=6)
        
        # 验证周数是否属于指定年份
        if week_start.isocalendar()[0] != year:
            click.echo(f'第{week}周不属于{year}年')
            return
        
        # 获取指定周的记录
        records = tracker.get_workload_records_by_week(week, year)
        if not records:
            click.echo(f'{year}年第{week}周暂无工作量记录')
            return
        
        # 显示记录
        click.echo(click.style(
            f'\n{year}年第{week}周工作量记录（{week_start.strftime("%m.%d")}-{week_end.strftime("%m.%d")}）：',
            fg='blue'
        ))
    else:
        # 获取当前绩效周期
        start_date, end_date = tracker.get_current_performance_cycle()
        if not start_date or not end_date:
            click.echo('请先设置绩效周期（使用 set perf 命令）')
            return
        
        # 获取记录
        records = tracker.get_all_workload_records(None if all else start_date, None if all else end_date)
        if not records:
            click.echo('暂无工作量记录')
            return
        
        # 显示记录
        click.echo(click.style(f'\n工作量记录列表（{start_date} 至 {end_date}）：', fg='blue'))
    
    # 显示记录表格
    headers = ['员工', '部门', '年份', '周数', '排名百分比', '得分', '描述']
    table_data = []
    
    for record in records:
        score_str = click.style(f"{record[5]:>+6.2f}", fg='green' if record[5] > 0 else 'red')
        percentage_str = f"{record[4]:>6.2f}%"
        table_data.append([
            record[1],  # 员工姓名
            record[2],  # 部门
            record[3],  # 年份
            record[0],  # 周数
            percentage_str,  # 排名百分比
            score_str,  # 得分
            record[6]   # 描述
        ])
    
    click.echo(tabulate(table_data, headers=headers, tablefmt=format))

@work.command('del')
@click.option('--week', '-w', type=int, help='要删除的周数')
@click.option('--year', '-y', type=int, default=lambda: datetime.now().year, help='年份')
@click.option('--force', '-f', is_flag=True, help='强制删除，不进行确认')
def delete_workload(week, year, force):
    """删除工作量记录"""
    if not week:
        # 显示可选的周数列表
        tracker = PerformanceTracker()
        records = tracker.get_workload_weeks(year)
        if not records:
            click.echo(f'{year}年暂无工作量记录')
            return
        
        click.echo(click.style(f'\n{year}年已记录的工作周：', fg='blue'))
        for record in records:
            week_num = record[0]
            first_day = datetime(year, 1, 1)
            week_start = first_day - timedelta(days=first_day.isoweekday() - 1)
            week_start = week_start + timedelta(weeks=week_num-1)
            week_end = week_start + timedelta(days=6)
            click.echo(f'第{week_num}周（{week_start.strftime("%m.%d")}-{week_end.strftime("%m.%d")}）')
        
        week = click.prompt('请选择要删除的周数', type=int)
    
    if not 1 <= week <= 53:
        click.echo('无效的周数，请输入1-53之间的数字')
        return
    
    tracker = PerformanceTracker()
    
    # 获取该周的记录
    records = tracker.get_workload_records_by_week(week, year)
    if not records:
        click.echo(f'{year}年第{week}周暂无工作量记录')
        return
    
    # 显示将要删除的记录
    click.echo(click.style(f'\n{year}年第{week}周的工作量记录：', fg='blue'))
    headers = ['员工', '部门', '排名百分比', '得分']
    table_data = []
    for record in records:
        score_str = click.style(f"{record[5]:>+6.2f}", fg='green' if record[5] > 0 else 'red')
        percentage_str = f"{record[4]:>6.2f}%"
        table_data.append([
            record[1],  # 员工姓名
            record[2],  # 部门
            percentage_str,  # 排名百分比
            score_str,  # 得分
        ])
    click.echo(tabulate(table_data, headers=headers))
    
    if not force and not click.confirm('\n确定要删除这些记录吗？此操作不可恢复'):
        click.echo('操作已取消')
        return
    
    # 删除记录
    tracker.delete_workload_records(week, year)
    click.echo(click.style('\n成功删除工作量记录', fg='green'))
