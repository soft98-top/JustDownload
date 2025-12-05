from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
import argparse
import os

from logger import setup_logging, get_logger
from plugin_manager import PluginManager
from plugins.search.youtube_plugin import YouTubeSearchPlugin
from plugins.search.seacms_plugin import SeaCMSSearchPlugin
from plugins.download.metube_plugin import MetubeDownloadPlugin
from plugins.download.qbittorrent_plugin import QBittorrentDownloadPlugin
from plugins.parser.m3u8_parser_plugin import M3U8ParserPlugin
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

# 注册插件
logger.info("开始注册插件...")
try:
    plugin_manager.register_search_plugin(YouTubeSearchPlugin())
    plugin_manager.register_search_plugin(SeaCMSSearchPlugin())
    plugin_manager.register_download_plugin(MetubeDownloadPlugin())
    plugin_manager.register_download_plugin(QBittorrentDownloadPlugin())
    plugin_manager.register_parser_plugin(M3U8ParserPlugin())
    logger.info("所有插件注册完成")
except Exception as e:
    logger.error(f"插件注册失败: {e}", exc_info=True)

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

@app.get("/api/search/{plugin_name}")
async def search(plugin_name: str, keyword: str):
    """搜索"""
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

class DownloadRequest(BaseModel):
    url: str
    title: str
    plugin_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


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
