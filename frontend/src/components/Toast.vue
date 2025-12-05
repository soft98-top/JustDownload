<template>
  <transition name="toast-fade">
    <div v-if="visible" :class="['toast', `toast-${type}`]">
      <div class="toast-icon">
        <span v-if="type === 'success'">✓</span>
        <span v-else-if="type === 'error'">✗</span>
        <span v-else-if="type === 'warning'">⚠</span>
        <span v-else>ℹ</span>
      </div>
      <div class="toast-content">
        <div class="toast-title">{{ title }}</div>
        <div v-if="message" class="toast-message">{{ message }}</div>
      </div>
      <button v-if="closable" @click="close" class="toast-close">&times;</button>
    </div>
  </transition>
</template>

<script>
export default {
  props: {
    type: {
      type: String,
      default: 'info',
      validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
    },
    title: {
      type: String,
      required: true
    },
    message: {
      type: String,
      default: ''
    },
    duration: {
      type: Number,
      default: 3000
    },
    closable: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      visible: false,
      timer: null
    }
  },
  mounted() {
    this.show()
  },
  methods: {
    show() {
      this.visible = true
      if (this.duration > 0) {
        this.timer = setTimeout(() => {
          this.close()
        }, this.duration)
      }
    },
    close() {
      this.visible = false
      if (this.timer) {
        clearTimeout(this.timer)
      }
      setTimeout(() => {
        this.$emit('close')
      }, 300)
    }
  }
}
</script>

<style scoped>
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  min-width: 300px;
  max-width: 500px;
  padding: 1rem 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  z-index: 9999;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: all 0.3s ease;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.toast-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
  flex-shrink: 0;
}

.toast-success .toast-icon {
  background: #27ae60;
  color: white;
}

.toast-error .toast-icon {
  background: #e74c3c;
  color: white;
}

.toast-warning .toast-icon {
  background: #f39c12;
  color: white;
}

.toast-info .toast-icon {
  background: #3498db;
  color: white;
}

.toast-content {
  flex: 1;
}

.toast-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #2c3e50;
}

.toast-message {
  font-size: 0.9rem;
  color: #666;
  line-height: 1.4;
}

.toast-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  line-height: 1;
  flex-shrink: 0;
}

.toast-close:hover {
  color: #333;
}

.toast-success {
  border-left: 4px solid #27ae60;
}

.toast-error {
  border-left: 4px solid #e74c3c;
}

.toast-warning {
  border-left: 4px solid #f39c12;
}

.toast-info {
  border-left: 4px solid #3498db;
}
</style>
