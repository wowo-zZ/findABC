def test_cat_add(runner, test_db):
    """测试添加表现类别命令"""
    result = runner.invoke(cli, ['cat', 'add'], input='技术能力\n技术实现质量与效率\n')
    assert result.exit_code == 0
    assert '成功添加表现类别' in result.output

def test_cat_show(runner, sample_data):
    """测试显示表现类别列表命令"""
    result = runner.invoke(cli, ['cat', 'show'])
    assert result.exit_code == 0
    assert '技术能力' in result.output

def test_cat_toggle(runner, sample_data):
    """测试启用/禁用表现类别命令"""
    result = runner.invoke(cli, ['cat', 'toggle', '--name', '技术能力', '--active', 'false'])
    assert result.exit_code == 0
    assert '成功禁用类别' in result.output

def test_cat_toggle_interactive(runner, sample_data):
    """测试交互式启用/禁用表现类别命令"""
    # 选择第一个类别并禁用
    result = runner.invoke(cli, ['cat', 'toggle'], input='1\ny\n')
    assert result.exit_code == 0
    assert '成功禁用类别' in result.output

def test_cat_toggle_empty(runner, test_db):
    """测试当没有类别时的情况"""
    result = runner.invoke(cli, ['cat', 'toggle'])
    assert result.exit_code == 0
    assert '暂无表现类别' in result.output

def test_cat_del(runner, sample_data):
    """测试删除表现类别命令"""
    result = runner.invoke(cli, ['cat', 'del', '技术能力', '--force'])
    assert result.exit_code == 0
    assert '成功删除类别' in result.output

def test_cat_del_interactive(runner, sample_data):
    """测试交互式删除表现类别命令"""
    result = runner.invoke(cli, ['cat', 'del'], input='1\ny\n')
    assert result.exit_code == 0
    assert '成功删除类别' in result.output

def test_cat_del_nonexistent(runner, sample_data):
    """测试删除不存在的类别"""
    result = runner.invoke(cli, ['cat', 'del', '不存在的类别', '--force'])
    assert result.exit_code == 0
    assert '未找到类别' in result.output 