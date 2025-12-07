#!/usr/bin/env python3
"""
查看服务状态
"""
import json
import os
import sys
import platform

PID_FILE = '.running_pids.json'
CONFIG_FILE = 'config.json'

def load_pids():
    """加载进程 ID"""
    if not os.path.exists(PID_FILE):
        return None
    
    with open(PID_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_config():
    """加载配置"""
    if not os.path.exists(CONFIG_FILE):
        return None
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_process(pid):
    """检查进程是否运行"""
    try:
        is_windows = platform.system() == 'Windows'
        
        if is_windows:
            import subprocess
            result = subprocess.run(
                ['tasklist', '/FI', f'PID eq {pid}'],
                capture_output=True,
                text=True
            )
            return str(pid) in result.stdout
        else:
            # Linux/Mac: 检查进程是否存在
            # 使用 /proc 文件系统（更可靠）
            if os.path.exists(f'/proc/{pid}'):
                return True
            # 备用方法：使用 kill -0
            try:
                os.kill(pid, 0)
                return True
            except ProcessLookupError:
                return False
            except PermissionError:
                # 进程存在但没有权限，说明进程在运行
                return True
    except Exception as e:
        # 如果出错，尝试备用方法
        try:
            os.kill(pid, 0)
            return True
        except:
            return False

def main():
    """主函数"""
    print("=" * 50)
    print("服务状态")
    print("=" * 50)
    
    config = load_config()
    pids = load_pids()
    
    if not pids:
        print("\n没有运行中的服务")
        print("\n提示: 使用 'python start.py' 启动服务")
        return
    
    print("\n进程状态:")
    
    # 检查后端
    if 'backend' in pids:
        backend_pid = pids['backend']
        status = "运行中 ✓" if check_process(backend_pid) else "已停止 ✗"
        print(f"  后端服务: {status} (PID: {backend_pid})")
        if config:
            print(f"    地址: {config['backend']['public_url']}")
    
    # 检查前端
    if 'frontend' in pids:
        frontend_pid = pids['frontend']
        status = "运行中 ✓" if check_process(frontend_pid) else "已停止 ✗"
        print(f"  前端服务: {status} (PID: {frontend_pid})")
        if config:
            print(f"    地址: {config['frontend']['public_url']}")
    
    print("\n" + "=" * 50)

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
