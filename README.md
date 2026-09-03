# GitHub一键自动部署工具

这是一个通过GitHub personal access token将本地项目**一键自动部署**到GitHub仓库并启用Pages的Python程序，支持自动浏览器预览功能。

## 🚀 核心功能

- 🔐 **仅需GitHub Token** - 自动完成所有配置
- 📦 **自动创建仓库** - 基于项目名称自动生成
- 🚀 **自动推送代码** - 完整的Git操作流程
- 🌐 **自动启用Pages** - 创建gh-pages分支并配置
- 🔗 **生成访问链接** - 直接返回可访问的URL
- ⚠️ **智能检查** - 仓库已存在时自动复用
- 🌐 **浏览器预览** - 自动打开浏览器预览已部署的应用

## 📋 完整操作流程

1. **输入GitHub Token**
2. **选择项目路径**
3. **选择是否启用浏览器预览**
4. **自动执行**：
   - 创建公开GitHub仓库
   - 初始化Git仓库
   - 提交并推送代码
   - 创建gh-pages分支
   - 启用GitHub Pages
   - 生成访问链接
   - **可选浏览器预览**

## 使用方法

### 1. 准备工作

确保你的系统已安装：
- Python 3.6+
- Git
- `requests`库（如果不存在，运行：`pip install requests`）

### 2. 获取GitHub Token

1. 登录GitHub
2. 进入 Settings → Developer settings → Personal access tokens → Tokens (classic)
3. 点击 "Generate new token"
4. 选择权限：至少需要 `repo` 权限
5. 生成并复制token（注意：token只显示一次，请妥善保存）

### 3. 运行程序

```bash
python github_deploy.py
```

### 4. 简单操作

程序只需要两个输入：
- 🔑 **GitHub personal access token**
- 📂 **项目路径**（默认为当前目录）

## 使用示例

```bash
$ python github_deploy.py
🚀 GitHub一键自动部署工具
==================================================
📋 功能：创建仓库 → 推送代码 → 启用Pages → 生成访问链接 → 浏览器预览
==================================================

🔑 请输入你的GitHub personal access token: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
📂 请输入项目路径 (默认为当前目录): /path/to/your/project
🌐 是否启用浏览器自动预览？(y/n): y

🔧 开始自动部署...

🚀 开始部署项目到GitHub: my-project
👤 用户: your-username
📦 创建仓库: my-project
✓ 仓库创建成功: https://github.com/your-username/my-project
✓ Git仓库初始化成功
✓ 远程仓库添加成功
✓ 文件添加成功
✓ 提交成功
✓ 推送到GitHub成功

📄 启动GitHub Pages部署...
✓ 创建gh-pages分支成功
✓ 创建默认index.html文件
✓ Pages内容推送到GitHub成功
✓ GitHub Pages已启用
⏳ 等待Pages构建完成...
✅ Pages访问地址: https://your-username.github.io/my-project

🌐 正在自动打开浏览器预览...
🌐 已在浏览器中打开: https://your-username.github.io/my-project

🎉 部署完成!
==================================================
🔗 仓库地址: https://github.com/your-username/my-project
📋 克隆地址: https://github.com/your-username/my-project.git
🌐 Pages访问地址: https://your-username.github.io/my-project
==================================================
✨ 所有步骤已完成！
```

## Pages功能说明

### 自动生成的内容
- 如果项目没有HTML文件，会自动创建一个简单的`index.html`
- 包含项目信息和部署时间
- 适配移动端显示

### Pages配置
- 使用`gh-pages`分支作为源
- 自动启用GitHub Pages服务
- 等待构建完成后返回访问链接

## 浏览器预览功能

### 功能特点
- **可选预览**：用户可以选择是否在浏览器中预览已部署的Pages应用
- **自动打开**：支持自动打开浏览器访问Pages应用
- **手动备选**：如果自动预览失败，提供手动访问的提示
- **智能等待**：等待Pages构建完成后才进行预览

### 使用方式
1. **运行程序时选择**：
   ```bash
   🌐 是否启用浏览器自动预览？(y/n): y
   ```

2. **部署完成后询问**：
   ```bash
   🌐 是否要在浏览器中预览Pages应用？(y/n): y
   ```

3. **编程方式调用**：
   ```python
   from github_deploy import GitHubDeployer
   
   deployer = GitHubDeployer('your_github_token')
   result = deployer.deploy_project('./my-project')
   
   # 预览Pages应用
   deployer.preview_pages_in_browser('my-project')
   ```

### 注意事项
- 需要浏览器工具包支持
- 如果预览失败，程序会提示手动访问链接
- 预览功能是可选的，不影响核心部署流程

## 注意事项

1. **Token安全**：GitHub token是敏感信息，请妥善保管
2. **权限要求**：token需要`repo`权限
3. **Git配置**：确保已配置Git用户名和邮箱
4. **网络连接**：需要稳定的网络连接
5. **Pages限制**：GitHub Pages有文件大小和流量限制
6. **浏览器预览**：需要浏览器工具包支持，如果预览失败可以手动访问链接

## 错误处理

程序包含完善的错误处理，常见问题：
- Token格式错误
- 网络连接问题
- 仓库已存在
- Git配置问题
- Pages构建失败
- 浏览器预览失败（提供手动访问提示）

## 高级用法

### 在其他Python程序中使用

```python
from github_deploy import GitHubDeployer

# 创建部署器
deployer = GitHubDeployer('your_github_token')

# 部署项目
result = deployer.deploy_project(
    project_path='./my-project',
    enable_pages=True
)

print(f"仓库地址: {result['repo_url']}")
print(f"Pages地址: {result['pages_url']}")
```

### 禁用Pages

```python
result = deployer.deploy_project(
    project_path='./my-project',
    enable_pages=False
)
```

### 浏览器预览

```python
from github_deploy import GitHubDeployer

# 创建部署器
deployer = GitHubDeployer('your_github_token')

# 部署项目
result = deployer.deploy_project(
    project_path='./my-project',
    enable_pages=True
)

# 预览Pages应用
deployer.preview_pages_in_browser('my-project')

# 或者预览任意URL
deployer.preview_in_browser('https://example.com')
```

## 许可证

MIT License

## 注意事项

1. **Token安全**：GitHub personal access token是敏感信息，请妥善保管，不要泄露
2. **权限要求**：token至少需要 `repo` 权限才能创建仓库和推送代码
3. **Git配置**：确保已配置好Git用户名和邮箱：
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```
4. **网络连接**：需要稳定的网络连接才能访问GitHub API

## 错误处理

程序包含完善的错误处理机制，常见错误包括：
- Token格式不正确
- 网络连接问题
- 仓库已存在
- Git配置问题
- 权限不足

## 自定义使用

你也可以直接导入`GitHubDeployer`类在其他Python程序中使用：

```python
from github_deploy import GitHubDeployer

# 创建部署器实例
deployer = GitHubDeployer('your_github_token')

# 部署项目
result = deployer.deploy_project(
    repo_name='my-repo',
    project_path='./my-project',
    description='My project description',
    private=False,
    commit_message='Initial commit'
)
```

## 许可证

MIT License