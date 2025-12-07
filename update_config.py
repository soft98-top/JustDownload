#!/usr/bin/env python3
"""
更新配置文件
"""
import json
import sys

def update_config():
    """交互式更新配置"""
    print("=" * 60)
    print("配置更新工具")
    print("=" * 60)
    
    # 读取当前配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("\n当前配置:")
        print(f"  后端: {config['backend']['public_url']}")
        print(f"  前端: {config['frontend']['public_url']}")
        print(f"  API: {config['frontend']['api_url']}")
    except FileNotFoundError:
        print("\n配置文件不存在，将创建新配置")
        config = {
            "backend": {
                "host": "0.0.0.0",
                "port": 8000,
                "public_url": "http://localhost:8000"
            },
            "frontend": {
                "host": "0.0.0.0",
                "port": 5173,
                "public_url": "http://localhost:5173",
                "api_url": "http://localhost:8000"
            }
        }
    
    print("\n" + "=" * 60)
    print("请输入新配置（直接回车保持当前值）")
    print("=" * 60)
    
    # 后端配置
    print("\n后端配置:")
    backend_host = input(f"  监听地址 [{config['backend']['host']}]: ").strip()
    if backend_host:
        config['backend']['host'] = backend_host
    
    backend_port = input(f"  端口 [{config['backend']['port']}]: ").strip()
    if backend_port:
        config['backend']['port'] = int(backend_port)
    
    backend_url = input(f"  对外访问地址 [{config['backend']['public_url']}]: ").strip()
    if backend_url:
        config['backend']['public_url'] = backend_url
    
    # 前端配置
    print("\n前端配置:")
    frontend_host = input(f"  监听地址 [{config['frontend']['host']}]: ").strip()
    if frontend_host:
        config['frontend']['host'] = frontend_host
    
    frontend_port = input(f"  端口 [{config['frontend']['port']}]: ").strip()
    if frontend_port:
        config['frontend']['port'] = int(frontend_port)
    
    frontend_url = input(f"  对外访问地址 [{config['frontend']['public_url']}]: ").strip()
    if frontend_url:
        config['frontend']['public_url'] = frontend_url
    
    api_url = input(f"  后端 API 地址 [{config['frontend']['api_url']}]: ").strip()
    if api_url:
        config['frontend']['api_url'] = api_url
    
    # 显示新配置
    print("\n" + "=" * 60)
    print("新配置:")
    print("=" * 60)
    print(json.dumps(config, indent=2, ensure_ascii=False))
    
    # 确认保存
    print("\n" + "=" * 60)
    confirm = input("保存配置? (y/n): ").strip().lower()
    
    if confirm == 'y':
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("\n✓ 配置已保存到 config.json")
        print("\n提示: 运行 'python stop.py && python start.py' 重启服务使配置生效")
    else:
        print("\n✗ 配置未保存")

def quick_update():
    """快速更新（命令行参数）"""
    if len(sys.argv) < 2:
        return False
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("错误: config.json 不存在")
        return True
    
    # 解析参数
    for arg in sys.argv[1:]:
        if '=' not in arg:
            continue
        
        key, value = arg.split('=', 1)
        
        if key == 'backend.port':
            config['backend']['port'] = int(value)
        elif key == 'frontend.port':
            config['frontend']['port'] = int(value)
        elif key == 'backend.host':
            config['backend']['host'] = value
        elif key == 'frontend.host':
            config['frontend']['host'] = value
        elif key == 'backend.url':
            config['backend']['public_url'] = value
        elif key == 'frontend.url':
            config['frontend']['public_url'] = value
        elif key == 'api.url':
            config['frontend']['api_url'] = value
        else:
            print(f"未知参数: {key}")
    
    # 保存配置
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✓ 配置已更新")
    print("\n新配置:")
    print(json.dumps(config, indent=2, ensure_ascii=False))
    
    return True

def main():
    """主函数"""
    # 检查是否有命令行参数
    if quick_update():
        return
    
    # 交互式更新
    try:
        update_config()
    except KeyboardInterrupt:
        print("\n\n✗ 已取消")
        sys.exit(0)

if __name__ == '__main__':
    main()
