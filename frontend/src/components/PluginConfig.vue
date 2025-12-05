<template>
  <div class="plugin-config-wrapper">
    <PluginConfigForm
      v-model="configData"
      :schema="schema"
    />
    
    <div class="config-actions">
      <button @click="saveConfig" class="btn btn-primary" :disabled="saving">
        {{ saving ? '保存中...' : '保存配置' }}
      </button>
      <button @click="cancel" class="btn">取消</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import PluginConfigForm from './PluginConfigForm.vue'
import toast from '../utils/toast'

export default {
  components: {
    PluginConfigForm
  },
  props: {
    pluginType: {
      type: String,
      required: true
    },
    pluginName: {
      type: String,
      required: true
    },
    schema: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      configData: {},
      saving: false
    }
  },
  created() {
    this.$toast = toast
  },
  async mounted() {
    await this.loadConfig()
  },
  methods: {
    async loadConfig() {
      try {
        const response = await axios.get(`/api/plugins/${this.pluginType}/${this.pluginName}/config`)
        this.configData = response.data.config || {}
      } catch (error) {
        console.error('加载配置失败:', error)
        this.$toast.error('加载配置失败', error.message)
      }
    },
    async saveConfig() {
      this.saving = true
      try {
        // 处理配置数据：将JSON字符串字段解析为对象
        const processedConfig = { ...this.configData }
        
        // 遍历schema，找到以_list结尾的text字段
        this.schema.forEach(field => {
          if (field.type === 'text' && field.name.endsWith('_list')) {
            const value = processedConfig[field.name]
            if (typeof value === 'string' && value.trim()) {
              try {
                // 尝试解析JSON字符串
                processedConfig[field.name] = JSON.parse(value)
              } catch (e) {
                // 如果解析失败，保持原值
                console.warn(`无法解析字段 ${field.name} 的JSON:`, e)
              }
            }
          }
        })
        
        await axios.post(`/api/plugins/${this.pluginType}/${this.pluginName}/config`, processedConfig)
        this.$toast.success('配置已保存')
        this.$emit('saved')
      } catch (error) {
        console.error('保存配置失败:', error)
        this.$toast.error('保存配置失败', error.response?.data?.detail || error.message)
      } finally {
        this.saving = false
      }
    },
    cancel() {
      this.$emit('cancel')
    }
  }
}
</script>

<style scoped>
.plugin-config-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.config-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 0.5rem 1.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn:hover {
  background: #f0f0f0;
}

.btn-primary {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
