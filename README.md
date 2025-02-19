# 员工绩效跟踪系统

## 项目简介

一个用于管理和跟踪团队成员日常表现和绩效评估的系统。系统支持员工信息管理、绩效记录、评分规则自定义等功能，提供命令行和Web界面两种使用方式。

## 主要功能

- 员工信息管理
  - 添加、查看和更新员工基本信息
  - 支持员工状态管理（激活/停用）
  - 按职级和职等排序显示员工列表

- 绩效记录与评估
  - 工作量评分：记录周度工作量和排名
  - 技术突破：记录技术创新和突破性成果
  - 晋升表现：记录职级晋升相关表现
  - 经验案例：记录知识分享和最佳实践

- 评分规则管理
  - 自定义不同类别的评分权重
  - 灵活配置绩效周期（月度/季度）
  - 支持全局评分规则设置

## 技术栈

- 后端：Python, FastAPI, SQLite
- 前端：Vue.js
- CLI：Click
- 数据库：SQLite

## 项目结构

```
├── data/               # 数据库文件目录
├── src/                # 源代码目录
│   ├── api/           # 后端API接口
│   ├── cli/           # 命令行工具
│   ├── core/          # 核心业务逻辑
│   ├── db/            # 数据库操作
│   ├── utils/         # 工具函数
│   └── web/           # 前端界面
├── tests/             # 测试文件
└── requirements.txt   # Python依赖
```

## 安装说明

1. 克隆项目到本地

```bash
git clone [项目地址]
cd findABC
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 初始化数据库

```bash
python -m src.db.database
```

## 使用说明

### 命令行工具

1. 添加新员工
```bash
python -m src.cli.commands add-employee
```

2. 记录绩效
```bash
python -m src.cli.commands add-performance
```

3. 查看绩效汇总
```bash
python -m src.cli.commands show-summary
```

### Web界面

1. 启动服务
```bash
python -m src.api.server
```

2. 访问地址：http://localhost:8000

## 数据库设计

### 主要表结构

1. employees - 员工信息表
   - id: 员工ID
   - name: 姓名
   - domain_account: 域账号
   - department: 部门
   - position: 职级职等
   - is_active: 是否在职

2. workload_scores - 工作量评分表
   - employee_id: 员工ID
   - week_number: 周数
   - year: 年份
   - ranking_percentage: 排名百分比
   - score: 得分

3. technical_breakthrough_scores - 技术突破评分表
   - employee_id: 员工ID
   - description: 突破描述
   - score: 得分
   - completion_date: 完成日期

4. promotion_scores - 晋升评分表
   - employee_id: 员工ID
   - new_value: 晋升详情
   - score: 得分
   - promotion_date: 晋升日期

5. experience_case_scores - 经验案例评分表
   - employee_id: 员工ID
   - description: 案例描述
   - score: 得分
   - submission_date: 提交日期

## 注意事项

1. 首次使用需要先设置默认部门
2. 建议定期备份数据库文件
3. Web服务启动时会同时启动前端和后端服务

## 评分规则说明

系统采用四个维度的综合评分机制：

1. 工作量（25%）
   - 基于周度工作量统计
   - 考虑团队内部排名

2. 技术突破（25%）
   - 技术创新和突破
   - 解决关键技术难题

3. 晋升表现（25%）
   - 职级晋升相关表现
   - 技能提升和成长

4. 经验案例（25%）
   - 知识分享和最佳实践
   - 团队贡献和影响力

最终得分为四个维度的加权平均值，满分100分。