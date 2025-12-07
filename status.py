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
            # 方法1: 使用 /proc 文件系统（最可靠）
            proc_path = f'/proc/{pid}'
            if os.path.exists(proc_path):
                # 进一步检查是否是僵尸进程
                try:
                    with open(f'{proc_path}/stat', 'r') as f:
                        stat = f.read()
                        # 检查进程状态，Z 表示僵尸进程
                        if ' Z ' not in stat and ' Z)' not in stat:
                            return True
                except:
                    # 如果无法读取状态，假设进程存在
                    return True
            
            # 方法2: 使用 kill -0（备用）
            try:
                os.kill(pid, 0)
                return True
            except ProcessLookupError:
                return False
            except PermissionError:
                # 进程存在但没有权限，说明进程在运行
                return True
            
            return False
    except Exception as e:
        # 如果出错，尝试最后的备用方法
        try:
            os.kill(pid, 0)
            return True
        except:
            return False

def check_process_tree(pid):
    """检查进程及其子进程"""
    try:
        is_windows = platform.system() == 'Windows'
        
        if is_windows:
            return check_process(pid)
        else:
            # Linux: 检查进程树
            import subprocess
            result = subprocess.run(
                ['pgrep', '-P', str(pid)],
                capture_output=True,
                text=True
            )
            # 如果有子进程，说明父进程肯定在运行
            if result.stdout.strip():
                return True
            # 否则检查进程本身
            return check_process(pid)
    except:
        return check_process(pid)

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
        is_running = check_process_tree(backend_pid)
        status = "运行中 ✓" if is_running else "已停止 ✗"
        print(f"  后端服务: {status} (PID: {backend_pid})")
        if config:
            print(f"    地址: {config['backend']['public_url']}")
    
    # 检查前端
    if 'frontend' in pids:
        frontend_pid = pids['frontend']
        is_running = check_process_tree(frontend_pid)
        status = "运行中 ✓" if is_running else "已停止 ✗"
        print(f"  前端服务: {status} (PID: {frontend_pid})")
        if config:
            print(f"    地址: {config['frontend']['public_url']}")
        
        # 如果显示已停止，但日志显示在运行，给出提示
        if not is_running:
            # 检查日志文件最后修改时间
            frontend_log = 'logs/frontend.log'
            if os.path.exists(frontend_log):
                import time
                mtime = os.path.getmtime(frontend_log)
                age = time.time() - mtime
                if age < 60:  # 最近1分钟有日志
                    print(f"    提示: 日志显示服务可能正在运行，请检查实际端口")
    
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
