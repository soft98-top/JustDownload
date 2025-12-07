<template>
  <div>
    <div class="card">
      <div class="header-actions">
        <h2>插件设置</h2>
        <div class="action-buttons">
          <button @click="showInstallDialog = true" class="btn btn-primary">
            📦 安装插件
          </button>
          <button @click="reloadPlugins" class="btn btn-secondary" :disabled="reloading">
            {{ reloading ? '🔄 重新加载中...' : '🔄 重新加载插件' }}
          </button>
          <button @click="exportConfig" class="btn btn-secondary">
            📤 导出配置
          </button>
          <button @click="showImportDialog = true" class="btn btn-secondary">
            📥 导入配置
          </button>
        </div>
      </div>
      
      <!-- Tab 导航 -->
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          :class="['tab', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
      
      <!-- Tab 内容 -->
      <div class="tab-content">
        <!-- 搜索插件 -->
        <div v-if="activeTab === 'search'" class="plugin-section">
          <div v-if="searchPlugins.length === 0" class="empty">
            <p>暂无搜索插件</p>
          </div>
          <div v-else class="plugin-list">
            <div v-for="plugin in searchPlugins" :key="plugin.name" class="plugin-item">
              <div class="plugin-header">
                <div class="plugin-info">
                  <h3>{{ plugin.name }}</h3>
                  <p class="plugin-description">{{ plugin.description }}</p>
                  <span class="plugin-version">v{{ plugin.version }}</span>
                </div>
                <div class="plugin-controls">
                  <label class="toggle-switch">
                    <input 
                      type="checkbox" 
                      :checked="plugin.enabled"
                      @change="togglePlugin('search', plugin.name, $event.target.checked)"
                    />
                    <span class="toggle-slider"></span>
                  </label>
                  <button 
                    @click="toggleConfig('search', plugin.name)"
                    class="btn btn-secondary"
                    :disabled="!plugin.enabled"
                  >
                    {{ expandedPlugin === `search:${plugin.name}` ? '收起配置' : '展开配置' }}
                  </button>
                  <button 
                    @click="deletePlugin('search', plugin.name)"
                    class="btn btn-danger"
                    title="删除插件"
                  >
                    🗑️
                  </button>
                </div>
              </div>
              
              <div v-if="expandedPlugin === `search:${plugin.name}` && plugin.enabled" class="plugin-config">
                <PluginConfig
                  :plugin-type="'search'"
                  :plugin-name="plugin.name"
                  :schema="plugin.config_schema"
                  @saved="onConfigSaved"
                  @cancel="expandedPlugin = null"
                />
              </div>
            </div>
          </div>
        </div>
        
        <!-- 下载插件 -->
        <div v-if="activeTab === 'download'" class="plugin-section">
          <div v-if="downloadPlugins.length === 0" class="empty">
            <p>暂无下载插件</p>
          </div>
          <div v-else class="plugin-list">
            <div v-for="plugin in downloadPlugins" :key="plugin.name" class="plugin-item">
              <div class="plugin-header">
                <div class="plugin-info">
                  <h3>{{ plugin.name }}</h3>
                  <p class="plugin-description">{{ plugin.description }}</p>
                  <div class="plugin-meta">
                    <span class="plugin-version">v{{ plugin.version }}</span>
                    <span class="plugin-protocols">
                      支持: {{ plugin.supported_protocols.join(', ') }}
                    </span>
                  </div>
                </div>
                <div class="plugin-controls">
                  <label class="toggle-switch">
                    <input 
                      type="checkbox" 
                      :checked="plugin.enabled"
                      @change="togglePlugin('download', plugin.name, $event.target.checked)"
                    />
                    <span class="toggle-slider"></span>
                  </label>
                  <button 
                    @click="toggleConfig('download', plugin.name)"
                    class="btn btn-secondary"
                    :disabled="!plugin.enabled"
                  >
                    {{ expandedPlugin === `download:${plugin.name}` ? '收起配置' : '展开配置' }}
                  </button>
                  <button 
                    @click="deletePlugin('download', plugin.name)"
                    class="btn btn-danger"
                    title="删除插件"
                  >
                    🗑️
                  </button>
                </div>
              </div>
              
              <div v-if="expandedPlugin === `download:${plugin.name}` && plugin.enabled" class="plugin-config">
                <PluginConfig
                  :plugin-type="'download'"
                  :plugin-name="plugin.name"
                  :schema="plugin.config_schema"
                  @saved="onConfigSaved"
                  @cancel="expandedPlugin = null"
                />
              </div>
            </div>
          </div>
        </div>
        
        <!-- 视频解析器 -->
        <div v-if="activeTab === 'parser'" class="plugin-section">
          <div v-if="parserPlugins.length === 0" class="empty">
            <p>暂无视频解析器插件</p>
          </div>
          <div v-else class="plugin-list">
            <div v-for="plugin in parserPlugins" :key="plugin.name" class="plugin-item">
              <div class="plugin-header">
                <div class="plugin-info">
                  <h3>{{ plugin.name }}</h3>
                  <p class="plugin-description">{{ plugin.description }}</p>
                  <span class="plugin-version">v{{ plugin.version }}</span>
                </div>
                <div class="plugin-controls">
                  <label class="toggle-switch">
                    <input 
                      type="checkbox" 
                      :checked="plugin.enabled"
                      @change="togglePlugin('parser', plugin.name, $event.target.checked)"
                    />
                    <span class="toggle-slider"></span>
                  </label>
                  <button 
                    @click="toggleConfig('parser', plugin.name)"
                    class="btn btn-secondary"
                    :disabled="!plugin.enabled"
                  >
                    {{ expandedPlugin === `parser:${plugin.name}` ? '收起配置' : '展开配置' }}
                  </button>
                  <button 
                    @click="deletePlugin('parser', plugin.name)"
                    class="btn btn-danger"
                    title="删除插件"
                  >
                    🗑️
                  </button>
                </div>
              </div>
              
              <div v-if="expandedPlugin === `parser:${plugin.name}` && plugin.enabled" class="plugin-config">
                <PluginConfig
                  :plugin-type="'parser'"
                  :plugin-name="plugin.name"
                  :schema="plugin.config_schema"
                  @saved="onConfigSaved"
                  @cancel="expandedPlugin = null"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 安装插件对话框 -->
    <div v-if="showInstallDialog" class="modal-overlay" @click="showInstallDialog = false">
      <div class="modal" @click.stop>
        <h3>安装插件</h3>
        <div class="form-group">
          <label>插件类型</label>
          <select v-model="installForm.type" class="form-control">
            <option value="search">搜索插件</option>
            <option value="download">下载插件</option>
            <option value="parser">解析器插件</option>
          </select>
        </div>
        <div class="form-group">
          <label>插件URL</label>
          <input 
            v-model="installForm.url" 
            type="text" 
            class="form-control"
            placeholder="https://example.com/plugin.py"
          />
        </div>
        <div class="modal-actions">
          <button @click="installPlugin" class="btn btn-primary" :disabled="installing">
            {{ installing ? '安装中...' : '安装' }}
          </button>
          <button @click="showInstallDialog = false" class="btn btn-secondary">
            取消
          </button>
        </div>
      </div>
    </div>
    
    <!-- 导入配置对话框 -->
    <div v-if="showImportDialog" class="modal-overlay" @click="showImportDialog = false">
      <div class="modal modal-large" @click.stop>
        <h3>导入配置</h3>
        <div class="form-group">
          <label>选择配置文件</label>
          <div class="file-input-group">
            <input 
              type="file" 
              ref="fileInput"
              accept=".json"
              @change="handleFileSelect"
              class="file-input"
              id="config-file-input"
            />
            <label for="config-file-input" class="btn btn-secondary file-label">
              📁 选择文件
            </label>
            <span v-if="selectedFileName" class="file-name">{{ selectedFileName }}</span>
          </div>
        </div>
        <div class="form-group">
          <label>配置JSON（可编辑）</label>
          <textarea 
            v-model="importConfigText" 
            class="form-control code-textarea"
            rows="15"
            placeholder="选择文件或直接粘贴配置JSON..."
          ></textarea>
          <div class="textarea-hint">
            提示：可以在加载文件后编辑配置内容
          </div>
        </div>
        <div class="modal-actions">
          <button @click="importConfig" class="btn btn-primary" :disabled="importing || !importConfigText">
            {{ importing ? '导入中...' : '导入' }}
          </button>
          <button @click="closeImportDialog" class="btn btn-secondary">
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import PluginConfig from '../components/PluginConfig.vue'
import toast from '../utils/toast'

