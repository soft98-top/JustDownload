#!/usr/bin/env python3
"""
查看服务日志
"""
import os
import sys

LOG_DIR = 'logs'

def show_log(log_file, lines=50):
    """显示日志文件的最后 N 行"""
    if not os.path.exists(log_file):
        print(f"日志文件不存在: {log_file}")
        return
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            if not last_lines:
                print("日志文件为空")
                return
            
            for line in last_lines:
                print(line.rstrip())
    except Exception as e:
        print(f"读取日志失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("=" * 50)
        print("查看服务日志")
        print("=" * 50)
        print("\n用法:")
        print("  python logs.py backend       # 查看后端日志")
        print("  python logs.py backend-error # 查看后端错误日志")
        print("  python logs.py frontend      # 查看前端日志")
        print("  python logs.py frontend-error # 查看前端错误日志")
        print("  python logs.py all           # 查看所有日志")
        print("\n可选参数:")
        print("  python logs.py backend 100   # 显示最后 100 行")
        return
    
    service = sys.argv[1].lower()
    lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    if service == 'backend':
        print("=" * 50)
        print("后端日志 (最后 {} 行)".format(lines))
        print("=" * 50)
        show_log(os.path.join(LOG_DIR, 'backend.log'), lines)
    
    elif service == 'backend-error':
        print("=" * 50)
        print("后端错误日志 (最后 {} 行)".format(lines))
        print("=" * 50)
        show_log(os.path.join(LOG_DIR, 'backend_error.log'), lines)
    
    elif service == 'frontend':
        print("=" * 50)
        print("前端日志 (最后 {} 行)".format(lines))
        print("=" * 50)
        show_log(os.path.join(LOG_DIR, 'frontend.log'), lines)
    
    elif service == 'frontend-error':
        print("=" * 50)
        print("前端错误日志 (最后 {} 行)".format(lines))
        print("=" * 50)
        show_log(os.path.join(LOG_DIR, 'frontend_error.log'), lines)
    
    elif service == 'all':
        print("\n" + "=" * 50)
        print("后端日志 (最后 {} 行)".format(lines))
        print("=" * 50)
        show_log(os.path.join(LOG_DIR, 'backend.log'), lines)
        
        print("\n" + "=" * 50)
        print("后端错误日志 (最后 {} 行)".format(lines))
        print("=" * 50)
        show_log(os.path.join(LOG_DIR, 'backend_error.log'), lines)
        
        print("\n" + "=" * 50)
        print("前端日志 (最后 {} 行)".format(lines))
        print("=" * 50)
        show_log(os.path.join(LOG_DIR, 'frontend.log'), lines)
        
        print("\n" + "=" * 50)
        print("前端错误日志 (最后 {} 行)".format(lines))
        print("=" * 50)
        show_log(os.path.join(LOG_DIR, 'frontend_error.log'), lines)
    
    else:
        print(f"未知的服务: {service}")
        print("可用的服务: backend, backend-error, frontend, frontend-error, all")

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
