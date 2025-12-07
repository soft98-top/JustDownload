#!/usr/bin/env python3
"""
修复配置并重启服务
"""
import json
import os
import sys
import subprocess
import time

def stop_services():
    """停止服务"""
    print("停止现有服务...")
    result = subprocess.run([sys.executable, 'stop.py'], capture_output=True)
    time.sleep(2)

def update_frontend_env(api_url):
    """更新前端环境变量"""
    env_file = os.path.join('frontend', '.env')
    print(f"\n更新前端环境变量: {env_file}")
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(f"VITE_API_BASE_URL={api_url}\n")
    
    print(f"  ✓ API 地址设置为: {api_url}")

def check_config():
    """检查并显示配置"""
    print("\n当前配置:")
    
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print(f"  后端: {config['backend']['public_url']}")
    print(f"  前端: {config['frontend']['public_url']}")
    print(f"  API: {config['frontend']['api_url']}")
    
    return config

def start_services():
    """启动服务"""
    print("\n启动服务...")
    result = subprocess.run([sys.executable, 'start.py'], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("  ✓ 服务启动命令已执行")
    else:
        print("  ✗ 启动失败")
        print(result.stderr)
        return False
    
    return True

def wait_and_check():
    """等待并检查服务"""
    print("\n等待服务启动...")
    time.sleep(5)
    
    print("\n检查服务状态...")
    subprocess.run([sys.executable, 'check_services.py'])

def main():
    """主函数"""
    print("=" * 60)
    print("修复配置并重启服务")
    print("=" * 60)
    
    # 检查配置文件
    if not os.path.exists('config.json'):
        print("\n错误: config.json 不存在")
        sys.exit(1)
    
    # 显示当前配置
    config = check_config()
    
    # 停止服务
    stop_services()
    
    # 更新前端环境变量
    api_url = config['frontend']['api_url']
    update_frontend_env(api_url)
    
    # 启动服务
    if not start_services():
        sys.exit(1)
    
    # 等待并检查
    wait_and_check()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print(f"\n访问地址:")
    print(f"  前端: {config['frontend']['public_url']}")
    print(f"  后端: {config['backend']['public_url']}")
    print("\n提示:")
    print("  - 如果无法访问，运行: python logs.py frontend-error")
    print("  - 检查防火墙是否开放端口")
    print("  - 使用 'python check_services.py' 验证服务状态")
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
