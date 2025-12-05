<template>
  <div>
    <div class="card">
      <div class="header">
        <h2>下载管理</h2>
        <div class="header-actions">
          <select v-model="selectedPlatform" @change="loadDownloads" class="platform-select">
            <option value="all">全部平台</option>
            <option v-for="plugin in enabledDownloadPlugins" :key="plugin.name" :value="plugin.name">
              {{ getPlatformDisplayName(plugin.name) }}
            </option>
          </select>
          <button @click="showAddDialog = true" class="btn btn-success">
            + 新增下载
          </button>
          <button @click="refreshDownloads" class="btn btn-primary" :disabled="loading">
            {{ loading ? '刷新中...' : '刷新' }}
          </button>
        </div>
      </div>
      
      <!-- 新增下载对话框 -->
      <div v-if="showAddDialog" class="dialog-overlay" @click.self="showAddDialog = false">
        <div class="dialog">
          <div class="dialog-header">
            <h3>新增下载</h3>
            <button @click="showAddDialog = false" class="btn-close">×</button>
          </div>
          <div class="dialog-body">
            <div class="form-field">
              <label>下载链接 *</label>
              <input 
                v-model="newDownload.url" 
                type="text" 
                placeholder="输入视频链接、m3u8链接或磁力链接"
                @keyup.enter="submitNewDownload"
              />
            </div>
            <div class="form-field">
              <label>标题</label>
              <input 
                v-model="newDownload.title" 
                type="text" 
                placeholder="可选，留空将自动生成"
                @keyup.enter="submitNewDownload"
              />
            </div>
            <div class="form-field">
              <label>下载插件</label>
              <select v-model="newDownload.plugin">
                <option value="">自动选择</option>
                <option v-for="plugin in enabledDownloadPlugins" :key="plugin.name" :value="plugin.name">
                  {{ getPlatformDisplayName(plugin.name) }}
                </option>
              </select>
            </div>
          </div>
          <div class="dialog-footer">
            <button @click="showAddDialog = false" class="btn btn-secondary">
              取消
            </button>
            <button @click="submitNewDownload" class="btn btn-primary" :disabled="!newDownload.url">
              开始下载
            </button>
          </div>
        </div>
      </div>
      
      <div v-if="loading && downloads.length === 0" class="loading">
        <p>加载中...</p>
      </div>
      
      <div v-else-if="downloads.length === 0" class="empty">
        <p>暂无下载任务</p>
        <p class="hint">在搜索页面添加下载任务后，会在这里显示</p>
      </div>
      
      <!-- 按平台分组显示 -->
      <div v-else class="downloads">
        <div v-for="platformGroup in platformGroups" :key="platformGroup.name" class="platform-group">
          <div class="platform-header">
            <h3>{{ getPlatformDisplayName(platformGroup.name) }}</h3>
            <a 
              v-if="platformGroup.web_ui_url" 
              :href="platformGroup.web_ui_url" 
              target="_blank" 
              class="btn btn-link"
            >
              🔗 打开平台
            </a>
          </div>
          
          <div class="download-list">
            <div v-for="download in platformGroup.downloads" :key="download.id" class="download-card">
              <div class="download-info">
                <h4>{{ download.title }}</h4>
                <div class="download-meta">
                  <span class="meta-item">
                    <strong>状态:</strong> 
                    <span :class="['status', `status-${download.status}`]">
                      {{ getStatusText(download.status) }}
                    </span>
                  </span>
                  <span v-if="download.created_at" class="meta-item">
                    <strong>时间:</strong> {{ formatTime(download.created_at) }}
                  </span>
                </div>
                <div class="download-url">{{ download.url }}</div>
                
                <div v-if="download.status === 'downloading' || download.status === 'pending'" class="progress-bar">
                  <div class="progress-fill" :style="{ width: download.progress + '%' }"></div>
                  <span class="progress-text">
                    {{ download.progress.toFixed(1) }}%
                    <span v-if="download.speed" class="progress-extra"> · {{ download.speed }}</span>
                    <span v-if="download.eta" class="progress-extra"> · ETA: {{ download.eta }}</span>
                  </span>
                </div>
              </div>
              
              <div class="download-actions">
                <button 
                  v-if="download.status === 'pending' || download.status === 'downloading'" 
                  @click="cancelDownload(download.platform, download.id)"
                  class="btn btn-warning"
                >
                  取消
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import toast from '../utils/toast'

