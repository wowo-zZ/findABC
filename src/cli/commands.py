#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from src.core.tracker import PerformanceTracker
import subprocess
import os
from pathlib import Path
from tabulate import tabulate
from datetime import datetime
import sqlite3

@click.group()
def cli():
    """员工绩效跟踪系统 - 帮助管理团队成员的日常表现和绩效评估"""
    pass

@cli.command('add-emp')
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

@cli.command('set-dept')
@click.option('--department', prompt='默认部门', help='设置全局默认部门')
def set_default_department(department):
    """设置全局默认部门 (set_default_department)"""
    tracker = PerformanceTracker()
    tracker.update_global_setting('default_department', department, '全局默认部门设置')
    click.echo(f'成功设置默认部门: {department}')

@cli.command('set-perf')
@click.option('--cycle', type=click.Choice(['monthly', 'quarterly']), prompt='绩效周期', help='设置绩效统计周期（monthly: 月度, quarterly: 季度）')
def set_performance_cycle(cycle):
    """设置绩效统计周期 (set_performance_cycle)"""
    tracker = PerformanceTracker()
    tracker.update_global_setting('performance_cycle', cycle, '绩效统计周期设置')
    cycle_text = '月度' if cycle == 'monthly' else '季度'
    click.echo(f'成功设置绩效统计周期为: {cycle_text}')

