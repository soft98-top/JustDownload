#!/usr/bin/env python3
"""
停止所有服务
"""
import json
import os
import sys
import signal
import platform

PID_FILE = '.running_pids.json'

def load_pids():
    """加载进程 ID"""
    if not os.path.exists(PID_FILE):
        print("没有找到运行中的服务")
        return None
    
    with open(PID_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def kill_process(pid, name):
    """终止进程"""
    try:
        is_windows = platform.system() == 'Windows'
        
        if is_windows:
            # Windows: 使用 taskkill
            import subprocess
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], 
                         capture_output=True)
        else:
            # Linux/Mac: 使用 kill
            os.killpg(pid, signal.SIGTERM)
        
        print(f"✓ 已停止 {name} (PID: {pid})")
        return True
    except ProcessLookupError:
        print(f"⚠ {name} (PID: {pid}) 进程不存在")
        return False
    except Exception as e:
        print(f"✗ 停止 {name} (PID: {pid}) 失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("停止所有服务")
    print("=" * 50)
    
    pids = load_pids()
    if not pids:
        sys.exit(0)
    
    # 停止后端
    if 'backend' in pids:
        kill_process(pids['backend'], '后端服务')
    
    # 停止前端
    if 'frontend' in pids:
        kill_process(pids['frontend'], '前端服务')
    
    # 删除 PID 文件
    try:
        os.remove(PID_FILE)
        print(f"\n✓ 已清理 PID 文件")
    except:
        pass
    
    print("\n所有服务已停止")

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
