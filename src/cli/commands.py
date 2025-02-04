#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from src.core.tracker import PerformanceTracker
import subprocess
import os
from pathlib import Path
from tabulate import tabulate

@click.group()
def cli():
    """员工绩效跟踪系统 - 帮助管理团队成员的日常表现和绩效评估"""
    pass

@cli.command()
@click.option('--name', prompt='员工姓名', help='员工姓名')
@click.option('--domain-account', prompt='域账号', help='域账号（字母+数字的字符串）')
@click.option('--gender', prompt='性别', help='性别')
@click.option('--hometown', prompt='家乡', help='家乡')
@click.option('--university', prompt='毕业院校', help='毕业院校')
@click.option('--major', prompt='专业', help='专业')
@click.option('--phone', prompt='联系电话', help='联系电话')
@click.option('--department', help='所属部门（可选）')
@click.option('--position', prompt='职位', help='职位')
def add_employee(name, domain_account, gender, hometown, university, major, phone, department, position):
    """添加新员工信息"""
    tracker = PerformanceTracker()
    tracker.add_employee(name, domain_account, gender, hometown, university, major, phone, department, position)
    click.echo(f'成功添加员工: {name}')

@cli.command()
@click.option('--department', prompt='默认部门', help='设置全局默认部门')
def set_default_department(department):
    """设置全局默认部门"""
    tracker = PerformanceTracker()
    tracker.update_global_setting('default_department', department, '全局默认部门设置')
    click.echo(f'成功设置默认部门: {department}')

@cli.command()
@click.option('--employee-id', prompt='员工ID', type=int, help='员工ID')
@click.option('--category', prompt='表现类别', help='表现类别(如：工作量/技术攻关/responsibility等)')
@click.option('--description', prompt='具体描述', help='表现的具体描述')
@click.option('--score', prompt='评分', type=float, help='评分(0-100)')
def add_record(employee_id, category, description, score):
    """记录员工表现"""
    tracker = PerformanceTracker()
    tracker.add_performance_record(employee_id, category, description, score)
    click.echo('成功记录员工表现')

@cli.command()
@click.option('--category', prompt='评分类别', help='评分类别')
@click.option('--weight', prompt='权重', type=float, help='权重(0-1)')
@click.option('--description', prompt='规则描述', help='规则描述')
def set_rule(category, weight, description):
    """设置评分规则"""
    tracker = PerformanceTracker()
    tracker.update_scoring_rule(category, weight, description)
    click.echo('成功更新评分规则')

@cli.command()
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def list_employees(format):
    """列出所有员工的基本信息"""
    tracker = PerformanceTracker()
    employees = tracker.get_all_employees()
    if not employees:
        click.echo('暂无员工信息')
        return
    
    headers = ['ID', '姓名', '部门', '职位']
    click.echo(click.style('\n员工列表：', fg='green', bold=True))
    click.echo(tabulate(employees, headers=headers, tablefmt=format))

@cli.command()
@click.argument('employee_id', type=int)
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def show_employee(employee_id, format):
    """显示特定员工的详细信息"""
    tracker = PerformanceTracker()
    employee = tracker.get_employee_detail(employee_id)
    if not employee:
        click.echo(f'未找到ID为 {employee_id} 的员工')
        return
    
    # 将元组转换为字典，方便格式化输出
    fields = ['ID', '姓名', '域账号', '性别', '家乡', '毕业院校', '专业', '电话', '部门', '职位', '入职日期', '创建时间']
    info = [[field, value] for field, value in zip(fields, employee)]
    
    click.echo(click.style(f'\n员工详细信息（ID: {employee_id}）：', fg='green', bold=True))
    click.echo(tabulate(info, tablefmt=format))

@cli.command()
@click.option('--frontend-port', default=3000, help='前端服务端口号')
@click.option('--backend-port', default=8000, help='后端服务端口号')
def serve(frontend_port, backend_port):
    """启动Web表单服务和后端API服务"""
    web_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) / 'src' / 'web'
    project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    click.echo('正在启动服务...')
    
    # 启动后端服务
    try:
        click.echo('正在启动后端服务...')
        backend_process = subprocess.Popen(
            ['python3', '-m', 'uvicorn', 'src.api.server:app', '--host', '0.0.0.0', '--port', str(backend_port)],
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待一段时间检查后端服务是否成功启动
        import time
        time.sleep(2)
        
        if backend_process.poll() is not None:
            # 如果进程已经结束，说明启动失败
            _, stderr = backend_process.communicate()
            click.echo(f'后端服务启动失败: {stderr.decode()}', err=True)
            return
            
        click.echo(f'后端服务访问地址: http://localhost:{backend_port}')
        click.echo(f'前端服务访问地址: http://localhost:{frontend_port}')
        
        # 启动前端服务
        try:
            subprocess.run(
                ['npm', 'run', 'dev', '--', '--port', str(frontend_port)],
                cwd=str(web_dir)
            )
        finally:
            # 确保在前端服务结束时关闭后端服务
            backend_process.terminate()
            backend_process.wait()
            
    except Exception as e:
        click.echo(f'服务启动失败: {str(e)}', err=True)
        if 'backend_process' in locals():
            backend_process.terminate()
            backend_process.wait()