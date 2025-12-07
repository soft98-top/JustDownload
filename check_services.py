#!/usr/bin/env python3
"""
检查服务是否真的在运行（通过端口检查）
"""
import socket
import json
import os
import sys

def check_port(host, port, timeout=2):
    """检查端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def check_http(url, timeout=2):
    """检查 HTTP 服务是否响应"""
    try:
        import urllib.request
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status == 200
    except:
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("服务实际状态检查（通过端口）")
    print("=" * 60)
    
    # 读取配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except:
        print("\n错误: 无法读取 config.json")
        sys.exit(1)
    
    backend_port = config['backend']['port']
    frontend_port = config['frontend']['port']
    
    print(f"\n配置的端口:")
    print(f"  后端: {backend_port}")
    print(f"  前端: {frontend_port}")
    
    # 检查后端
    print(f"\n检查后端 (端口 {backend_port})...")
    backend_port_open = check_port('127.0.0.1', backend_port)
    
    if backend_port_open:
        print(f"  ✓ 端口 {backend_port} 开放")
        # 尝试访问 API
        backend_url = f"http://127.0.0.1:{backend_port}/"
        if check_http(backend_url):
            print(f"  ✓ HTTP 服务响应正常")
            print(f"  ✓ 后端服务正在运行")
        else:
            print(f"  ⚠ 端口开放但 HTTP 无响应")
    else:
        print(f"  ✗ 端口 {backend_port} 未开放")
        print(f"  ✗ 后端服务未运行")
    
    # 检查前端
    print(f"\n检查前端 (端口 {frontend_port})...")
    frontend_port_open = check_port('127.0.0.1', frontend_port)
    
    if frontend_port_open:
        print(f"  ✓ 端口 {frontend_port} 开放")
        # 尝试访问前端
        frontend_url = f"http://127.0.0.1:{frontend_port}/"
        if check_http(frontend_url):
            print(f"  ✓ HTTP 服务响应正常")
            print(f"  ✓ 前端服务正在运行")
        else:
            print(f"  ⚠ 端口开放但 HTTP 无响应")
    else:
        print(f"  ✗ 端口 {frontend_port} 未开放")
        print(f"  ✗ 前端服务未运行")
    
    # 检查进程
    print(f"\n检查进程 PID...")
    if os.path.exists('.running_pids.json'):
        try:
            with open('.running_pids.json', 'r') as f:
                pids = json.load(f)
            
            print(f"  后端 PID: {pids.get('backend', 'N/A')}")
            print(f"  前端 PID: {pids.get('frontend', 'N/A')}")
            
            # 检查 PID 是否存在
            import platform
            is_linux = platform.system() == 'Linux'
            
            if is_linux:
                for name, pid in pids.items():
                    if os.path.exists(f'/proc/{pid}'):
                        print(f"  ✓ {name} 进程存在 (PID: {pid})")
                    else:
                        print(f"  ✗ {name} 进程不存在 (PID: {pid})")
        except Exception as e:
            print(f"  错误: {e}")
    else:
        print("  未找到 PID 文件")
    
    # 总结
    print("\n" + "=" * 60)
    print("总结:")
    print("=" * 60)
    
    if backend_port_open:
        print(f"✓ 后端服务正在运行: http://127.0.0.1:{backend_port}")
    else:
        print(f"✗ 后端服务未运行")
    
    if frontend_port_open:
        print(f"✓ 前端服务正在运行: http://127.0.0.1:{frontend_port}")
    else:
        print(f"✗ 前端服务未运行")
    
    print("\n提示:")
    print("  - 如果端口开放但进程显示不存在，说明进程检测有问题")
    print("  - 如果端口开放，服务就是在运行的，可以正常使用")
    print("  - 使用 'netstat -tlnp | grep <port>' 查看端口占用")
    
    print("=" * 60)

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
