def test_set_dept(runner, test_db):
    """测试设置默认部门命令"""
    result = runner.invoke(cli, ['set', 'dept', '研发部'])
    assert result.exit_code == 0
    assert '成功设置默认部门' in result.output

def test_set_perf(runner, test_db):
    """测试设置绩效周期命令"""
    result = runner.invoke(cli, ['set', 'perf', '--cycle', 'monthly'])
    assert result.exit_code == 0
    assert '成功设置绩效周期' in result.output

def test_set_rule(runner, test_db):
    """测试设置评分规则命令"""
    result = runner.invoke(cli, ['set', 'rule'], 
                         input='技术能力\n1.0\n技术实现质量与效率\n')
    assert result.exit_code == 0
    assert '成功更新评分规则' in result.output 