export default {
  name: 'Settings',
  components: {
    PluginConfig
  },
  data() {
    return {
      activeTab: 'search',
      tabs: [
        { key: 'search', label: '搜索插件' },
        { key: 'download', label: '下载插件' },
        { key: 'parser', label: '视频解析器' }
      ],
      searchPlugins: [],
      downloadPlugins: [],
      parserPlugins: [],
      expandedPlugin: null,
      showInstallDialog: false,
      showImportDialog: false,
      installForm: {
        type: 'search',
        url: ''
      },
      installing: false,
      importing: false,
      importConfigText: '',
      reloading: false,
      selectedFileName: ''
    }
  },
  created() {
    this.$toast = toast
  },
  async mounted() {
    await this.loadPlugins()
  },
  methods: {
    async loadPlugins() {
      try {
        const response = await axios.get('/api/plugins')
        this.searchPlugins = response.data.search || []
        this.downloadPlugins = response.data.download || []
        this.parserPlugins = response.data.parser || []
      } catch (error) {
        console.error('加载插件失败:', error)
        this.$toast.error('加载插件失败', error.message)
      }
    },
    toggleConfig(pluginType, pluginName) {
      const key = `${pluginType}:${pluginName}`
      if (this.expandedPlugin === key) {
        this.expandedPlugin = null
      } else {
        this.expandedPlugin = key
      }
    },
    async togglePlugin(pluginType, pluginName, enabled) {
      try {
        await axios.post(`/api/plugins/${pluginType}/${pluginName}/toggle`, null, {
          params: { enabled }
        })
        
        // 更新本地状态
        const plugins = pluginType === 'search' ? this.searchPlugins : this.downloadPlugins
        const plugin = plugins.find(p => p.name === pluginName)
        if (plugin) {
          plugin.enabled = enabled
        }
        
        // 如果禁用了插件，收起配置
        if (!enabled && this.expandedPlugin === `${pluginType}:${pluginName}`) {
          this.expandedPlugin = null
        }
        
        this.$toast.success(enabled ? '插件已启用' : '插件已禁用')
      } catch (error) {
        console.error('切换插件状态失败:', error)
        this.$toast.error('操作失败', error.response?.data?.detail || error.message)
        
        // 恢复原状态
        await this.loadPlugins()
      }
    },
    onConfigSaved() {
      this.$toast.success('配置已保存')
      this.expandedPlugin = null
    },
    async installPlugin() {
      if (!this.installForm.url) {
        this.$toast.error('请输入插件URL')
        return
      }
      
      this.installing = true
      try {
        const response = await axios.post('/api/plugins/install', {
          url: this.installForm.url,
          plugin_type: this.installForm.type
        })
        
        this.$toast.success(response.data.message)
        this.showInstallDialog = false
        this.installForm.url = ''
        
        // 如果热加载成功，刷新插件列表
        if (response.data.hot_loaded) {
          setTimeout(() => {
            this.loadPlugins()
          }, 500)
        } else {
          // 提示重启
          setTimeout(() => {
            this.$toast.info('请重启后端服务以加载新插件')
          }, 1000)
        }
      } catch (error) {
        console.error('安装插件失败:', error)
        this.$toast.error('安装失败', error.response?.data?.detail || error.message)
      } finally {
        this.installing = false
      }
    },
    async deletePlugin(pluginType, pluginName) {
      if (!confirm(`确定要删除插件 ${pluginName} 吗？`)) {
        return
      }
      
      try {
        const response = await axios.post('/api/plugins/delete', {
          plugin_type: pluginType,
          plugin_name: pluginName
        })
        
        this.$toast.success(response.data.message)
        
        // 如果热卸载成功，立即从列表中移除
        if (response.data.hot_unloaded) {
          if (pluginType === 'search') {
            this.searchPlugins = this.searchPlugins.filter(p => p.name !== pluginName)
          } else if (pluginType === 'download') {
            this.downloadPlugins = this.downloadPlugins.filter(p => p.name !== pluginName)
          } else if (pluginType === 'parser') {
            this.parserPlugins = this.parserPlugins.filter(p => p.name !== pluginName)
          }
        } else {
          // 提示重启
          setTimeout(() => {
            this.$toast.info('请重启后端服务以生效')
          }, 1000)
        }
      } catch (error) {
        console.error('删除插件失败:', error)
        this.$toast.error('删除失败', error.response?.data?.detail || error.message)
      }
    },
    async reloadPlugins() {
      this.reloading = true
      try {
        const response = await axios.post('/api/plugins/reload')
        
        this.$toast.success(response.data.message)
        
        // 重新加载插件列表
        await this.loadPlugins()
      } catch (error) {
        console.error('重新加载插件失败:', error)
        this.$toast.error('重新加载失败', error.response?.data?.detail || error.message)
      } finally {
        this.reloading = false
      }
    },
    async exportConfig() {
      try {
        const response = await axios.get('/api/config/export')
        
        // 下载为JSON文件
        const blob = new Blob([JSON.stringify(response.data.config, null, 2)], {
          type: 'application/json'
        })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `config_${new Date().toISOString().split('T')[0]}.json`
        a.click()
        URL.revokeObjectURL(url)
        
        this.$toast.success('配置已导出')
      } catch (error) {
        console.error('导出配置失败:', error)
        this.$toast.error('导出失败', error.response?.data?.detail || error.message)
      }
    },
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (!file) {
        return
      }
      
      this.selectedFileName = file.name
      
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const content = e.target.result
          // 验证JSON格式
          JSON.parse(content)
          // 格式化显示
          this.importConfigText = JSON.stringify(JSON.parse(content), null, 2)
          this.$toast.success('文件加载成功')
        } catch (error) {
          this.$toast.error('文件格式错误', '请选择有效的JSON文件')
          this.importConfigText = ''
          this.selectedFileName = ''
        }
      }
      reader.onerror = () => {
        this.$toast.error('文件读取失败')
        this.selectedFileName = ''
      }
      reader.readAsText(file)
    },
    closeImportDialog() {
      this.showImportDialog = false
      this.importConfigText = ''
      this.selectedFileName = ''
      // 清空文件选择
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
    },
    async importConfig() {
      if (!this.importConfigText) {
        this.$toast.error('请输入配置JSON或选择文件')
        return
      }
      
      this.importing = true
      try {
        const config = JSON.parse(this.importConfigText)
        
        const response = await axios.post('/api/config/import', { config })
        
        this.$toast.success(response.data.message)
        this.closeImportDialog()
        
        // 重新加载插件
        setTimeout(() => {
          window.location.reload()
        }, 1500)
      } catch (error) {
        console.error('导入配置失败:', error)
        if (error instanceof SyntaxError) {
          this.$toast.error('JSON格式错误', '请检查配置内容')
        } else {
          this.$toast.error('导入失败', error.response?.data?.detail || error.message)
        }
      } finally {
        this.importing = false
      }
    }
  }
}
</script>

