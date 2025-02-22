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