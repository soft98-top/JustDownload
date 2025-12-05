<template>
  <div>
    <div class="card">
      <div class="header-row">
        <h2>视频搜索</h2>
        <button 
          v-if="results.length > 0" 
          @click="clearResults" 
          class="btn btn-secondary btn-sm"
          title="清除搜索结果"
        >
          清除结果
        </button>
      </div>
      <div class="search-form">
        <select v-model="selectedPlugin" v-if="enabledSearchPlugins.length > 0">
          <option v-for="plugin in enabledSearchPlugins" :key="plugin.name" :value="plugin.name">
            {{ plugin.description }}
          </option>
        </select>
        <div v-else class="no-plugins-warning">
          <span>⚠️ 没有启用的搜索插件，请前往设置页面启用</span>
        </div>
        <input 
          v-model="keyword" 
          @keyup.enter="search"
          placeholder="输入搜索关键词"
          :disabled="enabledSearchPlugins.length === 0"
        />
        <button 
          @click="search" 
          class="btn btn-primary"
          :disabled="enabledSearchPlugins.length === 0"
        >
          搜索
        </button>
      </div>
    </div>

    <div v-if="loading" class="card">
      <p>搜索中...</p>
    </div>

    <div v-if="results.length > 0" class="results">
      <div v-for="result in results" :key="result.url" class="card result-item">
        <img v-if="result.thumbnail" :src="result.thumbnail" :alt="result.title" />
        <div class="result-info">
          <h3>{{ result.title }}</h3>
          <p class="result-meta">
            <span v-if="result.metadata?.note">{{ result.metadata.note }}</span>
            <span v-if="result.metadata?.episode_count"> · {{ result.metadata.episode_count }}集</span>
            <span> · 来源: {{ result.platform }}</span>
          </p>
          <p v-if="result.description" class="result-description">{{ result.description }}</p>
          
          <div class="action-buttons">
            <button @click="openVideoDetail(result)" class="btn btn-primary">
              <span class="play-icon">▶</span> 播放
            </button>
            <button @click="openDownloadDialog(result)" class="btn btn-success">下载</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 视频详情对话框 -->
    <VideoDetailDialog
      :show="showVideoDetail"
      :video="currentResult || {}"
      @close="showVideoDetail = false"
    />
    
    <!-- 下载对话框 -->
    <DownloadDialog
      :show="showDownloadDialog"
      :result="currentResult"
      :downloadPlugins="downloadPlugins"
      @close="showDownloadDialog = false"
      @download="handleDownload"
    />
  </div>
</template>

<script>
import axios from 'axios'
import DownloadDialog from '../components/DownloadDialog.vue'
import VideoDetailDialog from '../components/VideoDetailDialog.vue'
import toast from '../utils/toast'

