<template>
  <div>
    <div class="card">
      <h2>插件设置</h2>
      
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
      expandedPlugin: null
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
</style>
