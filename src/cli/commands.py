#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from src.core.tracker import PerformanceTracker
import subprocess
import os
from pathlib import Path
from tabulate import tabulate
from datetime import datetime

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
@click.option('--phone', prompt='联系电话', help='联系电话（11位手机号）')
@click.option('--id-card', prompt='身份证号', help='18位身份证号码')
@click.option('--department', help='所属部门（可选）')
@click.option('--position', prompt='职级', type=click.Choice(['P2-1', 'P2-2', 'P2-3', 'P3-1', 'P3-2', 'P3-3', 'P4-1', 'P4-2', 'P4-3']), help='职级（P2-1至P4-3）')
@click.option('--join-date', prompt='入职日期', help='入职日期（格式：YYYY-MM-DD）')
def add_employee(name, domain_account, gender, hometown, university, major, phone, id_card, department, position, join_date):
    """添加新员工信息"""
    tracker = PerformanceTracker()
    tracker.add_employee(name, domain_account, gender, hometown, university, major, phone, id_card, department, position, join_date)
    click.echo(f'成功添加员工: {name}')

@cli.command()
@click.option('--department', prompt='默认部门', help='设置全局默认部门')
def set_default_department(department):
    """设置全局默认部门"""
    tracker = PerformanceTracker()
    tracker.update_global_setting('default_department', department, '全局默认部门设置')
    click.echo(f'成功设置默认部门: {department}')

@cli.command()
@click.option('--cycle', type=click.Choice(['monthly', 'quarterly']), prompt='绩效周期', help='设置绩效统计周期（monthly: 月度, quarterly: 季度）')
def set_performance_cycle(cycle):
    """设置绩效统计周期"""
    tracker = PerformanceTracker()
    tracker.update_global_setting('performance_cycle', cycle, '绩效统计周期设置')
    cycle_text = '月度' if cycle == 'monthly' else '季度'
    click.echo(f'成功设置绩效统计周期为: {cycle_text}')

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
@click.argument('employee_id', type=int)
@click.option('--force', '-f', is_flag=True, help='强制删除，不进行确认')
def delete_employee(employee_id, force):
    """删除指定员工"""
    tracker = PerformanceTracker()
    employee = tracker.get_employee_detail(employee_id)
    if not employee:
        click.echo(f'未找到ID为 {employee_id} 的员工')
        return
    
    if not force and not click.confirm(f'确定要删除员工 {employee[1]}（ID: {employee_id}）吗？'):
        click.echo('操作已取消')
        return
    
    try:
        tracker.delete_employee(employee_id)
        click.echo(f'成功删除员工 {employee[1]}（ID: {employee_id}）')
    except Exception as e:
        click.echo(f'删除员工失败：{str(e)}')

@cli.command()
@click.argument('identifier')
@click.option('--name', '-n', help='按姓名查询')
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def show_employee(identifier, name, format):
    """显示员工的详细信息
    
    可以通过ID或姓名查询（使用--by-name选项）
    
    示例：
    perf show-employee 1        # 通过ID查询
    perf show-employee -n 张三  # 通过姓名查询
    """
    tracker = PerformanceTracker()
    
    tracker = PerformanceTracker()
    if name:
        employee = tracker.get_employee_by_name(name)
        if not employee:
            click.echo(f'未找到姓名为 {name} 的员工')
            return
    else:
        try:
            employee_id = int(identifier)
            employee = tracker.get_employee_detail(employee_id)
            if not employee:
                click.echo(f'未找到ID为 {employee_id} 的员工')
                return
        except ValueError:
            click.echo('使用ID查询时，ID必须为数字')
            return
    
    # 将元组转换为字典，方便格式化输出
    fields = ['ID', '姓名', '域账号', '性别', '家乡', '毕业院校', '专业', '电话', '身份证', '部门', '职级', '入职日期']
    info = [[field, value] for field, value in zip(fields, employee)]
    
    click.echo(click.style(f'\n员工详细信息：', fg='green', bold=True))
    click.echo(tabulate(info, tablefmt=format))

@cli.command()
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def show_performance_summary(format):
    """显示当前绩效周期内所有员工的绩效统计"""
    tracker = PerformanceTracker()
    start_date, end_date = tracker.get_current_performance_cycle()
    
    if not start_date or not end_date:
        click.echo('请先设置绩效周期（使用 set_performance_cycle 命令）')
        return
    
    summary = tracker.get_performance_summary(start_date, end_date)
    if not summary:
        click.echo('当前周期内暂无绩效记录')
        return
    
    headers = ['ID', '姓名', '部门', '工作量', '技术', 'responsibility', '经验案例', '总分']
    click.echo(click.style(f'\n绩效统计（{start_date} 至 {end_date}）：', fg='green', bold=True))
    click.echo(tabulate(summary, headers=headers, tablefmt=format))