export default {
  components: {
    DownloadDialog,
    VideoDetailDialog
  },
  created() {
    this.$toast = toast
  },
  data() {
    return {
      searchPlugins: [],
      downloadPlugins: [],
      selectedPlugin: '',
      keyword: '',
      results: [],
      loading: false,
      showDownloadDialog: false,
      showVideoDetail: false,
      currentResult: null
    }
  },
  computed: {
    enabledSearchPlugins() {
      // 只返回启用的搜索插件
      return this.searchPlugins.filter(plugin => plugin.enabled !== false)
    }
  },
  async mounted() {
    await this.loadPlugins()
    this.loadSearchCache()
  },
  methods: {
    async loadPlugins() {
      try {
        const response = await axios.get('/api/plugins')
        this.searchPlugins = response.data.search || []
        this.downloadPlugins = response.data.download || []
        
        // 默认选择第一个启用的搜索插件
        const enabledPlugins = this.searchPlugins.filter(p => p.enabled !== false)
        if (enabledPlugins.length > 0) {
          this.selectedPlugin = enabledPlugins[0].name
        }
      } catch (error) {
        console.error('加载插件失败:', error)
        this.$toast.error('加载插件失败', error.message)
      }
    },
    loadSearchCache() {
      try {
        const cached = localStorage.getItem('search_cache')
        if (cached) {
          const data = JSON.parse(cached)
          // 检查缓存是否过期（24小时）
          const cacheTime = new Date(data.timestamp).getTime()
          const now = new Date().getTime()
          const hoursDiff = (now - cacheTime) / (1000 * 60 * 60)
          
          if (hoursDiff < 24) {
            this.results = data.results || []
            this.keyword = data.keyword || ''
            this.selectedPlugin = data.plugin || this.selectedPlugin
            console.log(`已恢复 ${this.results.length} 条搜索结果`)
          } else {
            // 缓存过期，清除
            localStorage.removeItem('search_cache')
          }
        }
      } catch (error) {
        console.error('加载搜索缓存失败:', error)
        localStorage.removeItem('search_cache')
      }
    },
    saveSearchCache() {
      try {
        const cacheData = {
          results: this.results,
          keyword: this.keyword,
          plugin: this.selectedPlugin,
          timestamp: new Date().toISOString()
        }
        localStorage.setItem('search_cache', JSON.stringify(cacheData))
      } catch (error) {
        console.error('保存搜索缓存失败:', error)
      }
    },
    clearResults() {
      this.results = []
      this.keyword = ''
      localStorage.removeItem('search_cache')
      this.$toast.info('已清除搜索结果')
    },
    async search() {
      if (!this.selectedPlugin || !this.keyword) {
        this.$toast.warning('请选择插件并输入关键词')
        return
      }

      this.loading = true
      try {
        const response = await axios.get(`/api/search/${this.selectedPlugin}`, {
          params: { keyword: this.keyword }
        })
        this.results = response.data.results
        
        // 保存搜索结果到缓存
        this.saveSearchCache()
        
        if (this.results.length === 0) {
          this.$toast.info('未找到结果', '请尝试其他关键词')
        } else {
          this.$toast.success(`找到 ${this.results.length} 个结果`)
        }
      } catch (error) {
        console.error('搜索失败:', error)
        this.$toast.error('搜索失败', error.response?.data?.detail || error.message)
      } finally {
        this.loading = false
      }
    },
    openVideoDetail(result) {
      this.currentResult = result
      this.showVideoDetail = true
    },
    openDownloadDialog(result) {
      this.currentResult = result
      this.showDownloadDialog = true
    },
    async handleDownload(downloadData) {
      try {
        const response = await axios.post('/api/download', downloadData)
        
        // 构建成功消息
        let message = `使用插件: ${response.data.task.plugin_name}`
        if (downloadData.metadata?.episode) {
          message += `\n剧集: ${downloadData.metadata.episode}`
        }
        if (downloadData.metadata?.parser) {
          message += `\n解析器: ${downloadData.metadata.parser}`
        }
        
        this.$toast.success('下载任务已创建', message)
      } catch (error) {
        console.error('创建下载任务失败:', error)
        const errorMsg = error.response?.data?.detail || '创建下载任务失败'
        this.$toast.error('下载失败', errorMsg)
      }
    }
  }
}
</script>

<style scoped>
.search-form {
  display: grid;
  grid-template-columns: 200px 1fr auto;
  gap: 1rem;
  margin-top: 1rem;
}

.no-plugins-warning {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
  color: #856404;
  font-size: 0.9rem;
}

.search-form input:disabled,
.search-form button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.results {
  display: grid;
  gap: 1rem;
}

.result-item {
  display: flex;
  gap: 1rem;
}

.result-item img {
  width: 120px;
  height: 90px;
  object-fit: cover;
  border-radius: 4px;
}

.result-info {
  flex: 1;
}

.result-info h3 {
  margin-bottom: 0.5rem;
}

.result-info p {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.result-meta {
  font-weight: 500;
  color: #555;
}

.result-description {
  font-size: 0.9rem;
  color: #666;
  line-height: 1.5;
  margin-bottom: 0.75rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.play-icon {
  font-size: 0.9em;
  margin-right: 4px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
}

.header-row h2 {
  margin: 0;
}

.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
}
</style>
