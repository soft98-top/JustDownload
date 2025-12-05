<template>
  <div v-if="show" class="dialog-overlay" @click="close">
    <div class="dialog" @click.stop>
      <div class="dialog-header">
        <h3>下载选项</h3>
        <button @click="close" class="close-btn">&times;</button>
      </div>
      
      <div class="dialog-body">
        <div class="info-section" v-if="result">
          <h4>{{ result.title }}</h4>
          <p class="meta">
            <span v-if="result.metadata?.note">{{ result.metadata.note }}</span>
            <span v-if="result.metadata?.episode_count"> · {{ result.metadata.episode_count }}集</span>
          </p>
        </div>

        <!-- 剧集选择 (如果有多集) -->
        <div v-if="result.metadata?.episodes?.length > 1" class="section">
          <label>选择剧集:</label>
          <select v-model="selectedEpisode" class="full-width">
            <option value="">全部下载</option>
            <option v-for="(ep, idx) in result.metadata.episodes" :key="idx" :value="idx">
              {{ ep.episode_name || ep.name }} <span v-if="ep.flag">({{ ep.flag }})</span>
            </option>
          </select>
        </div>

        <!-- M3U8解析器选择 (如果有解析器) -->
        <div v-if="hasM3u8Parsers" class="section">
          <label>M3U8解析器:</label>
          <select v-model="selectedParser" class="full-width">
            <option value="">使用原始地址</option>
            <option v-for="(parser, idx) in currentParsers" :key="idx" :value="idx">
              {{ parser.name }}
            </option>
          </select>
        </div>

        <!-- 下载插件选择 -->
        <div class="section">
          <label>下载插件:</label>
          <select v-model="selectedDownloader" class="full-width">
            <option v-for="plugin in enabledDownloadPlugins" :key="plugin.name" :value="plugin.name">
              {{ plugin.description }} ({{ plugin.supported_protocols.join(', ') }})
            </option>
          </select>
        </div>

        <!-- 下载地址（可编辑） -->
        <div class="section">
          <label>下载地址:</label>
          <textarea 
            v-model="editableUrl" 
            class="url-input"
            rows="3"
            placeholder="输入或修改下载地址"
          ></textarea>
        </div>
      </div>

      <div class="dialog-footer">
        <button @click="close" class="btn">取消</button>
        <button @click="confirmDownload" class="btn btn-success">确认下载</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    show: Boolean,
    result: Object,
    downloadPlugins: Array
  },
  data() {
    return {
      selectedEpisode: '',
      selectedParser: '',
      selectedDownloader: '',
      editableUrl: ''
    }
  },
  computed: {
    // 只显示启用的下载插件
    enabledDownloadPlugins() {
      return (this.downloadPlugins || []).filter(plugin => plugin.enabled !== false)
    },
    currentEpisode() {
      if (!this.result) return null
      if (this.selectedEpisode === '' || !this.result.metadata?.episodes) {
        return this.result.metadata?.episodes?.[0] || null
      }
      return this.result.metadata.episodes[this.selectedEpisode]
    },
    currentParsers() {
      return this.currentEpisode?.parsed_urls || []
    },
    hasM3u8Parsers() {
      return this.currentParsers.length > 0
    },
    autoSelectedUrl() {
      if (!this.result) return ''
      
      if (!this.currentEpisode) {
        return this.result.url || ''
      }
      
      if (this.selectedParser !== '' && this.currentParsers[this.selectedParser]) {
        return this.currentParsers[this.selectedParser].url
      }
      
      // 兼容新旧字段名
      return this.currentEpisode.play_url || this.currentEpisode.url || ''
    }
  },
  methods: {
    close() {
      this.$emit('close')
    },
    confirmDownload() {
      if (!this.result) return
      
      // 构建下载标题，如果是剧集则添加剧集名称
      let downloadTitle = this.result.title
      const episodeName = this.currentEpisode?.episode_name || this.currentEpisode?.name
      
      // 如果有剧集信息且有多集，添加剧集名称到标题
      const hasMultipleEpisodes = this.result.metadata?.episodes?.length > 1
      if (episodeName && (hasMultipleEpisodes || this.selectedEpisode !== '')) {
        downloadTitle = `${this.result.title} - ${episodeName}`
      }
      
      const downloadData = {
        url: this.editableUrl,  // 使用可编辑的URL
        title: downloadTitle,
        plugin_name: this.selectedDownloader || undefined,
        metadata: {
          episode: episodeName,
          parser: this.selectedParser !== '' ? this.currentParsers[this.selectedParser]?.name : null
        }
      }
      this.$emit('download', downloadData)
      this.close()
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        // 重置选择
        this.selectedEpisode = ''
        this.selectedParser = ''
        // 默认选择第一个启用的下载插件
        this.selectedDownloader = this.enabledDownloadPlugins.length > 0 
          ? this.enabledDownloadPlugins[0].name 
          : ''
        // 初始化可编辑URL
        this.editableUrl = this.autoSelectedUrl
      }
    },
    autoSelectedUrl(newVal) {
      // 当自动选择的URL变化时，更新可编辑URL
      this.editableUrl = newVal
    }
  }
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.dialog-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #999;
  line-height: 1;
  padding: 0;
  width: 30px;
  height: 30px;
}

.close-btn:hover {
  color: #333;
}

.dialog-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.info-section h4 {
  margin: 0 0 0.5rem 0;
}

.meta {
  color: #666;
  margin: 0 0 1rem 0;
}

.section {
  margin-bottom: 1.5rem;
}

.section label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.full-width {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.url-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.85rem;
  font-family: monospace;
  resize: vertical;
  min-height: 60px;
}

.url-input:focus {
  outline: none;
  border-color: #3498db;
}

.dialog-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
</style>
