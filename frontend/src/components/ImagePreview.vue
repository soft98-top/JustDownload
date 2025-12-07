<template>
  <div v-if="show" class="image-preview-overlay" @click="close">
    <div class="image-preview-container" @click.stop>
      <button class="close-btn" @click="close" title="关闭 (ESC)">✕</button>
      <img :src="imageUrl" :alt="imageAlt" @click.stop />
      <div v-if="imageAlt" class="image-caption">{{ imageAlt }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImagePreview',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    imageUrl: {
      type: String,
      default: ''
    },
    imageAlt: {
      type: String,
      default: ''
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        // 显示时禁止页面滚动
        document.body.style.overflow = 'hidden'
        // 添加键盘事件监听
        document.addEventListener('keydown', this.handleKeydown)
      } else {
        // 隐藏时恢复页面滚动
        document.body.style.overflow = ''
        // 移除键盘事件监听
        document.removeEventListener('keydown', this.handleKeydown)
      }
    }
  },
  beforeUnmount() {
    // 组件销毁时清理
    document.body.style.overflow = ''
    document.removeEventListener('keydown', this.handleKeydown)
  },
  methods: {
    close() {
      this.$emit('close')
    },
    handleKeydown(e) {
      if (e.key === 'Escape') {
        this.close()
      }
    }
  }
}
</script>

<style scoped>
.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  cursor: pointer;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.image-preview-container {
  position: relative;
  width: 95vw;
  height: 95vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: default;
  animation: zoomIn 0.3s ease;
}

@keyframes zoomIn {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.image-preview-container img {
  max-width: 95vw;
  max-height: calc(95vh - 80px); /* 减去标题和关闭按钮的空间 */
  min-width: 60vw; /* 最小宽度，让小图片也能放大 */
  min-height: 60vh; /* 最小高度 */
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  cursor: zoom-out;
}

.close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 24px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.image-caption {
  margin-top: 1rem;
  color: white;
  font-size: 0.9rem;
  text-align: center;
  max-width: 600px;
  padding: 0.5rem 1rem;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  backdrop-filter: blur(10px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .image-preview-container {
    width: 98vw;
    height: 98vh;
  }
  
  .image-preview-container img {
    max-width: 98vw;
    max-height: calc(98vh - 60px);
    min-width: 80vw; /* 移动端更大的最小宽度 */
    min-height: 50vh;
  }
  
  .close-btn {
    top: 10px;
    right: 10px;
  }
  
  .image-caption {
    font-size: 0.8rem;
    padding: 0.4rem 0.8rem;
  }
}
</style>