@cli.command()
@click.argument('employee_id', type=int)
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def show_performance_detail(employee_id, format):
    """显示特定员工在当前绩效周期内的详细评分记录"""
    tracker = PerformanceTracker()
    start_date, end_date = tracker.get_current_performance_cycle()
    
    if not start_date or not end_date:
        click.echo('请先设置绩效周期（使用 set_performance_cycle 命令）')
        return
    
    # 获取员工信息
    employee = tracker.get_employee_detail(employee_id)
    if not employee:
        click.echo(f'未找到ID为 {employee_id} 的员工')
        return
    
    # 获取详细评分记录
    details = tracker.get_employee_performance_detail(employee_id, start_date, end_date)
    if not details:
        click.echo('当前周期内暂无评分记录')
        return
    
    headers = ['评分类别', '描述', '得分', '权重', '记录日期']
    click.echo(click.style(f'\n{employee[1]}的绩效详情（{start_date} 至 {end_date}）：', fg='green', bold=True))
    click.echo(tabulate(details, headers=headers, tablefmt=format))

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
def get_week_prompt():
    """生成周数选择的提示信息，包含日期范围"""
    current_year = datetime.now().year
    current_week = datetime.now().isocalendar()[1] - 1
    weeks_info = []
    
    # 首先添加最近6周的信息（本周和前5周）
    start_week = max(1, current_week - 5)
    end_week = current_week
    
    for week in range(start_week, end_week + 1):
        first_day = datetime.strptime(f'{current_year}-W{week:02d}-1', '%Y-W%W-%w')
        last_day = datetime.strptime(f'{current_year}-W{week:02d}-0', '%Y-W%W-%w')
        weeks_info.append(f'{week}. 第{week}周：{first_day.strftime("%m.%d")}-{last_day.strftime("%m.%d")}' + (' (本周)' if week == current_week else ''))
    
    # 生成提示信息
    prompt = click.style('\n最近6周：', fg='green', bold=True) + '\n'
    prompt += "\n".join(weeks_info)
    
    # 添加查看所有周的选项
    prompt += "\n\n输入 'all' 查看所有周\n"
    prompt += "请输入周数或 'all'："
    
    return prompt

@cli.command()
@click.option('--week', prompt=get_week_prompt(), type=str, help='输入第几周（1-52）或输入"all"查看所有周')
def record_workload(week):
    """记录员工每周工作量排名"""
    year = datetime.now().year
    
    if week.lower() == 'all':
        # 显示所有周的信息
        all_weeks_info = []
        for w in range(1, 53):
            first_day = datetime.strptime(f'{year}-W{w:02d}-1', '%Y-W%W-%w')
            last_day = datetime.strptime(f'{year}-W{w:02d}-0', '%Y-W%W-%w')
            all_weeks_info.append(f'{w}. 第{w}周：{first_day.strftime("%m.%d")}-{last_day.strftime("%m.%d")}')
        
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
    
    if not 1 <= week <= 52:
        click.echo('无效的周数，请输入1-52之间的数字')
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
    
    click.echo(click.style('\n当前员工列表：', fg='green', bold=True))
    headers = ['ID', '姓名', '部门', '职位']
    click.echo(tabulate(employees, headers=headers))
    
    click.echo('\n请输入员工姓名，按工作量从高到低排序（空格分隔）：')
    while True:
        try:
            input_names = click.prompt('员工姓名').strip().split()
            
            # 验证输入的姓名是否都有效，并获取对应的员工ID
            employee_dict = {emp[1]: emp[0] for emp in employees}  # 建立姓名到ID的映射
            invalid_names = [name for name in input_names if name not in employee_dict]
            
            if invalid_names:
                click.echo(f'以下姓名无效：{"、".join(invalid_names)}，请重新输入')
                continue
            
            if len(input_names) != len(employees):
                click.echo('请输入所有员工的姓名')
                continue
            
            if len(input_names) != len(set(input_names)):
                click.echo('员工姓名有重复，请重新输入')
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
@click.option('--format', '-f', default='fancy_grid', help='输出格式 (simple/grid/fancy_grid)')
def list_employees(format):
    """列出所有员工的基本信息"""
    tracker = PerformanceTracker()
    employees = tracker.get_all_employees()
    if not employees:
        click.echo('暂无员工信息')
        return
    
    headers = ['ID', '姓名', '域账号', '性别', '家乡', '毕业院校', '专业', '身份证号', '手机号', '部门', '职位', '入职日期']
    click.echo(click.style('\n员工列表：', fg='green', bold=True))
    # 格式化员工数据，确保只显示需要的字段，并对敏感信息进行脱敏处理
    formatted_data = []
    for i, emp in enumerate(employees):
        # 对身份证号进行脱敏：显示前6位和后4位，中间用*号代替
        id_card = emp[7] if len(emp[7]) >= 10 else emp[7]
        masked_id_card = id_card[:6] + '*' * (len(id_card)-10) + id_card[-4:] if len(id_card) >= 10 else id_card
        
        # 对手机号进行脱敏：显示前3位和后4位，中间用*号代替
        phone = emp[8] if len(emp[8]) >= 7 else emp[8]
        masked_phone = phone[:3] + '*' * (len(phone)-7) + phone[-4:] if len(phone) >= 7 else phone
        
        # 为偶数行添加颜色
        row_data = [emp[0], emp[1], emp[2], emp[3], emp[4], emp[5], emp[6], 
                   masked_id_card, masked_phone, emp[9], emp[10], emp[11]]
        if i % 2 == 0:
            row_data = [click.style(str(cell), fg='yellow') for cell in row_data]
        else:
            row_data = [click.style(str(cell), fg='green') for cell in row_data]
        formatted_data.append(row_data)
    
    # 使用fancy_grid作为默认格式，并添加表格边框
    click.echo(tabulate(formatted_data, headers=headers, tablefmt=format))

