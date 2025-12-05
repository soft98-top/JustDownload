#!/usr/bin/env python3
"""
测试数据库功能
"""
import sys
import asyncio
from database import get_database
from models import DownloadTask

def test_database():
    """测试数据库基本功能"""
    print("=" * 60)
    print("测试数据库功能")
    print("=" * 60)
    
    db = get_database()
    
    # 1. 创建测试任务
    print("\n1. 创建测试任务...")
    task = DownloadTask(
        id="test-task-001",
        url="https://example.com/video.mp4",
        title="测试视频",
        status="pending",
        progress=0.0,
        plugin_name="metube",
        save_path="/downloads",
        metadata={"test": True}
    )
    
    success = db.add_task(task.model_dump())
    if success:
        print("✓ 任务创建成功")
    else:
        print("✗ 任务创建失败")
        return False
    
    # 2. 获取任务
    print("\n2. 获取任务...")
    retrieved_task = db.get_task("test-task-001")
    if retrieved_task:
        print(f"✓ 任务获取成功: {retrieved_task['title']}")
        print(f"  状态: {retrieved_task['status']}")
        print(f"  进度: {retrieved_task['progress']}%")
    else:
        print("✗ 任务获取失败")
        return False
    
    # 3. 更新任务
    print("\n3. 更新任务状态...")
    success = db.update_task("test-task-001", {
        "status": "downloading",
        "progress": 50.0
    })
    if success:
        print("✓ 任务更新成功")
        updated_task = db.get_task("test-task-001")
        print(f"  新状态: {updated_task['status']}")
        print(f"  新进度: {updated_task['progress']}%")
    else:
        print("✗ 任务更新失败")
        return False
    
    # 4. 获取所有任务
    print("\n4. 获取所有任务...")
    all_tasks = db.get_all_tasks()
    print(f"✓ 找到 {len(all_tasks)} 个任务")
    for t in all_tasks:
        print(f"  - {t['id']}: {t['title']} ({t['status']})")
    
    # 5. 根据状态获取任务
    print("\n5. 获取下载中的任务...")
    downloading_tasks = db.get_tasks_by_status("downloading")
    print(f"✓ 找到 {len(downloading_tasks)} 个下载中的任务")
    
    # 6. 删除任务
    print("\n6. 删除测试任务...")
    success = db.delete_task("test-task-001")
    if success:
        print("✓ 任务删除成功")
    else:
        print("✗ 任务删除失败")
        return False
    
    # 验证删除
    deleted_task = db.get_task("test-task-001")
    if deleted_task is None:
        print("✓ 确认任务已删除")
    else:
        print("✗ 任务仍然存在")
        return False
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
