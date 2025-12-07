#!/usr/bin/env python3
"""
统一启动脚本 - 支持配置化部署
"""
import json
import os
import sys
import subprocess
import time
import signal
import platform

# 配置文件路径
CONFIG_FILE = 'config.json'
PID_FILE = '.running_pids.json'

def load_config():
    """加载配置文件"""
    if not os.path.exists(CONFIG_FILE):
        print(f"错误: 配置文件 {CONFIG_FILE} 不存在")
        print("请先创建配置文件，参考 config.json")
        sys.exit(1)
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_pids(pids):
    """保存进程 ID"""
    with open(PID_FILE, 'w', encoding='utf-8') as f:
        json.dump(pids, f, indent=2)

def create_frontend_env(config):
    """创建前端环境变量文件"""
    env_content = f"VITE_API_BASE_URL={config['frontend']['api_url']}\n"
    env_path = os.path.join('frontend', '.env')
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✓ 已创建前端环境配置: {env_path}")
    print(f"  API 地址: {config['frontend']['api_url']}")

def check_dependencies():
    """检查依赖"""
    print("\n检查依赖...")
    
    # 检查后端依赖
    req_file = os.path.join('backend', 'requirements.txt')
    if os.path.exists(req_file):
        print("  安装后端依赖...")
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', req_file, '-q'],
            capture_output=True
        )
        if result.returncode == 0:
            print("  ✓ 后端依赖已就绪")
        else:
            print("  ⚠ 后端依赖安装失败，但继续启动...")
    
    # 检查前端依赖
    node_modules = os.path.join('frontend', 'node_modules')
    if not os.path.exists(node_modules):
        print("  安装前端依赖（首次运行可能需要较长时间）...")
        result = subprocess.run(
            ['npm', 'install'],
            cwd='frontend',
            capture_output=True
        )
        if result.returncode == 0:
            print("  ✓ 前端依赖已安装")
        else:
            print("  ✗ 前端依赖安装失败")
            return False
    else:
        print("  ✓ 前端依赖已就绪")
    
    return True

def start_backend(config):
    """启动后端服务"""
    print("\n启动后端服务...")
    
    backend_config = config['backend']
    cmd = [
        sys.executable,
        'main.py',
        '--host', backend_config['host'],
        '--port', str(backend_config['port']),
        '--log-level', 'INFO'
    ]
    
    # 根据操作系统选择启动方式
    is_windows = platform.system() == 'Windows'
    
    if is_windows:
        # Windows: 使用 CREATE_NEW_PROCESS_GROUP
        process = subprocess.Popen(
            cmd,
            cwd='backend',
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    else:
        # Linux/Mac: 使用 nohup
        process = subprocess.Popen(
            cmd,
            cwd='backend',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setpgrp
        )
    
    print(f"  后端 PID: {process.pid}")
    print(f"  监听地址: {backend_config['host']}:{backend_config['port']}")
    print(f"  访问地址: {backend_config['public_url']}")
    
    return process.pid

def start_frontend(config):
    """启动前端服务"""
    print("\n启动前端服务...")
    
    frontend_config = config['frontend']
    
    # 设置环境变量
    env = os.environ.copy()
    env['VITE_PORT'] = str(frontend_config['port'])
    env['VITE_HOST'] = frontend_config['host']
    
    # 根据操作系统选择启动方式
    is_windows = platform.system() == 'Windows'
    
    if is_windows:
        # Windows
        process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd='frontend',
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    else:
        # Linux/Mac
        process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd='frontend',
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setpgrp
        )
    
    print(f"  前端 PID: {process.pid}")
    print(f"  监听地址: {frontend_config['host']}:{frontend_config['port']}")
    print(f"  访问地址: {frontend_config['public_url']}")
    
    return process.pid

def main():
    """主函数"""
    print("=" * 50)
    print("模块化下载系统 - 统一启动")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    print(f"\n✓ 已加载配置文件: {CONFIG_FILE}")
    
    # 创建前端环境配置
    create_frontend_env(config)
    
    # 检查依赖
    if not check_dependencies():
        print("\n依赖检查失败，退出")
        sys.exit(1)
    
    # 启动后端
    backend_pid = start_backend(config)
    time.sleep(3)  # 等待后端启动
    
    # 启动前端
    frontend_pid = start_frontend(config)
    time.sleep(2)  # 等待前端启动
    
    # 保存 PID
    pids = {
        'backend': backend_pid,
        'frontend': frontend_pid
    }
    save_pids(pids)
    
    # 输出访问信息
    print("\n" + "=" * 50)
    print("服务已启动")
    print("=" * 50)
    print(f"后端 API: {config['backend']['public_url']}")
    print(f"前端界面: {config['frontend']['public_url']}")
    print("\n提示:")
    print("  - 进程已在后台运行")
    print("  - 使用 'python stop.py' 停止所有服务")
    print("  - 使用 'python status.py' 查看服务状态")
    print("=" * 50)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
