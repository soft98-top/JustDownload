<template>
  <div class="config-form">
    <div v-for="field in schema" :key="field.name" class="form-field">
      <label :for="field.name">
        {{ field.label }}
        <span v-if="field.required" class="required">*</span>
      </label>
      
      <div class="field-description" v-if="field.description">
        {{ field.description }}
      </div>
      
      <!-- 文本输入 - 如果是JSON数组/对象，使用textarea -->
      <textarea
        v-if="(field.type === 'text' || field.type === 'password') && isJsonField(field.name)"
        :id="field.name"
        v-model="formData[field.name]"
        :placeholder="getPlaceholder(field)"
        :required="field.required"
        rows="6"
        class="json-textarea"
      ></textarea>
      
      <!-- 普通文本输入 -->
      <input
        v-else-if="field.type === 'text' || field.type === 'password'"
        :id="field.name"
        :type="field.type"
        v-model="formData[field.name]"
        :placeholder="getPlaceholder(field)"
        :required="field.required"
      />
      
      <!-- 数字输入 -->
      <input
        v-else-if="field.type === 'number'"
        :id="field.name"
        type="number"
        v-model.number="formData[field.name]"
        :placeholder="getPlaceholder(field)"
        :required="field.required"
      />
      
      <!-- 布尔值（开关） -->
      <label v-else-if="field.type === 'boolean'" class="switch-label">
        <input
          :id="field.name"
          type="checkbox"
          v-model="formData[field.name]"
          class="switch-input"
        />
        <span class="switch-slider"></span>
        <span class="switch-text">{{ formData[field.name] ? '启用' : '禁用' }}</span>
      </label>
      
      <!-- 下拉选择 -->
      <select
        v-else-if="field.type === 'select'"
        :id="field.name"
        v-model="formData[field.name]"
        :required="field.required"
      >
        <option value="">请选择</option>
        <option v-for="opt in field.options" :key="opt" :value="opt">
          {{ opt }}
        </option>
      </select>
      
      <!-- 列表编辑器（用于资源站列表、解析器列表等） -->
      <div v-else-if="field.type === 'list'" class="list-editor">
        <div v-for="(item, index) in formData[field.name]" :key="index" class="list-item">
          <div class="list-item-header">
            <span class="list-item-number">#{{ index + 1 }}</span>
            <button @click="removeListItem(field.name, index)" class="btn-remove-small" type="button">
              ✕
            </button>
          </div>
          <div class="list-item-fields">
            <div v-for="subField in field.fields" :key="subField.name" class="list-subfield">
              <!-- 布尔类型子字段 -->
              <label v-if="subField.type === 'boolean'" class="subfield-checkbox">
                <input type="checkbox" v-model="item[subField.name]" />
                <span>{{ subField.label }}</span>
              </label>
              
              <!-- 文本类型子字段 -->
              <div v-else class="subfield-text">
                <label>{{ subField.label }}</label>
                <input
                  :type="subField.type === 'number' ? 'number' : 'text'"
                  v-model="item[subField.name]"
                  :placeholder="subField.label"
                  class="list-item-input"
                />
              </div>
            </div>
          </div>
        </div>
        <button @click="addListItem(field.name, field.fields)" class="btn-add" type="button">
          + 添加{{ field.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    schema: {
      type: Array,
      required: true
    },
    modelValue: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      formData: {}
    }
  },
  watch: {
    modelValue: {
      immediate: true,
      handler(newVal) {
        this.initFormData(newVal)
      }
    },
    formData: {
      deep: true,
      handler(newVal) {
        this.$emit('update:modelValue', newVal)
      }
    }
  },
  methods: {
    isJsonField(fieldName) {
      // 检查字段名是否包含_list后缀，或者字段值是否为数组/对象
      if (fieldName.endsWith('_list')) return true
      const value = this.formData[fieldName]
      return typeof value === 'object' && value !== null
    },
    initFormData(config) {
      // 如果schema未定义，直接返回
      if (!this.schema || !Array.isArray(this.schema)) {
        this.formData = {}
        return
      }
      
      const data = {}
      this.schema.forEach(field => {
        if (field.type === 'list') {
          // 列表类型，尝试解析JSON或使用空数组
          if (config[field.name]) {
            if (typeof config[field.name] === 'string') {
              try {
                data[field.name] = JSON.parse(config[field.name])
              } catch {
                data[field.name] = []
              }
            } else {
              data[field.name] = config[field.name]
            }
          } else {
            // 如果没有配置值，使用空数组
            data[field.name] = []
          }
        } else if (field.type === 'boolean') {
          // 布尔值：优先使用配置值，否则使用默认值
          if (config[field.name] !== undefined && config[field.name] !== null) {
            data[field.name] = config[field.name]
          } else {
            data[field.name] = field.default !== undefined ? field.default : false
          }
        } else if (field.type === 'text' && field.name.endsWith('_list')) {
          // 特殊处理：以_list结尾的text字段，转换为JSON字符串
          if (config[field.name]) {
            if (typeof config[field.name] === 'string') {
              // 已经是字符串，直接使用
              data[field.name] = config[field.name]
            } else {
              // 是对象或数组，转换为格式化的JSON字符串
              data[field.name] = JSON.stringify(config[field.name], null, 2)
            }
          } else if (field.default) {
            // 使用默认值
            data[field.name] = typeof field.default === 'string' 
              ? field.default 
              : JSON.stringify(field.default, null, 2)
          } else {
            data[field.name] = ''
          }
        } else {
          // 其他类型：只有配置中有值时才填充，否则留空显示placeholder
          if (config[field.name] !== undefined && config[field.name] !== null && config[field.name] !== '') {
            data[field.name] = config[field.name]
          } else {
            // 留空，让placeholder显示
            data[field.name] = ''
          }
        }
      })
      this.formData = data
    },
    getPlaceholder(field) {
      // 如果有描述，优先使用描述
      if (field.description) {
        return field.description
      }
      // 否则使用默认值作为placeholder
      if (field.default !== undefined && field.default !== null && field.default !== '') {
        return `默认: ${field.default}`
      }
      return ''
    },
    addListItem(fieldName, fields) {
      if (!this.formData[fieldName]) {
        this.formData[fieldName] = []
      }
      const newItem = {}
      fields.forEach(f => {
        newItem[f.name] = f.default || (f.name === 'enabled' ? true : '')
      })
      this.formData[fieldName].push(newItem)
    },
    removeListItem(fieldName, index) {
      this.formData[fieldName].splice(index, 1)
    }
  }
}
</script>