<style scoped>
.card h2 {
  margin-bottom: 1.5rem;
}

/* Tab 样式 */
.tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 1.5rem;
}

.tab {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 1rem;
  color: #666;
  transition: all 0.2s;
  position: relative;
  bottom: -2px;
}

.tab:hover {
  color: #3498db;
  background: #f8f9fa;
}

.tab.active {
  color: #3498db;
  border-bottom-color: #3498db;
  font-weight: 600;
}

.tab-content {
  min-height: 400px;
}

/* 插件列表 */
.plugin-section {
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.plugin-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.plugin-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid #e0e0e0;
  transition: all 0.2s;
}

.plugin-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.plugin-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.plugin-info {
  flex: 1;
}

.plugin-info h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.plugin-description {
  margin: 0 0 0.5rem 0;
  color: #666;
  font-size: 0.95rem;
}

.plugin-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.plugin-version {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background: #3498db;
  color: white;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.plugin-protocols {
  color: #999;
  font-size: 0.85rem;
}

.plugin-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* 开关样式 */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 26px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.3s;
  border-radius: 26px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

.toggle-switch input:checked + .toggle-slider {
  background-color: #27ae60;
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(24px);
}

.toggle-switch input:disabled + .toggle-slider {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 配置区域 */
.plugin-config {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #ddd;
  animation: slideDown 0.3s;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 1000px;
  }
}

.empty {
  text-align: center;
  padding: 3rem;
  color: #999;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 头部操作按钮 */
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header-actions h2 {
  margin: 0;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-danger {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-danger:hover {
  background: #c0392b;
}

/* 模态框 */
.modal-overlay {
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

.modal {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #2c3e50;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
}

textarea.form-control {
  font-family: monospace;
  resize: vertical;
}

.modal-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

/* 大号对话框 */
.modal-large {
  max-width: 700px;
}

/* 文件选择 */
.file-input-group {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.file-input {
  display: none;
}

.file-label {
  margin: 0;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

.file-name {
  color: #27ae60;
  font-size: 0.9rem;
  font-weight: 500;
}

/* 代码文本框 */
.code-textarea {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  resize: vertical;
}

.textarea-hint {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #999;
  font-style: italic;
}
</style>
