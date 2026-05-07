# 用户管理系统

基于 Flask + SQLite 的用户管理系统，支持用户增删改查及 CSV 导入导出功能。

## 功能特性

- ✅ 用户列表展示（支持分页）
- ✅ 添加用户（带表单验证）
- ✅ 编辑用户信息
- ✅ 单条删除 + 批量删除
- ✅ 导出 CSV 文件
- ✅ 导入 CSV 文件（带数据校验）
- ✅ 下载导入模板

## 技术栈

- Python 3.x
- Flask
- SQLite
- 原生 HTML/CSS/JavaScript

## 快速开始

### 安装依赖

```bash
pip install flask
```

### 启动服务

```bash
python app.py
```

### 访问地址

打开浏览器访问 http://localhost:5001

## API 接口

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/users` | 获取用户列表 |
| POST | `/api/users` | 添加用户 |
| PUT | `/api/users/:id` | 更新用户 |
| DELETE | `/api/users/:id` | 删除用户 |
| DELETE | `/api/users/batch` | 批量删除 |
| GET | `/api/users/export` | 导出 CSV |
| POST | `/api/users/import` | 导入 CSV |
| GET | `/api/users/template` | 下载模板 |

## 项目结构

```
user-management-flask/
├── app.py              # Flask 后端 API
├── users.db            # SQLite 数据库（运行后自动生成）
├── templates/
│   └── index.html      # 前端页面
├── .gitignore          # Git 忽略文件
└── README.md           # 项目说明
```

## 使用说明

1. **添加用户**: 点击「+ 添加用户」按钮，填写姓名、邮箱和年龄
2. **编辑用户**: 点击用户列表中的「编辑」按钮
3. **删除用户**: 点击「删除」按钮，或勾选多条后批量删除
4. **导出数据**: 点击「导出 CSV」下载用户列表
5. **导入数据**: 点击「导入 CSV」上传文件（建议先下载模板）