export default {
  name: 'Downloads',
  data() {
    return {
      selectedPlatform: 'all',
      downloads: [],
      platformGroups: [],
      downloadPlugins: [],
      loading: false,
      refreshTimer: null,
      showAddDialog: false,
      newDownload: {
        url: '',
        title: '',
        plugin: ''
      }
    }
  },
  computed: {
    enabledDownloadPlugins() {
      // 只返回启用的下载插件
      return this.downloadPlugins.filter(plugin => plugin.enabled !== false)
    }
  },
  created() {
    this.$toast = toast
  },
  async mounted() {
    await this.loadPlugins()
    await this.loadDownloads()
    // 每10秒自动刷新
    this.refreshTimer = setInterval(() => {
      this.loadDownloads(true)
    }, 10000)
  },
  beforeUnmount() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer)
    }
  },
  methods: {
    async loadPlugins() {
      try {
        const response = await axios.get('/api/plugins')
        this.downloadPlugins = response.data.download || []
      } catch (error) {
        console.error('加载插件失败:', error)
      }
    },
    async loadDownloads(silent = false) {
      if (!silent) {
        this.loading = true
      }
      
      try {
        const response = await axios.get('/api/downloads', {
          params: { platform: this.selectedPlatform }
        })
        
        if (this.selectedPlatform === 'all') {
          // 聚合模式
          this.platformGroups = response.data.platforms || []
          this.downloads = []
          this.platformGroups.forEach(pg => {
            this.downloads.push(...pg.downloads)
          })
        } else {
          // 单平台模式
          this.platformGroups = [{
            name: response.data.platform,
            web_ui_url: response.data.web_ui_url,
            downloads: response.data.downloads || []
          }]
          this.downloads = response.data.downloads || []
        }
      } catch (error) {
        console.error('加载下载记录失败:', error)
        if (!silent) {
          this.$toast.error('加载失败', error.response?.data?.detail || error.message)
        }
      } finally {
        this.loading = false
      }
    },
    async refreshDownloads() {
      await this.loadDownloads()
      this.$toast.success('已刷新')
    },
    async cancelDownload(platform, downloadId) {
      if (!confirm('确定要取消这个下载任务吗？')) {
        return
      }
      
      try {
        await axios.post('/api/downloads/cancel', {
          platform: platform,
          download_id: downloadId
        })
        
        await this.loadDownloads()
        this.$toast.success('任务已取消')
      } catch (error) {
        console.error('取消任务失败:', error)
        this.$toast.error('取消失败', error.response?.data?.detail || error.message)
      }
    },
    async submitNewDownload() {
      if (!this.newDownload.url) {
        this.$toast.error('请输入下载链接')
        return
      }
      
      try {
        const title = this.newDownload.title || `下载任务 ${new Date().toLocaleString()}`
        
        await axios.post('/api/download', {
          url: this.newDownload.url,
          title: title,
          plugin_name: this.newDownload.plugin || null
        })
        
        this.showAddDialog = false
        this.newDownload = {
          url: '',
          title: '',
          plugin: ''
        }
        
        await this.loadDownloads()
        this.$toast.success('下载任务已添加')
      } catch (error) {
        console.error('添加下载失败:', error)
        this.$toast.error('添加失败', error.response?.data?.detail || error.message)
      }
    },
    getPlatformDisplayName(platform) {
      const names = {
        'metube': 'MeTube',
        'qbittorrent': 'qBittorrent'
      }
      return names[platform] || platform
    },
    getStatusText(status) {
      const statusMap = {
        'pending': '等待中',
        'downloading': '下载中',
        'completed': '已完成',
        'failed': '失败',
        'cancelled': '已取消',
        'paused': '已暂停',
        'unknown': '未知'
      }
      return statusMap[status] || status
    },
    formatTime(timeStr) {
      if (!timeStr) return '-'
      
      // 如果是Unix时间戳（数字）
      if (typeof timeStr === 'number') {
        const date = new Date(timeStr * 1000)
        return date.toLocaleString('zh-CN')
      }
      
      // 如果是ISO字符串
      const date = new Date(timeStr)
      return date.toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.platform-select {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
}

.platform-select:focus {
  outline: none;
  border-color: #3498db;
}

.loading,
.empty {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.empty .hint {
  font-size: 0.9rem;
  color: #999;
  margin-top: 0.5rem;
}

.downloads {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.platform-group {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid #e0e0e0;
}

.platform-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #ddd;
}

.platform-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.btn-link {
  color: #3498db;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border: 1px solid #3498db;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-link:hover {
  background: #3498db;
  color: white;
}

.download-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.download-card {
  background: white;
  border-radius: 6px;
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  border: 1px solid #e0e0e0;
}

.download-info {
  flex: 1;
}

.download-info h4 {
  margin: 0 0 0.75rem 0;
  color: #2c3e50;
  font-size: 1rem;
}

.download-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.meta-item {
  font-size: 0.9rem;
  color: #666;
}

.status {
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-pending {
  background: #f39c12;
  color: white;
}

.status-downloading {
  background: #3498db;
  color: white;
}

.status-completed {
  background: #27ae60;
  color: white;
}

.status-failed {
  background: #e74c3c;
  color: white;
}

.status-cancelled {
  background: #95a5a6;
  color: white;
}

.status-paused {
  background: #95a5a6;
  color: white;
}

.download-url {
  font-size: 0.85rem;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-top: 0.5rem;
}

.progress-bar {
  position: relative;
  height: 24px;
  background: #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  margin-top: 1rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2980b9);
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.85rem;
  font-weight: 600;
  color: #2c3e50;
  white-space: nowrap;
}

.progress-extra {
  font-weight: normal;
  font-size: 0.8rem;
}

.download-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.download-actions .btn {
  white-space: nowrap;
  min-width: 80px;
}

.btn-success {
  background: #27ae60;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-success:hover {
  background: #229954;
}

.btn-warning {
  background: #f39c12;
  color: white;
}

.btn-warning:hover {
  background: #e67e22;
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.dialog-header h3 {
  margin: 0;
  color: #2c3e50;
}

.btn-close {
  background: none;
  border: none;
  font-size: 2rem;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.btn-close:hover {
  color: #333;
}

.dialog-body {
  padding: 1.5rem;
}

.form-field {
  margin-bottom: 1.5rem;
}

.form-field:last-child {
  margin-bottom: 0;
}

.form-field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-field input,
.form-field select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-field input:focus,
.form-field select:focus {
  outline: none;
  border-color: #3498db;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e0e0e0;
}
</style>
