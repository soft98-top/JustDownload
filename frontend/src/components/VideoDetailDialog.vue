<template>
  <div v-if="show" class="dialog-overlay" @click.self="close">
    <div class="dialog-content">
      <div class="dialog-header">
        <h2>{{ video.title }}</h2>
        <button class="close-btn" @click="close">×</button>
      </div>
      
      <div class="dialog-body">
        <!-- 视频信息 -->
        <div class="video-info">
          <img v-if="video.thumbnail" :src="video.thumbnail" alt="封面" class="thumbnail" />
          <div class="info-text">
            <p class="platform">来源: {{ video.platform }}</p>
            <p v-if="video.metadata?.note" class="note">{{ video.metadata.note }}</p>
            <p class="description">{{ video.metadata?.full_description || video.description }}</p>
          </div>
        </div>
        
        <!-- 剧集列表 -->
        <div class="episodes-section">
          <h3>剧集列表 (共{{ episodes.length }}集)</h3>
          <div class="episodes-list">
            <div v-for="(episode, index) in episodes" :key="index" class="episode-item">
              <div class="episode-header">
                <span class="episode-name">{{ episode.episode_name }}</span>
                <span v-if="episode.flag" class="episode-flag">{{ episode.flag }}</span>
              </div>
              
              <div class="episode-links">
                <!-- 原始链接 -->
                <div class="link-item">
                  <span class="link-label">原始地址:</span>
                  <a :href="episode.play_url" target="_blank" class="link-url">
                    {{ truncateUrl(episode.play_url) }}
                  </a>
                  <button @click="copyUrl(episode.play_url)" class="copy-btn">复制</button>
                </div>
                
                <!-- 解析后的链接 -->
                <div v-if="episode.parsed_urls && episode.parsed_urls.length > 0" class="parsed-links">
                  <div v-for="(parsed, pIndex) in episode.parsed_urls" :key="pIndex" class="link-item">
                    <span class="link-label">{{ parsed.name }}:</span>
                    <a :href="parsed.url" target="_blank" class="link-url">
                      {{ truncateUrl(parsed.url) }}
                    </a>
                    <button @click="copyUrl(parsed.url)" class="copy-btn">复制</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import toast from '../utils/toast'

export default {
  name: 'VideoDetailDialog',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    video: {
      type: Object,
      required: true
    }
  },
  computed: {
    episodes() {
      return this.video.metadata?.episodes || []
    }
  },
  methods: {
    close() {
      this.$emit('close')
    },
    truncateUrl(url) {
      if (url.length > 60) {
        return url.substring(0, 60) + '...'
      }
      return url
    },
    async copyUrl(url) {
      try {
        await navigator.clipboard.writeText(url)
        toast.success('链接已复制')
      } catch (err) {
        toast.error('复制失败')
      }
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
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.dialog-content {
  background: white;
  border-radius: 12px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.dialog-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 32px;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

.dialog-body {
  padding: 24px;
  overflow-y: auto;
}

.video-info {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.thumbnail {
  width: 200px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}

.info-text {
  flex: 1;
}

.platform {
  color: #6b7280;
  font-size: 14px;
  margin: 0 0 8px 0;
}

.note {
  color: #3b82f6;
  font-size: 14px;
  margin: 0 0 12px 0;
  font-weight: 500;
}

.description {
  color: #374151;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

.episodes-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 16px 0;
}

.episodes-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.episode-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  background: #f9fafb;
}

.episode-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.episode-name {
  font-weight: 600;
  color: #111827;
  font-size: 15px;
}

.episode-flag {
  font-size: 12px;
  color: #6b7280;
  background: #e5e7eb;
  padding: 2px 8px;
  border-radius: 4px;
}

.episode-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.link-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.link-label {
  color: #6b7280;
  font-weight: 500;
  min-width: 80px;
}

.link-url {
  flex: 1;
  color: #3b82f6;
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.link-url:hover {
  text-decoration: underline;
}

.copy-btn {
  padding: 4px 12px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.2s;
}

.copy-btn:hover {
  background: #2563eb;
}

.parsed-links {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-left: 20px;
  padding-left: 12px;
  border-left: 2px solid #e5e7eb;
}
</style>
