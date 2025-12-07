from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
import argparse
import os
import asyncio

from logger import setup_logging, get_logger
from plugin_manager import PluginManager
from models import DownloadTask

# 解析命令行参数
parser = argparse.ArgumentParser(description='模块化下载系统')
parser.add_argument('--log-level', 
                    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                    default=os.getenv('LOG_LEVEL', 'INFO'),
                    help='日志级别 (默认: INFO)')
parser.add_argument('--verbose', '-v',
                    action='store_true',
                    default=os.getenv('VERBOSE', '').lower() in ('true', '1', 'yes'),
                    help='启用详细日志模式')
parser.add_argument('--host',
                    default='0.0.0.0',
                    help='服务器主机地址 (默认: 0.0.0.0)')
parser.add_argument('--port',
                    type=int,
                    default=8000,
                    help='服务器端口 (默认: 8000)')

args, unknown = parser.parse_known_args()

# 配置日志
setup_logging(level=args.log_level, verbose=args.verbose)
logger = get_logger(__name__)

logger.info(f"启动模块化下载系统 - 日志级别: {args.log_level}, 详细模式: {args.verbose}")

app = FastAPI(title="模块化下载系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

plugin_manager = PluginManager()

# 自动扫描并加载所有插件
logger.info("开始自动扫描并加载插件...")
try:
    success_count, fail_count = plugin_manager.auto_discover_plugins()
    logger.info(f"插件自动加载完成: 成功 {success_count}, 失败 {fail_count}（所有插件默认禁用状态）")
except Exception as e:
    logger.error(f"插件自动加载失败: {e}", exc_info=True)

@app.get("/")
async def root():
    logger.debug("访问根路径")
    return {"message": "模块化下载系统 API", "status": "running"}

@app.get("/api/plugins")
async def list_plugins():
    """列出所有插件"""
    logger.debug("获取插件列表")
    plugins = plugin_manager.list_plugins()
    logger.debug(f"返回 {len(plugins['search'])} 个搜索插件, {len(plugins['download'])} 个下载插件, {len(plugins.get('parser', []))} 个解析器插件")
    return plugins


@app.get("/api/plugins/{plugin_type}/{plugin_name}/config")
async def get_plugin_config(plugin_type: str, plugin_name: str):
    """获取插件配置"""
    try:
        from config_storage import get_config_storage
        storage = get_config_storage()
        config = storage.get(plugin_type, plugin_name)
        return {"config": config}
    except Exception as e:
        logger.error(f"获取插件配置失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plugins/{plugin_type}/{plugin_name}/config")
async def set_plugin_config(plugin_type: str, plugin_name: str, config: Dict[str, Any]):
    """设置插件配置"""
    logger.info(f"设置插件配置: {plugin_type}/{plugin_name}")
    logger.debug(f"配置内容: {config}")
    try:
        plugin_manager.set_plugin_config(plugin_type, plugin_name, config)
        logger.info(f"插件 {plugin_name} 配置成功")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"设置插件配置失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/plugins/{plugin_type}/{plugin_name}/toggle")
async def toggle_plugin(plugin_type: str, plugin_name: str, enabled: bool):
    """启用/禁用插件"""
    logger.info(f"切换插件状态: {plugin_type}/{plugin_name} -> {enabled}")
    try:
        from config_storage import get_config_storage
        storage = get_config_storage()
        storage.set_enabled(plugin_type, plugin_name, enabled)
        logger.info(f"插件 {plugin_name} 已{'启用' if enabled else '禁用'}")
        return {"status": "success", "enabled": enabled}
    except Exception as e:
        logger.error(f"切换插件状态失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search/async")
async def create_search_task(plugin_name: str, keyword: str):
    """创建异步搜索任务"""
    logger.info(f"创建异步搜索任务: 插件={plugin_name}, 关键词={keyword}")
    
    plugin = plugin_manager.get_search_plugin(plugin_name)
    if not plugin:
        logger.error(f"插件未找到: {plugin_name}")
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    try:
        from search_task_manager import get_task_manager
        task_manager = get_task_manager()
        
        # 创建任务
        task_id = task_manager.create_task(plugin_name, keyword)
        
        # 在后台执行搜索
        asyncio.create_task(task_manager.execute_search(task_id, plugin, keyword))
        
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "搜索任务已创建"
        }
    except Exception as e:
        logger.error(f"创建搜索任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/task/{task_id}")
