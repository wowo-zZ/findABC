def test_show_perf(runner, sample_data):
    """测试显示绩效统计命令"""
    # 先添加一些表现记录
    runner.invoke(cli, ['rec', 'add'], input='1\n1\n+5\n完成新功能开发\n')
    result = runner.invoke(cli, ['show', 'perf'])
    assert result.exit_code == 0
    assert '张三' in result.output
    assert '技术能力' in result.output

def test_show_detail(runner, sample_data):
    """测试显示详细记录命令"""
    # 先添加一些表现记录
    runner.invoke(cli, ['rec', 'add'], input='1\n1\n+5\n完成新功能开发\n')
    result = runner.invoke(cli, ['show', 'detail', '1'])
    assert result.exit_code == 0
    assert '张三的绩效详情' in result.output
    assert '完成新功能开发' in result.output 