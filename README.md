# 员工绩效跟踪系统

## 项目简介

一个用于管理和跟踪团队成员日常表现和绩效评估的系统。系统支持员工信息管理、绩效记录、表现类别管理等功能，提供命令行方式使用。

## 主要功能

### 1. 员工管理 (`perf emp`)
- `emp add` - 添加新员工
- `emp del` - 删除员工信息
- `emp show` - 查看员工列表
  - 按职级和职等排序显示
  - 支持查看所有员工或仅显示在职员工
- `emp toggle` - 激活/禁用员工

### 2. 表现类别管理 (`perf cat`)
- `cat show` - 查看表现类别列表
  - `--all` 显示所有类别（包括已禁用的）
- `cat add` - 添加新的表现类别
- `cat toggle` - 启用/禁用表现类别
- `cat change` - 修改表现类别信息

### 3. 表现记录管理 (`perf rec`)
- `rec add` - 添加单个表现记录
- `rec del` - 删除表现记录
- `rec change` - 修改表现记录
- `rec env` - 记录团队事件
  - 支持统一加分和单独加分两种模式
  - 可以同时为多名员工添加得分记录

### 4. 绩效查看 (`perf show`)
- `show perf` - 查看绩效统计
  - 显示工作承担得分和各表现类别得分
  - 自动计算总分并排序
  - 支持自定义表格格式（simple/grid/fancy_grid）
- `show detail <employee_id>` - 查看详细记录
  - 显示工作承担记录
  - 显示表现得分记录
  - 支持自定义表格格式

### 5. 系统设置 (`perf set`)
- `set dept <department>` - 设置默认部门
  - 用于新员工入职时的默认部门设置
- `set perf` - 设置绩效统计周期
  - 支持月度（monthly）和季度（quarterly）两种模式
  - 影响绩效统计的时间范围
- `set rule` - 设置评分规则
  - 设置各评分类别的权重
  - 添加规则说明

## 项目结构

```
├── data/               # 数据库文件目录
├── src/                # 源代码目录
│   ├── cli/           # 命令行工具
│   ├── core/          # 核心业务逻辑
│   ├── db/            # 数据库操作
│   └── utils/         # 工具函数
├── tests/             # 测试文件
└── requirements.txt   # Python依赖
```

## 安装说明

1. 克隆项目到本地
```bash
git clone [项目地址]
cd performance-tracker
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 初始化数据库
```bash
python -m src.db.database
```

## 数据库设计

### 主要表结构

1. employees - 员工信息表
   - id: 员工ID
   - name: 姓名
   - domain_account: 域账号
   - department: 部门
   - position: 职级职等
   - is_active: 是否在职

2. performance_categories - 表现类别表
   - id: 类别ID
   - name: 类别名称
   - description: 类别描述
   - is_active: 是否启用

3. performance_records - 表现记录表
   - employee_id: 员工ID
   - category_id: 类别ID
   - description: 表现描述
   - score: 得分
   - record_date: 记录日期

4. workload_scores - 工作承担评分表
   - employee_id: 员工ID
   - week_number: 周数
   - year: 年份
   - score: 得分
   - description: 描述

## 评分规则说明

系统采用两个维度的评分机制：

1. 工作承担得分
   - 来自每周工作量评分的总分
   - 反映日常工作的完成情况

2. 表现得分
   - 来自各类表现评价的得分总和
   - 类别可配置，支持灵活扩展

最终得分为工作承担得分与表现得分的总和。

## 注意事项

1. 所有得分操作都需要在有效的绩效周期内进行
2. 表现类别必须处于启用状态才能使用
3. 只能为激活状态的员工记录得分
4. 分值必须带有正负号（如：+5, -3）
5. 建议定期备份数据库文件

## 使用示例

1. 设置系统参数
```bash
# 设置默认部门
perf set dept "研发部"

# 设置绩效周期为季度
perf set perf --cycle quarterly

# 设置评分规则
perf set rule --category "技术能力" --weight 1.0 --description "技术实现质量与效率"
```

2. 查看绩效信息
```bash
# 查看所有员工的绩效统计
perf show perf --format grid

# 查看特定员工的详细记录
perf show detail 1 --format fancy_grid
```