async def get_search_task(task_id: str):
    """获取搜索任务状态"""
    try:
        from search_task_manager import get_task_manager
        task_manager = get_task_manager()
        
        task = task_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # 如果任务完成，添加解析后的播放链接
        if task.status == "completed" and task.results:
            active_parsers = plugin_manager.get_active_parsers()
            if active_parsers:
                for result in task.results:
                    if result.get("metadata") and result["metadata"].get("episodes"):
                        episodes = result["metadata"]["episodes"]
                        result["metadata"]["episodes"] = plugin_manager.parse_video_urls(episodes)
        
        return task.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取搜索任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/{plugin_name}")
async def search(plugin_name: str, keyword: str):
    """搜索（同步接口，保持向后兼容）"""
    logger.info(f"搜索请求: 插件={plugin_name}, 关键词={keyword}")
    
    plugin = plugin_manager.get_search_plugin(plugin_name)
    if not plugin:
        logger.error(f"插件未找到: {plugin_name}")
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    try:
        logger.debug(f"开始搜索...")
        results = await plugin.search(keyword)
        logger.info(f"搜索完成，找到 {len(results)} 个结果")
        logger.debug(f"结果预览: {[r.title for r in results[:3]]}")
        
        # 为搜索结果添加解析后的播放链接
        results_dict = [r.model_dump() for r in results]
        
        # 检查是否有启用的解析器
        active_parsers = plugin_manager.get_active_parsers()
        if active_parsers:
            for result in results_dict:
                # episodes 通常在 metadata 中
                if result.get("metadata") and result["metadata"].get("episodes"):
                    episodes = result["metadata"]["episodes"]
                    logger.debug(f"为视频 {result['title']} 的 {len(episodes)} 个剧集添加解析链接")
                    result["metadata"]["episodes"] = plugin_manager.parse_video_urls(episodes)
        else:
            logger.debug("没有启用的解析器，跳过URL解析")
        
        return {"results": results_dict}
    except Exception as e:
        logger.error(f"搜索失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

class VideoInfoRequest(BaseModel):
    url: str
    plugin_name: str

class DownloadRequest(BaseModel):
    url: str
    title: str
    plugin_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@app.post("/api/video-info")
async def get_video_info(request: VideoInfoRequest):
    """获取视频详细信息"""
    logger.info(f"获取视频详情: 插件={request.plugin_name}, URL={request.url[:100]}...")
    
    plugin = plugin_manager.get_search_plugin(request.plugin_name)
    if not plugin:
        logger.error(f"插件未找到: {request.plugin_name}")
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    try:
        logger.debug(f"开始获取视频详情...")
        video_info = await plugin.get_video_info(request.url)
        logger.info(f"视频详情获取成功: {video_info.title}")
        
        # 转换为字典
        result = video_info.model_dump()
        
        # 为剧集添加解析后的播放链接
        active_parsers = plugin_manager.get_active_parsers()
        if active_parsers and result.get("metadata") and result["metadata"].get("episodes"):
            episodes = result["metadata"]["episodes"]
            logger.debug(f"为 {len(episodes)} 个剧集添加解析链接")
            result["metadata"]["episodes"] = plugin_manager.parse_video_urls(episodes)
        
        return result
    except Exception as e:
        logger.error(f"获取视频详情失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取视频详情失败: {str(e)}")


@app.post("/api/download")
async def create_download_task(request: DownloadRequest):
    """创建下载任务"""
    logger.info(f"创建下载任务: {request.title}")
    logger.debug(f"下载请求详情: url={request.url[:100]}..., plugin={request.plugin_name}")
    
    try:
        # 选择下载插件
        if not request.plugin_name:
            logger.debug("自动选择下载插件...")
            plugin = plugin_manager.get_suitable_download_plugin(request.url)
            if not plugin:
                logger.error(f"未找到合适的下载插件，URL: {request.url}")
                raise HTTPException(status_code=400, detail="No suitable download plugin found")
            logger.info(f"自动选择插件: {plugin.name}")
        else:
            logger.debug(f"使用指定插件: {request.plugin_name}")
            plugin = plugin_manager.get_download_plugin(request.plugin_name)
            if not plugin:
                logger.error(f"插件未找到: {request.plugin_name}")
                raise HTTPException(status_code=404, detail="Plugin not found")
        
        # 创建任务
        task = DownloadTask(
            id=str(uuid.uuid4()),
            url=request.url,
            title=request.title,
            status="pending",
            plugin_name=plugin.name,
            save_path=plugin.config.get('download_path', '/downloads'),
            metadata=request.metadata or {}
        )
        
        logger.info(f"任务ID: {task.id}, 使用插件: {plugin.name}")
        logger.debug(f"保存路径: {task.save_path}")
        
        # 保存任务到数据库
        from database import get_database
        db = get_database()
        db.add_task(task.model_dump())
        
        # 执行下载（插件内部会更新任务状态）
        logger.debug("开始执行下载...")
        success = await plugin.download(task)
        
        if success:
            logger.info(f"下载任务创建成功: {task.id}")
            # 重新获取任务以获取最新状态
            updated_task = db.get_task(task.id)
            return {"status": "success", "task": updated_task or task.model_dump()}
        else:
            logger.error(f"下载失败: {task.id}")
            raise HTTPException(status_code=500, detail="Download failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建下载任务异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建下载任务失败: {str(e)}")


@app.get("/api/downloads")
async def get_downloads(platform: str = "all"):
    """获取下载记录（从下载插件查询）
    
    Args:
        platform: 平台名称 (all/metube/qbittorrent)
    """
    logger.info(f"查询下载记录: platform={platform}")
    
    try:
        if platform == "all":
            # 聚合所有平台的下载记录（只查询启用的插件）
            all_downloads = []
            platforms_info = []
            
            for plugin_info in plugin_manager.list_plugins()['download']:
                plugin_name = plugin_info['name']
                
                # 跳过禁用的插件
                if not plugin_info.get('enabled', True):
                    logger.debug(f"跳过禁用的插件: {plugin_name}")
                    continue
                
                plugin = plugin_manager.get_download_plugin(plugin_name)
                if plugin:
                    try:
                        downloads = await plugin.get_downloads()
                        web_ui_url = plugin.get_web_ui_url()
                        
                        platforms_info.append({
                            'name': plugin_name,
                            'web_ui_url': web_ui_url,
                            'downloads': downloads
                        })
                        
                        all_downloads.extend(downloads)
                    except Exception as e:
                        logger.error(f"获取 {plugin_name} 下载记录失败: {e}")
            
            logger.info(f"聚合查询完成，共 {len(all_downloads)} 条记录")
            
            return {
                "platform": "all",
                "platforms": platforms_info,
                "total": len(all_downloads)
            }
        else:
            # 查询指定平台
            plugin = plugin_manager.get_download_plugin(platform)
            if not plugin:
                raise HTTPException(status_code=404, detail=f"Platform {platform} not found")
            
            downloads = await plugin.get_downloads()
            web_ui_url = plugin.get_web_ui_url()
            
            logger.info(f"查询 {platform} 完成，共 {len(downloads)} 条记录")
            
            return {
                "platform": platform,
                "web_ui_url": web_ui_url,
                "downloads": downloads
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取下载记录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class CancelDownloadRequest(BaseModel):
    platform: str
    download_id: str


@app.post("/api/downloads/cancel")
async def cancel_download(request: CancelDownloadRequest):
    """取消下载任务
    
    Args:
        platform: 平台名称 (metube/qbittorrent)
        download_id: 平台的下载ID
    """
    logger.info(f"取消下载任务: platform={request.platform}, id={request.download_id}")
    
    try:
        # 获取插件
        plugin = plugin_manager.get_download_plugin(request.platform)
        if not plugin:
            raise HTTPException(status_code=404, detail=f"Platform {request.platform} not found")
        
        # 调用插件取消
        success = await plugin.cancel(request.download_id)
        
        if success:
            logger.info(f"✓ 任务已取消: {request.platform}/{request.download_id}")
            return {"status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Failed to cancel download")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 插件管理 API ====================

class InstallPluginRequest(BaseModel):
    url: str
    plugin_type: str  # search/download/parser


@app.post("/api/plugins/install")
async def install_plugin(request: InstallPluginRequest):
    """在线安装插件（支持热加载）"""
    logger.info(f"安装插件: {request.url}")
    
    try:
        import httpx
        import os
        import re
        
        # 下载插件文件
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(request.url)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="无法下载插件文件")
            
            plugin_code = response.text
        
        # 提取插件名称
        name_match = re.search(r'def name\(self\).*?return\s+["\'](\w+)["\']', plugin_code, re.DOTALL)
        if not name_match:
            raise HTTPException(status_code=400, detail="无法解析插件名称")
        
        plugin_name = name_match.group(1)
        
        # 保存插件文件
        plugin_dir = os.path.join("plugins", request.plugin_type)
        
        # 确保插件目录存在
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)
            logger.info(f"创建插件目录: {plugin_dir}")
        
        plugin_path = os.path.join(plugin_dir, f"{plugin_name}_plugin.py")
        
        if os.path.exists(plugin_path):
            raise HTTPException(status_code=400, detail="插件已存在")
        
        with open(plugin_path, 'w', encoding='utf-8') as f:
            f.write(plugin_code)
        
        logger.info(f"插件文件已保存: {plugin_path}")
        
        # 检查是否有requirements文件
        requirements_url = request.url.replace('.py', '_requirements.txt')
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                req_response = await client.get(requirements_url)
                if req_response.status_code == 200:
                    req_path = os.path.join(plugin_dir, f"{plugin_name}_requirements.txt")
                    with open(req_path, 'w', encoding='utf-8') as f:
                        f.write(req_response.text)
                    
                    logger.info(f"依赖文件已保存: {req_path}")
                    
                    # 安装依赖
                    import subprocess
                    result = subprocess.run(
                        ['pip', 'install', '-r', req_path],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode != 0:
                        logger.warning(f"依赖安装失败: {result.stderr}")
        except:
            pass
        
        # 热加载插件
        hot_load_success = plugin_manager.hot_load_plugin(request.plugin_type, plugin_name)
        
        if hot_load_success:
            logger.info(f"插件安装并热加载成功: {plugin_name}")
            return {
                "status": "success",
                "plugin_name": plugin_name,
                "hot_loaded": True,
                "message": "插件安装成功并已加载，可以立即使用"
            }
        else:
            logger.warning(f"插件安装成功但热加载失败: {plugin_name}")
            return {
                "status": "success",
                "plugin_name": plugin_name,
                "hot_loaded": False,
                "message": "插件安装成功，请重启服务以加载插件"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"安装插件失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class DeletePluginRequest(BaseModel):
    plugin_type: str  # search/download/parser
    plugin_name: str


@app.post("/api/plugins/delete")
async def delete_plugin(request: DeletePluginRequest):
    """删除插件（支持热卸载）"""
    logger.info(f"删除插件: {request.plugin_type}/{request.plugin_name}")
    
    try:
        import os
        
        plugin_dir = os.path.join("plugins", request.plugin_type)
        plugin_path = os.path.join(plugin_dir, f"{request.plugin_name}_plugin.py")
        req_path = os.path.join(plugin_dir, f"{request.plugin_name}_requirements.txt")
        
        if not os.path.exists(plugin_path):
            raise HTTPException(status_code=404, detail="插件不存在")
        
        # 先热卸载插件
        unregister_success = plugin_manager.unregister_plugin(request.plugin_type, request.plugin_name)
        
        # 删除插件文件
        os.remove(plugin_path)
        
        # 删除requirements文件（如果存在）
        if os.path.exists(req_path):
            os.remove(req_path)
        
        # 从配置中删除
        from config_storage import get_config_storage
        storage = get_config_storage()
        config_key = f"{request.plugin_type}:{request.plugin_name}"
        # TODO: 添加删除配置的方法
        
        if unregister_success:
            logger.info(f"插件删除并热卸载成功: {request.plugin_name}")
            return {
                "status": "success",
                "hot_unloaded": True,
                "message": "插件删除成功并已卸载"
            }
        else:
            logger.warning(f"插件删除成功但热卸载失败: {request.plugin_name}")
            return {
                "status": "success",
                "hot_unloaded": False,
                "message": "插件删除成功，请重启服务以生效"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除插件失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/plugins/reload")
async def reload_plugins():
    """重新加载所有插件"""
    logger.info("重新加载所有插件")
    
    try:
        success_count, fail_count = plugin_manager.reload_all_plugins()
        
        return {
            "status": "success",
            "success_count": success_count,
            "fail_count": fail_count,
            "message": f"插件重新加载完成: 成功 {success_count}, 失败 {fail_count}"
        }
        
    except Exception as e:
        logger.error(f"重新加载插件失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 配置导入导出 API ====================

@app.get("/api/config/export")
async def export_config():
    """导出所有配置"""
    logger.info("导出配置")
    
    try:
        import json
        import os
        
        # 获取配置文件路径（相对于当前工作目录）
        config_path = os.path.join('config', 'plugins.json')
        
        # 如果文件不存在，返回空配置
        if not os.path.exists(config_path):
            logger.warning(f"配置文件不存在: {config_path}")
            return {
                "status": "success",
                "config": {},
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }
        
        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        logger.info(f"配置导出成功，包含 {len(config_data)} 个插件配置")
        
        return {
            "status": "success",
            "config": config_data,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"导出配置失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class ImportConfigRequest(BaseModel):
    config: Dict[str, Any]


@app.post("/api/config/import")
async def import_config(request: ImportConfigRequest):
    """导入配置"""
    logger.info("导入配置")
    
    try:
        import json
        import os
        
        # 确保config目录存在
        config_dir = 'config'
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            logger.info(f"创建配置目录: {config_dir}")
        
        # 保存配置
        config_path = os.path.join(config_dir, 'plugins.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(request.config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"配置文件已保存，包含 {len(request.config)} 个插件配置")
        
        # 重新加载配置存储
        from config_storage import get_config_storage
        storage = get_config_storage()
        storage.reload()
        logger.info("配置存储已重新加载")
        
        # 重新加载所有插件的配置到内存
        reload_count = 0
        for config_key in request.config.keys():
            if ':' in config_key:
                plugin_type, plugin_name = config_key.split(':', 1)
                config_data = request.config[config_key]
                
                # 获取插件实例并更新配置
                plugin = None
                if plugin_type == "search":
                    plugin = plugin_manager.get_search_plugin(plugin_name)
                elif plugin_type == "download":
                    plugin = plugin_manager.get_download_plugin(plugin_name)
                elif plugin_type == "parser":
                    plugin = plugin_manager.get_parser_plugin(plugin_name)
                
                if plugin:
                    plugin.set_config(config_data)
                    reload_count += 1
                    logger.info(f"已更新插件配置到内存: {plugin_type}/{plugin_name}")
        
        logger.info(f"配置导入成功，已更新 {reload_count} 个插件的内存配置")
        return {
            "status": "success",
            "reloaded_count": reload_count,
            "message": f"配置导入成功，已更新 {reload_count} 个插件配置"
        }
        
    except Exception as e:
        logger.error(f"导入配置失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))




if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"启动服务器: {args.host}:{args.port}")
    
    # 配置uvicorn日志
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["default"]["fmt"] = "%(levelprefix)s %(message)s"
    log_config["formatters"]["access"]["fmt"] = '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    
    uvicorn.run(
        app, 
        host=args.host, 
        port=args.port,
        log_level=args.log_level.lower(),
        log_config=log_config
    )
