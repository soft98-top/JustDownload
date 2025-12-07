#!/usr/bin/env python3
"""
诊断脚本 - 检查系统配置和依赖
"""
import os
import sys
import json
import subprocess
import platform

def check_python():
    """检查 Python 版本"""
    print("检查 Python...")
    version = sys.version_info
    print(f"  Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("  ✓ Python 版本符合要求 (>= 3.8)")
        return True
    else:
        print("  ✗ Python 版本过低，需要 3.8 或更高")
        return False

def check_node():
    """检查 Node.js"""
    print("\n检查 Node.js...")
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"  Node.js 版本: {version}")
            print("  ✓ Node.js 已安装")
            return True
        else:
            print("  ✗ Node.js 未安装或无法运行")
            return False
    except FileNotFoundError:
        print("  ✗ Node.js 未安装")
        return False

def check_npm():
    """检查 npm"""
    print("\n检查 npm...")
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"  npm 版本: {version}")
            print("  ✓ npm 已安装")
            return True
        else:
            print("  ✗ npm 未安装或无法运行")
            return False
    except FileNotFoundError:
        print("  ✗ npm 未安装")
        return False

def check_config():
    """检查配置文件"""
    print("\n检查配置文件...")
    
    if not os.path.exists('config.json'):
        print("  ✗ config.json 不存在")
        print("  提示: 运行 'cp config.json.example config.json' 创建配置文件")
        return False
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("  ✓ config.json 存在且格式正确")
        
        # 检查必需字段
        required_fields = {
            'backend': ['host', 'port', 'public_url'],
            'frontend': ['host', 'port', 'public_url', 'api_url']
        }
        
        all_ok = True
        for section, fields in required_fields.items():
            if section not in config:
                print(f"  ✗ 缺少 {section} 配置")
                all_ok = False
            else:
                for field in fields:
                    if field not in config[section]:
                        print(f"  ✗ 缺少 {section}.{field} 配置")
                        all_ok = False
        
        if all_ok:
            print("  ✓ 配置文件完整")
            print(f"\n  配置信息:")
            print(f"    后端: {config['backend']['public_url']}")
            print(f"    前端: {config['frontend']['public_url']}")
            print(f"    API: {config['frontend']['api_url']}")
        
        return all_ok
        
    except json.JSONDecodeError as e:
        print(f"  ✗ config.json 格式错误: {e}")
        return False
    except Exception as e:
        print(f"  ✗ 读取配置文件失败: {e}")
        return False

def check_frontend_deps():
    """检查前端依赖"""
    print("\n检查前端依赖...")
    
    node_modules = os.path.join('frontend', 'node_modules')
    if not os.path.exists(node_modules):
        print("  ✗ 前端依赖未安装")
        print("  提示: 运行 'cd frontend && npm install'")
        return False
    
    print("  ✓ 前端依赖已安装")
    return True

def check_backend_deps():
    """检查后端依赖"""
    print("\n检查后端依赖...")
    
    req_file = os.path.join('backend', 'requirements.txt')
    if not os.path.exists(req_file):
        print("  ⚠ requirements.txt 不存在")
        return True
    
    # 简单检查，不实际验证所有包
    print("  ✓ requirements.txt 存在")
    print("  提示: 确保已运行 'pip install -r backend/requirements.txt'")
    return True

def check_ports(config):
    """检查端口是否被占用"""
    print("\n检查端口...")
    
    import socket
    
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return False
            except OSError:
                return True
    
    backend_port = config['backend']['port']
    frontend_port = config['frontend']['port']
    
    backend_in_use = is_port_in_use(backend_port)
    frontend_in_use = is_port_in_use(frontend_port)
    
    if backend_in_use:
        print(f"  ⚠ 后端端口 {backend_port} 已被占用")
    else:
        print(f"  ✓ 后端端口 {backend_port} 可用")
    
    if frontend_in_use:
        print(f"  ⚠ 前端端口 {frontend_port} 已被占用")
    else:
        print(f"  ✓ 前端端口 {frontend_port} 可用")
    
    return not (backend_in_use or frontend_in_use)

def check_logs():
    """检查日志文件"""
    print("\n检查日志文件...")
    
    log_files = [
        'logs/backend.log',
        'logs/backend_error.log',
        'logs/frontend.log',
        'logs/frontend_error.log'
    ]
    
    found_logs = False
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"  {log_file}: {size} 字节")
            found_logs = True
            
            # 如果是错误日志且有内容，显示最后几行
            if 'error' in log_file and size > 0:
                print(f"    最后几行:")
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines[-5:]:
                            print(f"      {line.rstrip()}")
                except:
                    pass
    
    if not found_logs:
        print("  未找到日志文件（服务可能未启动过）")
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("系统诊断")
    print("=" * 60)
    print(f"\n操作系统: {platform.system()} {platform.release()}")
    print(f"Python 路径: {sys.executable}")
    
    results = []
    
    # 检查 Python
    results.append(("Python", check_python()))
    
    # 检查 Node.js
    results.append(("Node.js", check_node()))
    
    # 检查 npm
    results.append(("npm", check_npm()))
    
    # 检查配置文件
    config_ok = check_config()
    results.append(("配置文件", config_ok))
    
    # 如果配置文件正确，继续检查
    if config_ok:
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 检查端口
            results.append(("端口", check_ports(config)))
        except:
            pass
    
    # 检查依赖
    results.append(("前端依赖", check_frontend_deps()))
    results.append(("后端依赖", check_backend_deps()))
    
    # 检查日志
    check_logs()
    
    # 总结
    print("\n" + "=" * 60)
    print("诊断总结")
    print("=" * 60)
    
    all_ok = True
    for name, ok in results:
        status = "✓" if ok else "✗"
        print(f"  {status} {name}")
        if not ok:
            all_ok = False
    
    print("\n" + "=" * 60)
    
    if all_ok:
        print("✓ 所有检查通过！")
        print("\n如果服务仍然无法启动，请查看日志:")
        print("  python logs.py frontend-error")
    else:
        print("✗ 发现问题，请根据上述提示修复")
    
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