<style scoped>
.config-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field label {
  font-weight: 500;
  color: #333;
}

.required {
  color: #e74c3c;
}

.field-description {
  font-size: 0.85rem;
  color: #666;
  margin-top: -0.25rem;
}

input[type="text"],
input[type="password"],
input[type="number"],
select,
textarea {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.json-textarea {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  resize: vertical;
  min-height: 120px;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: #3498db;
}

/* 开关样式 */
.switch-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.switch-input {
  display: none;
}

.switch-slider {
  position: relative;
  width: 50px;
  height: 26px;
  background: #ccc;
  border-radius: 13px;
  transition: background 0.3s;
}

.switch-slider::before {
  content: '';
  position: absolute;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: white;
  top: 2px;
  left: 2px;
  transition: transform 0.3s;
}

.switch-input:checked + .switch-slider {
  background: #27ae60;
}

.switch-input:checked + .switch-slider::before {
  transform: translateX(24px);
}

.switch-text {
  font-size: 0.9rem;
  color: #666;
}

/* 列表编辑器 */
.list-editor {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.list-item {
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.list-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.list-item-number {
  font-weight: 600;
  color: #3498db;
  font-size: 0.9rem;
}

.btn-remove-small {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-remove-small:hover {
  background: #c0392b;
  transform: scale(1.1);
}

.list-item-fields {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.list-subfield {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.subfield-text label {
  font-size: 0.85rem;
  color: #666;
  font-weight: 500;
}

.list-item-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.list-item-input:focus {
  outline: none;
  border-color: #3498db;
}

.subfield-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.subfield-checkbox input {
  width: auto;
  cursor: pointer;
}

.subfield-checkbox:hover {
  background: #e9ecef;
}

.btn-add {
  padding: 0.75rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  align-self: flex-start;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-add:hover {
  background: #2980b9;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