@cli.command('add-rec')
@click.pass_context
def add_record(ctx):
    """记录员工表现 (add_record)"""
    tracker = PerformanceTracker()
    
    # 获取并显示所有激活状态的员工
    employees = tracker.get_all_employees()
    if not employees:
        click.echo('暂无员工信息')
        return
        
    active_employees = [emp for emp in employees if emp[12]]
    if not active_employees:
        click.echo('暂无激活状态的员工')
        return
    
    # 将员工信息格式化为 "ID:姓名" 的形式，每行显示多个
    employee_info = [f"{emp[0]}:{emp[1]}" for emp in active_employees]
    formatted_info = "  ".join(employee_info)
    click.echo(click.style("\n当前激活员工列表（ID:姓名）：", fg='green'))
    click.echo(formatted_info + "\n")
    
    # 检查当前是否在有效的绩效周期内
    start_date, end_date = tracker.get_current_performance_cycle()
    if not start_date or not end_date:
        click.echo('错误：请先设置绩效统计周期（使用 set-perf 命令）')
        return

    # 先获取员工ID
    employee_id = click.prompt('请输入员工ID', type=int)
    
    # 验证员工是否存在且处于激活状态
    employee = tracker.get_employee_detail(employee_id)
    if not employee:
        click.echo(f'错误：未找到ID为 {employee_id} 的员工')
        return
    
    if not employee[12]:  # 检查是否激活
        click.echo(f'错误：员工 {employee[1]} 当前处于未激活状态，无法记录表现')
        return
    
    # 获取当前启用的表现类别
    categories = tracker.get_active_categories()
    if not categories:
        click.echo('错误：未找到任何可用的表现类别，请先添加类别')
        return
    
    click.echo(click.style('\n可选的表现类别：', fg='green'))
    for i, (name, description) in enumerate(categories, 1):
        click.echo(f'{i}. {name} - {description}')
    
    while True:
        category_input = click.prompt('请选择表现类别(输入序号或类别名称)')
        try:
            # 尝试通过序号选择
            idx = int(category_input) - 1
            if 0 <= idx < len(categories):
                category = categories[idx][0]  # 获取类别名称
                break
        except ValueError:
            # 通过名称选择
            if category_input in [cat[0] for cat in categories]:
                category = category_input
                break
        click.echo('无效的选择，请重新输入')
    
    operation = click.prompt('操作类型 (+/-)', type=click.Choice(['+', '-']))
    score = click.prompt('分值 (0-100)', type=float)
    description = click.prompt('具体描述')
    
    # 根据操作类型调整分数
    final_score = score if operation == '+' else -score
    
    try:
        # 使用当前时间作为记录时间
        tracker.add_performance_record(
            employee_id=employee_id,
            category=category,
            description=f'{"加分" if operation == "+" else "减分"}原因：{description}',
            score=final_score
        )
        
        operation_text = '加' if operation == '+' else '减'
        click.echo(click.style(f'成功为员工 {employee[1]} {operation_text}分：', fg='green'))
        click.echo(f'类别：{category}')
        click.echo(f'分值：{operation}{score}')
        click.echo(f'原因：{description}')
        click.echo(f'记录时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
    except Exception as e:
        click.echo(f'记录失败：{str(e)}')

@cli.command('set-rule')
@click.option('--category', prompt='评分类别', help='评分类别')
@click.option('--weight', prompt='权重', type=float, help='权重(0-1)')
@click.option('--description', prompt='规则描述', help='规则描述')
def set_rule(category, weight, description):
    """设置评分规则 (set_rule)"""
    tracker = PerformanceTracker()
    tracker.update_scoring_rule(category, weight, description)
    click.echo('成功更新评分规则')

@cli.command('del-emp')
@click.argument('employee_id', type=int)
@click.option('--force', '-f', is_flag=True, help='强制删除，不进行确认')
def delete_employee(employee_id, force):
    """删除指定员工 (delete_employee)"""
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

@cli.command('show-emp')
@click.argument('identifier', required=False)
@click.option('--name', '-n', help='按姓名查询')
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def show_employee(identifier, name, format):
    """显示员工的详细信息 (show_employee)"""
    tracker = PerformanceTracker()
    
    if name:
        employee = tracker.get_employee_by_name(name)
    elif identifier:
        try:
            employee_id = int(identifier)
            employee = tracker.get_employee_detail(employee_id)
        except ValueError:
            click.echo('使用ID查询时，ID必须为数字')
            return
    else:
        click.echo('错误：请提供员工ID或使用--name选项指定员工姓名')
        return
    
    if not employee:
        message = f'未找到{"姓名为 " + name if name else "ID为 " + str(identifier)}的员工'
        click.echo(message)
        return
    
    # 将元组转换为字典，方便格式化输出
    fields = ['ID', '姓名', '域账号', '性别', '家乡', '毕业院校', '专业', '电话', '身份证', '部门', '职级', '入职日期']
    info = [[field, value] for field, value in zip(fields, employee)]
    
    click.echo(click.style(f'\n员工详细信息：', fg='green', bold=True))
    click.echo(tabulate(info, tablefmt=format))

@cli.command('show-perf')
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def show_performance_summary(format):
    """显示当前绩效周期内所有员工的绩效统计 (show_performance_summary)"""
    tracker = PerformanceTracker()
    start_date, end_date = tracker.get_current_performance_cycle()
    
    if not start_date or not end_date:
        click.echo('请先设置绩效周期（使用 set-perf 命令）')
        return
    
    # 获取绩效统计和表现类别
    summary, categories = tracker.get_performance_summary(start_date, end_date)
    if not summary:
        click.echo('当前周期内暂无绩效记录')
        return

    # 动态构建表头
    headers = ['ID', '姓名', '部门', '工作承担'] + categories + ['总分']
    click.echo(click.style(f'\n绩效统计（{start_date} 至 {end_date}）：', fg='green', bold=True))
    
    # 格式化数据，添加颜色
    formatted_summary = []
    for row in summary:
        # 转换为列表以便修改
        row_data = list(row)
        # 为得分添加颜色（从工作承担开始到总分的所有列）
        for i in range(3, len(row_data)):
            score = row_data[i]
            if score > 0:
                row_data[i] = click.style(f"{score:>6.2f}", fg='green')
            elif score < 0:
                row_data[i] = click.style(f"{score:>6.2f}", fg='red')
            else:
                row_data[i] = f"{score:>6.2f}"
        formatted_summary.append(row_data)
    
    click.echo(tabulate(formatted_summary, headers=headers, tablefmt=format))

@cli.command('show-detail')
@click.argument('employee_id', type=int)
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
def show_performance_detail(employee_id, format):
    """显示特定员工在当前绩效周期内的详细评分记录 (show_performance_detail)"""
    tracker = PerformanceTracker()
    start_date, end_date = tracker.get_current_performance_cycle()
    
    if not start_date or not end_date:
        click.echo('请先设置绩效周期（使用 set-performance_cycle 命令）')
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
                score_str,  # 得分
                detail[4]   # 描述
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

@cli.command('toggle-emp')
@click.option('--employee-id', prompt='员工ID', type=int, help='员工ID')
@click.option('--active/--inactive', prompt='是否激活', help='激活或取消激活员工')
def toggle_employee_status(employee_id, active):
    """激活或取消激活员工 (toggle_employee_status)"""
    tracker = PerformanceTracker()
    try:
        tracker.toggle_employee_status(employee_id, active)
        status = '激活' if active else '取消激活'
        click.echo(f'成功{status}员工')
    except ValueError as e:
        click.echo(f'错误：{str(e)}')

@cli.command('web')
@click.option('--frontend-port', default=3000, help='前端服务端口号')
@click.option('--backend-port', default=8000, help='后端服务端口号')
def serve(frontend_port, backend_port):
    """启动Web表单服务和后端API服务 (serve)"""
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

@cli.command('rec-work')
@click.option('--week', prompt=get_week_prompt(), type=str, help='输入第几周（1-52）或输入"all"查看所有周')
def record_workload(week):
    """记录员工每周工作量排名 (record_workload)"""
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

@cli.command('list-emp')
@click.option('--format', '-f', default='fancy_grid', help='输出格式 (simple/grid/fancy_grid)')
def list_employees(format):
    """列出所有员工的基本信息 (list_employees)"""
    tracker = PerformanceTracker()
    employees = tracker.get_all_employees()
    if not employees:
        click.echo('暂无员工信息')
        return
    
    headers = ['ID', '姓名', '域账号', '性别', '家乡', '毕业院校', '专业', '身份证号', '手机号', '部门', '职位', '入职日期', '状态']
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
        
        # 根据激活状态设置颜色
        status = '已激活' if emp[12] else '未激活'
        row_data = [emp[0], emp[1], emp[2], emp[3], emp[4], emp[5], emp[6], 
                   masked_id_card, masked_phone, emp[9], emp[10], emp[11], status]
        
        # 未激活员工使用灰色，激活员工根据奇偶行使用不同颜色
        if not emp[12]:  # 未激活
            row_data = [click.style(str(cell), fg='white') for cell in row_data]
        else:  # 已激活
            if i % 2 == 0:
                row_data = [click.style(str(cell), fg='yellow') for cell in row_data]
            else:
                row_data = [click.style(str(cell), fg='green') for cell in row_data]
        formatted_data.append(row_data)
    
    # 使用fancy_grid作为默认格式，并添加表格边框
    click.echo(tabulate(formatted_data, headers=headers, tablefmt=format))

@cli.group('cat')
def category():
    """表现类别管理相关命令"""
    pass

@category.command('show')
@click.option('--format', '-f', default='simple', help='输出格式 (simple/grid/fancy_grid)')
@click.option('--all', '-a', is_flag=True, help='显示所有类别（包括已禁用的）')
def show_categories(format, all):
    """显示表现类别信息"""
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
@click.option('--name', prompt='类别名称', help='表现类别名称')
@click.option('--active/--inactive', prompt='是否启用', help='启用或禁用类别')
def toggle_category(name, active):
    """启用或禁用表现类别"""
    tracker = PerformanceTracker()
    try:
        tracker.toggle_category(name, active)
        status = '启用' if active else '禁用'
        click.echo(f'成功{status}类别: {name}')
    except Exception as e:
        click.echo(f'操作失败：{str(e)}')

@category.command('change')
def change_category():
    """修改表现类别信息"""
    tracker = PerformanceTracker()
    
    # 获取并显示所有表现类别
    categories = tracker.get_all_categories()
    if not categories:
        click.echo('错误：未找到任何表现类别')
        return
    
    # 显示所有类别
    click.echo(click.style('\n当前所有表现类别：', fg='green'))
    headers = ['序号', '类别名称', '描述', '状态']
    category_list = []
    for i, (name, description, is_active) in enumerate(categories, 1):
        status = click.style('已启用', fg='green') if is_active else click.style('已禁用', fg='red')
        category_list.append([i, name, description, status])
    click.echo(tabulate(category_list, headers=headers))
    
    # 选择要修改的类别
    while True:
        category_input = click.prompt('\n请选择要修改的类别(输入序号或类别名称)')
        try:
            # 尝试通过序号选择
            idx = int(category_input) - 1
            if 0 <= idx < len(categories):
                old_name = categories[idx][0]
                break
        except ValueError:
            # 通过名称选择
            if category_input in [cat[0] for cat in categories]:
                old_name = category_input
                break
        click.echo('无效的选择，请重新输入')
    
    # 获取当前类别信息
    old_category = next(cat for cat in categories if cat[0] == old_name)
    
    # 提示用户输入新的信息
    click.echo(click.style('\n当前类别信息：', fg='yellow'))
    click.echo(f'名称：{old_category[0]}')
    click.echo(f'描述：{old_category[1]}')
    click.echo(f'状态：{"已启用" if old_category[2] else "已禁用"}')
    
    # 获取新的信息
    new_name = click.prompt('新名称（直接回车保持不变）', default=old_category[0])
    new_description = click.prompt('新描述（直接回车保持不变）', default=old_category[1])
    new_status = click.prompt(
        '是否启用',
        type=click.Choice(['y', 'n']),
        default='y' if old_category[2] else 'n'
    ) == 'y'
    
    # 确认修改
    click.echo(click.style('\n请确认以下修改：', fg='yellow'))
    if new_name != old_category[0]:
        click.echo(f'名称：{old_category[0]} -> {new_name}')
    if new_description != old_category[1]:
        click.echo(f'描述：{old_category[1]} -> {new_description}')
    if new_status != old_category[2]:
        click.echo(f'状态：{"已启用" if old_category[2] else "已禁用"} -> {"已启用" if new_status else "已禁用"}')
    
    if not click.confirm('\n是否确认执行以上修改？'):
        click.echo('操作已取消')
        return
    
    try:
        # 执行修改
        tracker.update_category(old_name, new_name, new_description, new_status)
        click.echo(click.style('\n类别信息修改成功！', fg='green'))
    except Exception as e:
        click.echo(f'修改失败：{str(e)}')

@cli.command('add-env')
@click.option('--event', prompt='事件描述', help='具体事件描述')
def add_event_score(event):
    """根据团队事件为多名员工同时加减分 (add_event_score)"""
    tracker = PerformanceTracker()
    
    # 获取并显示所有启用的表现类别
    categories = tracker.get_active_categories()
    if not categories:
        click.echo('错误：未找到任何可用的表现类别，请先添加类别')
        return
    
    click.echo(click.style('\n可选的表现类别：', fg='green'))
    for i, (name, description) in enumerate(categories, 1):
        click.echo(f'{i}. {name} - {description}')
    
    # 获取表现类别
    while True:
        category_input = click.prompt('请选择表现类别(输入序号或类别名称)')
        try:
            # 尝试通过序号选择
            idx = int(category_input) - 1
            if 0 <= idx < len(categories):
                category = categories[idx][0]  # 获取类别名称
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

@cli.group('rec')
def record():
    """表现记录管理相关命令"""
    pass

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