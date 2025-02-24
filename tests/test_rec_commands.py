def test_rec_add(runner, sample_data):
    """测试添加表现记录命令"""
    result = runner.invoke(cli, ['rec', 'add'], input='1\n1\n+5\n完成新功能开发\n')
    assert result.exit_code == 0
    assert '记录添加成功' in result.output

def test_rec_env(runner, sample_data):
    """测试添加团队事件记录命令"""
    result = runner.invoke(cli, ['rec', 'env'], 
                         input='项目按期交付\n技术能力\n1\n+10\n1\ny\n')
    assert result.exit_code == 0
    assert '成功为 1 名员工添加得分记录' in result.output

def test_rec_change(runner, sample_data):
    """测试修改表现记录命令"""
    # 先添加一条记录
    runner.invoke(cli, ['rec', 'add'], input='1\n1\n+5\n完成新功能开发\n')
    # 然后修改这条记录
    result = runner.invoke(cli, ['rec', 'change'], input='1\n1\n+8\n完成新功能开发并优化性能\ny\n')
    assert result.exit_code == 0
    assert '记录修改成功' in result.output

def test_rec_list(runner, sample_data):
    """测试列出表现记录命令"""
    # 先添加一些记录
    runner.invoke(cli, ['rec', 'add'], input='1\n1\n+5\n完成新功能开发\n')
    runner.invoke(cli, ['rec', 'add'], input='1\n1\n-2\n代码质量问题\n')
    
    # 测试列出记录
    result = runner.invoke(cli, ['rec', 'list'])
    assert result.exit_code == 0
    assert '完成新功能开发' in result.output
    assert '代码质量问题' in result.output
    assert '+5.00' in result.output
    assert '-2.00' in result.output

def test_rec_list_empty(runner, sample_data):
    """测试当没有记录时的情况"""
    result = runner.invoke(cli, ['rec', 'list'])
    assert result.exit_code == 0
    assert '暂无表现记录' in result.output

def test_rec_work(runner, sample_data):
    """测试列出工作量记录命令"""
    # 先添加一些工作量记录
    tracker = sample_data
    tracker.add_workload_score(
        employee_id=1,
        week=1,
        year=2024,
        ranking_percentage=85.5,
        score=8.5,
        description="完成所有计划任务"
    )
    
    result = runner.invoke(cli, ['rec', 'work'])
    assert result.exit_code == 0
    assert '张三' in result.output
    assert '研发部' in result.output
    assert '85.50%' in result.output
    assert '+8.50' in result.output
    assert '完成所有计划任务' in result.output

def test_rec_work_empty(runner, sample_data):
    """测试当没有工作量记录时的情况"""
    result = runner.invoke(cli, ['rec', 'work'])
    assert result.exit_code == 0
    assert '暂无工作量记录' in result.output

def test_rec_work_by_week(runner, sample_data):
    """测试按周查看工作量记录命令"""
    # 先添加一些工作量记录
    tracker = sample_data
    tracker.add_workload_score(
        employee_id=1,
        week=1,
        year=2024,
        ranking_percentage=85.5,
        score=8.5,
        description="完成所有计划任务"
    )
    
    result = runner.invoke(cli, ['rec', 'work', '--week', '1', '--year', '2024'])
    assert result.exit_code == 0
    assert '张三' in result.output
    assert '研发部' in result.output
    assert '85.50%' in result.output
    assert '+8.50' in result.output
    assert '完成所有计划任务' in result.output

def test_rec_work_by_week_empty(runner, sample_data):
    """测试查看不存在记录的周"""
    result = runner.invoke(cli, ['rec', 'work', '--week', '2', '--year', '2024'])
    assert result.exit_code == 0
    assert '暂无工作量记录' in result.output 