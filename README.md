# 员工绩效跟踪系统

一个用于管理和跟踪团队成员日常表现和绩效评估的系统。

## 功能特点

- 员工信息管理：添加和查看员工基本信息
- 绩效记录：记录员工日常表现和评分
- 评分规则：可自定义不同类别的评分权重
- 部门管理：支持设置全局默认部门
- 提供命令行和Web界面两种使用方式

## 安装说明

1. 克隆项目到本地

2. 安装Python依赖
```bash
pip install -r requirements.txt
```

3. 安装前端依赖（如需使用Web界面）
```bash
cd src/web
npm install
```

## 使用方法

### 命令行界面

1. 添加新员工
```bash
findabc add-employee
```

2. 设置默认部门
```bash
findabc set-default-department
```

3. 记录员工表现
```bash
findabc add-record
```

4. 查看员工列表
```bash
findabc list-employees
```

5. 查看员工详情
```bash
findabc show-employee <员工ID>
```

### Web界面

启动Web服务：
```bash
findabc serve
```

默认端口：
- 前端：http://localhost:3000
- 后端：http://localhost:8000

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

## 技术栈

- 后端：Python, FastAPI, SQLite
- 前端：Vue.js
- CLI：Click
- 数据库：SQLite

## 开发说明

1. 数据库初始化会自动完成，无需手动操作
2. 所有数据存储在`data/performance.db`文件中
3. 支持跨域请求，方便本地开发

## 注意事项

1. 首次使用需要先设置默认部门
2. 建议定期备份数据库文件
3. Web服务启动时会同时启动前端和后端服务