@cli.command()
@click.argument('employee_id', type=int)
@click.option('--force', '-f', is_flag=True, help='强制删除，不进行确认')
def delete_employee(employee_id, force):
    """删除指定员工"""
    tracker = PerformanceTracker()
    employee = tracker.get_employee_detail(employee_id)
    if not employee:
        click.echo(f'未找到ID为 {employee_id} 的员工')
        return
    
    if not force and not click.confirm(f'确定要删除员工 {employee[1]}（ID: {employee_id}）吗？'):
        click.echo('操作已取消')
        return
    
    try:
        tracker.delete_employee(employee_id)
        click.echo(f'成功删除员工 {employee[1]}（ID: {employee_id}）')
    except Exception as e:
        click.echo(f'删除员工失败：{str(e)}')

@cli.command()
@click.argument('employee_id', required=False)
@click.option('--name', '-n', help='按姓名查询')
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def show_employee(employee_id, name, format):
    """显示员工的详细信息"""
    tracker = PerformanceTracker()
    
    if name:
        employee = tracker.get_employee_by_name(name)
    elif employee_id:
        try:
            employee_id = int(employee_id)
            employee = tracker.get_employee_detail(employee_id)
        except ValueError:
            click.echo('错误：员工ID必须是一个整数')
            return
    else:
        click.echo('错误：请提供员工ID或使用--name选项指定员工姓名')
        return

    if not employee:
        message = f'未找到{"姓名为 " + name if name else "ID为 " + str(employee_id)}的员工'
        click.echo(message)
        return
    
    # 将元组转换为字典，方便格式化输出
    fields = ['ID', '姓名', '域账号', '性别', '家乡', '毕业院校', '专业', '电话', '部门', '职位', '入职日期', '创建时间']
    info = [[field, value] for field, value in zip(fields, employee)]
    
    click.echo(click.style(f'\n员工详细信息（ID: {employee_id}）：', fg='green', bold=True))
    click.echo(tabulate(info, tablefmt=format))

@cli.command()
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def show_performance_summary(format):
    """显示当前绩效周期内所有员工的绩效统计"""
    tracker = PerformanceTracker()
    start_date, end_date = tracker.get_current_performance_cycle()
    
    if not start_date or not end_date:
        click.echo('请先设置绩效周期（使用 set_performance_cycle 命令）')
        return
    
    summary = tracker.get_performance_summary(start_date, end_date)
    if not summary:
        click.echo('当前周期内暂无绩效记录')
        return
    
    headers = ['ID', '姓名', '部门', '工作量', '技术', 'responsibility', '经验案例', '总分']
    click.echo(click.style(f'\n绩效统计（{start_date} 至 {end_date}）：', fg='green', bold=True))
    click.echo(tabulate(summary, headers=headers, tablefmt=format))

@cli.command()
@click.argument('employee_id', type=int)
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def show_performance_detail(employee_id, format):
    """显示特定员工在当前绩效周期内的详细评分记录"""
    tracker = PerformanceTracker()
    start_date, end_date = tracker.get_current_performance_cycle()
    
    if not start_date or not end_date:
        click.echo('请先设置绩效周期（使用 set_performance_cycle 命令）')
        return
    
    # 获取员工信息
    employee = tracker.get_employee_detail(employee_id)
    if not employee:
        click.echo(f'未找到ID为 {employee_id} 的员工')
        return
    
    # 获取详细评分记录
    details = tracker.get_employee_performance_detail(employee_id, start_date, end_date)
    if not details:
        click.echo('当前周期内暂无评分记录')
        return
    
    headers = ['评分类别', '描述', '得分', '权重', '记录日期']
    click.echo(click.style(f'\n{employee[1]}的绩效详情（{start_date} 至 {end_date}）：', fg='green', bold=True))
    click.echo(tabulate(details, headers=headers, tablefmt=format))

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