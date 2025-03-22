# 员工绩效跟踪系统

## 项目简介

一个用于管理和跟踪团队成员日常表现和绩效评估的系统。系统支持员工信息管理、绩效记录、表现类别管理等功能，提供命令行方式使用。

## 主要功能

### 1. 员工管理 (`perf emp`)

- `emp add` - 添加新员工
  - 支持设置员工基本信息（姓名、域账号、部门等）
  - 自动分配员工ID
- `emp del` - 删除员工信息
  - 支持通过ID或域账号删除
  - 删除后相关记录会被保留
- `emp show` - 查看员工详情
  - 按职级和职等排序显示
- `emp toggle` - 激活/禁用员工
  - 控制员工状态，影响绩效记录权限
- `emp list` - 查看员工列表
  - 支持查看所有员工或仅显示在职员工

### 2. 表现类别管理 (`perf cat`)

- `cat add` - 添加表现类别
  - 支持设置类别名称和描述
  - 自动分配类别ID
- `cat del` - 删除表现类别
  - 支持通过ID删除
  - 删除后相关记录会被保留
- `cat show` - 查看类别列表
  - 显示所有表现类别
  - 支持查看启用/禁用状态
- `cat toggle` - 激活/禁用类别
  - 控制类别状态
  - 禁用后不能用于新的表现记录

### 3. 工作量记录 (`perf work`)

- `work add` - 记录工作量得分
  - 按周记录工作承担情况
  - 支持添加描述说明
- `work del` - 删除工作量记录
  - 支持删除特定周的记录
- `work show` - 查看工作量记录
  - 支持按时间范围筛选
  - 提供多种展示格式

### 4. 表现记录管理 (`perf rec`)

- `rec add` - 添加单个表现记录
  - 支持选择表现类别
  - 记录具体表现描述和得分
- `rec del` - 删除表现记录
  - 支持按ID删除记录
- `rec change` - 修改表现记录
  - 可更新描述和得分
- `rec list` - 列出表现记录
  - 支持查看所有记录或当前周期内的记录
- `rec env` - 记录团队事件
  - 支持统一加分和单独加分两种模式
  - 可以同时为多名员工添加得分记录

### 5. 绩效查看 (`perf show`)

- `show perf` - 查看绩效统计
  - 显示表现得分和各表现类别得分
  - 自动计算总分并排序
  - 支持自定义表格格式（simple/grid/fancy_grid）
- `show detail <employee_id>` - 查看详细记录
  - 显示工作承担记录
  - 显示表现得分记录
  - 支持自定义表格格式

### 6. 系统设置 (`perf set`)

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

## 注意事项

1. 所有得分操作都需要在有效的绩效周期内进行
2. 表现类别必须处于启用状态才能使用
3. 只能为激活状态的员工记录得分
4. 分值必须带有正负号（如：+5, -3）
5. 建议定期备份数据库文件