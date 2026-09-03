#!/usr/bin/env python3
"""
GitHub一键部署工具
通过GitHub token自动创建仓库、推送代码、启用Pages并生成访问链接
"""

import os
import sys
import json
import requests
from pathlib import Path
import subprocess
import re
from datetime import datetime
import time
import threading

class GitHubDeployer:
    def __init__(self, token):
        """
        初始化GitHub部署器
        
        Args:
            token (str): GitHub personal access token
        """
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
        self.user_info = None
        self.repo_info = None
        
    def create_repository(self, repo_name, description=None, private=False):
        """
        创建GitHub仓库
        
        Args:
            repo_name (str): 仓库名称
            description (str): 仓库描述
            private (bool): 是否为私有仓库
            
        Returns:
            dict: API响应
        """
        url = f'{self.base_url}/user/repos'
        data = {
            'name': repo_name,
            'description': description or f'Auto-deployed project on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'private': private,
            'auto_init': False
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f'创建仓库失败: {str(e)}')
    
    def check_repository_exists(self, repo_name):
        """
        检查仓库是否已存在
        
        Args:
            repo_name (str): 仓库名称
            
        Returns:
            bool: 仓库是否存在
        """
        url = f'{self.base_url}/repos/{repo_name}'
        try:
            response = requests.get(url, headers=self.headers)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_user_info(self):
        """
        获取用户信息
        
        Returns:
            dict: 用户信息
        """
        if self.user_info:
            return self.user_info
            
        url = f'{self.base_url}/user'
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            self.user_info = response.json()
            return self.user_info
        except requests.exceptions.RequestException as e:
            raise Exception(f'获取用户信息失败: {str(e)}')
    
    def initialize_git_repo(self, path='.'):
        """
        初始化Git仓库
        
        Args:
            path (str): 项目路径
        """
        try:
            subprocess.run(['git', 'init'], cwd=path, check=True, capture_output=True)
            print('✓ Git仓库初始化成功')
        except subprocess.CalledProcessError as e:
            raise Exception(f'Git初始化失败: {str(e)}')
    
    def add_remote_origin(self, repo_url, path='.'):
        """
        添加远程仓库
        
        Args:
            repo_url (str): 仓库URL
            path (str): 项目路径
        """
        try:
            subprocess.run(['git', 'remote', 'add', 'origin', repo_url], 
                         cwd=path, check=True, capture_output=True)
            print('✓ 远程仓库添加成功')
        except subprocess.CalledProcessError as e:
            raise Exception(f'添加远程仓库失败: {str(e)}')
    
    def add_and_commit_files(self, commit_message='Initial commit', path='.'):
        """
        添加并提交文件
        
        Args:
            commit_message (str): 提交信息
            path (str): 项目路径
        """
        try:
            # 添加所有文件
            subprocess.run(['git', 'add', '.'], cwd=path, check=True, capture_output=True)
            print('✓ 文件添加成功')
            
            # 提交
            subprocess.run(['git', 'commit', '-m', commit_message], 
                         cwd=path, check=True, capture_output=True)
            print('✓ 提交成功')
        except subprocess.CalledProcessError as e:
            raise Exception(f'提交失败: {str(e)}')
    
    def push_to_github(self, path='.'):
        """
        推送到GitHub
        
        Args:
            path (str): 项目路径
        """
        try:
            subprocess.run(['git', 'push', '-u', 'origin', 'main'], 
                         cwd=path, check=True, capture_output=True)
            print('✓ 推送到GitHub成功')
        except subprocess.CalledProcessError as e:
            raise Exception(f'推送失败: {str(e)}')
    
    def enable_pages(self, repo_name):
        """
        启用GitHub Pages
        
        Args:
            repo_name (str): 仓库名称
            
        Returns:
            dict: Pages配置信息
        """
        user_info = self.get_user_info()
        owner = user_info['login']
        
        # 设置source为gh-pages分支
        url = f'{self.base_url}/repos/{owner}/{repo_name}/pages'
        data = {
            'source': {
                'branch': 'gh-pages',
                'path': '/'
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers)
            if response.status_code == 201:
                print('✓ GitHub Pages已启用')
                return response.json()
            else:
                # 如果已经启用，尝试更新配置
                response = requests.put(url, json=data, headers=self.headers)
                if response.status_code in [200, 201]:
                    print('✓ GitHub Pages配置已更新')
                    return response.json()
                else:
                    print(f'⚠️ Pages启用状态: {response.status_code}')
                    return None
        except requests.exceptions.RequestException as e:
            print(f'⚠️ 启用Pages时出错: {str(e)}')
            return None
    
    def get_pages_status(self, repo_name):
        """
        获取Pages状态
        
        Args:
            repo_name (str): 仓库名称
            
        Returns:
            dict: Pages状态信息
        """
        user_info = self.get_user_info()
        owner = user_info['login']
        
        url = f'{self.base_url}/repos/{owner}/{repo_name}/pages'
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def get_pages_url(self, repo_name):
        """
        获取Pages访问URL
        
        Args:
            repo_name (str): 仓库名称
            
        Returns:
            str: Pages访问URL，如果不可用则返回None
        """
        pages_info = self.get_pages_status(repo_name)
        if pages_info and pages_info.get('status') == 'built':
            return pages_info.get('html_url')
        return None
    
    def preview_in_browser(self, url):
        """
        在浏览器中预览网页
        
        Args:
            url (str): 要预览的网页URL
        """
        try:
            # 使用package_proxy调用浏览器工具
            result = package_proxy(
                tool_name="browser:goto",
                params={
                    "url": url,
                    "wait_until": "networkidle"
                }
            )
            print(f'🌐 已在浏览器中打开: {url}')
            return result
        except Exception as e:
            print(f'⚠️ 浏览器预览失败: {str(e)}')
            print('💡 提示: 你可以手动打开浏览器访问上述链接')
            return None
    
    def preview_pages_in_browser(self, repo_name):
        """
        在浏览器中预览GitHub Pages
        
        Args:
            repo_name (str): 仓库名称
            
        Returns:
            bool: 预览是否成功
        """
        pages_url = self.get_pages_url(repo_name)
        if pages_url:
            print(f'🌐 正在预览GitHub Pages: {pages_url}')
            return self.preview_in_browser(pages_url)
        else:
            print('⚠️ Pages还未就绪，无法预览')
            return False
    
    def create_gh_pages_branch(self, path='.'):
        """
        创建gh-pages分支用于Pages
        
        Args:
            path (str): 项目路径
        """
        try:
            # 创建并切换到gh-pages分支
            subprocess.run(['git', 'checkout', '-b', 'gh-pages'], 
                         cwd=path, check=True, capture_output=True)
            print('✓ 创建gh-pages分支成功')
        except subprocess.CalledProcessError as e:
            # 如果分支已存在，切换到它
            try:
                subprocess.run(['git', 'checkout', 'gh-pages'], 
                             cwd=path, check=True, capture_output=True)
                print('✓ 切换到现有gh-pages分支')
            except subprocess.CalledProcessError:
                raise Exception(f'创建gh-pages分支失败: {str(e)}')
    
    def deploy_to_pages(self, repo_name, path='.'):
        """
        部署到GitHub Pages
        
        Args:
            repo_name (str): 仓库名称
            path (str): 项目路径
        """
        print('📄 开始部署到GitHub Pages...')
        
        # 切换到gh-pages分支
        self.create_gh_pages_branch(path)
        
        # 删除所有现有文件（保留.git目录）
        import shutil
        git_dir = os.path.join(path, '.git')
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if item != '.git':
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
        
        # 创建一个简单的index.html（如果项目没有HTML文件）
        index_path = os.path.join(path, 'index.html')
        if not os.path.exists(index_path):
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{repo_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            text-align: center;
        }}
        h1 {{
            color: #0366d6;
        }}
        .info {{
            background: #f6f8fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <h1>🎉 {repo_name}</h1>
    <div class="info">
        <p>✅ 项目已成功部署到GitHub Pages！</p>
        <p>🔗 仓库地址: https://github.com/{self.get_user_info()['login']}/{repo_name}</p>
        <p>📅 部署时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>''')
            print('✓ 创建默认index.html文件')
        
        # 提交并推送到gh-pages分支
        try:
            subprocess.run(['git', 'add', '.'], cwd=path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Add Pages content'], 
                         cwd=path, check=True, capture_output=True)
            subprocess.run(['git', 'push', '-u', 'origin', 'gh-pages'], 
                         cwd=path, check=True, capture_output=True)
            print('✓ Pages内容推送到GitHub成功')
        except subprocess.CalledProcessError as e:
            raise Exception(f'Pages部署失败: {str(e)}')
        
        # 启用Pages
        self.enable_pages(repo_name)
    
    def deploy_project(self, project_path='.', enable_pages=True):
        """
        一键部署项目到GitHub（简化版，自动生成仓库名称）
        
        Args:
            project_path (str): 项目路径
            enable_pages (bool): 是否启用Pages
            
        Returns:
            dict: 部署结果
        """
        # 获取用户信息
        user_info = self.get_user_info()
        print(f'👤 用户: {user_info["login"]}')
        
        # 自动生成仓库名称
        project_name = os.path.basename(os.path.abspath(project_path))
        repo_name = project_name.lower().replace(' ', '-').replace('_', '-')
        
        print(f'🚀 开始部署项目到GitHub: {repo_name}')
        
        # 检查仓库是否存在
        if self.check_repository_exists(f"{user_info['login']}/{repo_name}"):
            print(f'⚠️ 仓库 {repo_name} 已存在，将使用现有仓库')
        else:
            # 创建仓库
            print(f'📦 创建仓库: {repo_name}')
            repo_info = self.create_repository(repo_name, f'Auto-deployed project on {datetime.now().strftime("%Y-%m-%d")}', False)
            print(f'✓ 仓库创建成功: {repo_info["html_url"]}')
            self.repo_info = repo_info
        
        # 初始化Git仓库
        self.initialize_git_repo(project_path)
        
        # 添加远程仓库
        repo_url = f'https://github.com/{user_info["login"]}/{repo_name}.git'
        self.add_remote_origin(repo_url, project_path)
        
        # 提交文件
        self.add_and_commit_files('Initial commit', project_path)
        
        # 推送到GitHub
        self.push_to_github(project_path)
        
        result = {
            'success': True,
            'repo_url': f'https://github.com/{user_info["login"]}/{repo_name}',
            'repo_clone_url': f'https://github.com/{user_info["login"]}/{repo_name}.git',
            'message': '项目部署成功'
        }
        
        # 启用Pages
        if enable_pages:
            print('\n📄 启动GitHub Pages部署...')
            self.deploy_to_pages(repo_name, project_path)
            
            # 等待Pages构建完成
            print('⏳ 等待Pages构建完成...')
            time.sleep(30)  # 等待30秒让Pages构建
            
            # 获取Pages URL
            pages_url = self.get_pages_url(repo_name)
            if pages_url:
                result['pages_url'] = pages_url
                print(f'✅ Pages访问地址: {pages_url}')
                
                # 询问用户是否要预览
                preview_choice = input('\n🌐 是否要在浏览器中预览Pages应用？(y/n): ').strip().lower()
                if preview_choice == 'y' or preview_choice == 'yes':
                    print('🌐 正在打开浏览器预览...')
                    self.preview_pages_in_browser(repo_name)
            else:
                print('⚠️ Pages可能还在构建中，请稍后检查')
        
        return result

def validate_token(token):
    """验证GitHub token格式"""
    if not token or len(token.strip()) == 0:
        raise ValueError('GitHub token不能为空')
    
    # 简单的token格式验证
    if not re.match(r'^[a-zA-Z0-9]{40}$', token.strip()):
        raise ValueError('GitHub token格式不正确，应该是40个字符的字符串')

def validate_project_path(path):
    """验证项目路径"""
    if not os.path.exists(path):
        raise ValueError(f'项目路径不存在: {path}')
    
    if not os.path.isdir(path):
        raise ValueError(f'项目路径不是目录: {path}')

def main():
    """主函数"""
    print('🚀 GitHub一键自动部署工具')
    print('=' * 50)
    print('📋 功能：创建仓库 → 推送代码 → 启用Pages → 生成访问链接 → 浏览器预览')
    print('=' * 50)
    
    try:
        # 获取GitHub token
        token = input('🔑 请输入你的GitHub personal access token: ').strip()
        validate_token(token)
        
        # 获取项目路径
        project_path = input('📂 请输入项目路径 (默认为当前目录): ').strip()
        if not project_path:
            project_path = '.'
        validate_project_path(project_path)
        
        # 询问是否要启用浏览器预览
        auto_preview = input('🌐 是否启用浏览器自动预览？(y/n): ').strip().lower()
        enable_auto_preview = auto_preview == 'y' or auto_preview == 'yes'
        
        print('\n🔧 开始自动部署...')
        
        # 创建部署器并执行部署
        deployer = GitHubDeployer(token)
        result = deployer.deploy_project(
            project_path=project_path,
            enable_pages=True
        )
        
        print('\n🎉 部署完成!')
        print('=' * 50)
        print(f'🔗 仓库地址: {result["repo_url"]}')
        print(f'📋 克隆地址: {result["repo_clone_url"]}')
        
        if 'pages_url' in result:
            print(f'🌐 Pages访问地址: {result["pages_url"]}')
            
            # 如果用户选择了自动预览，直接预览
            if enable_auto_preview:
                print('🌐 正在自动打开浏览器预览...')
                deployer.preview_pages_in_browser(result["pages_url"].split('/')[-2])
        
        print('=' * 50)
        print('✨ 所有步骤已完成！')
        
    except Exception as e:
        print(f'\n❌ 部署失败: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    main()