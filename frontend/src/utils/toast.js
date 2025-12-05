import { createApp } from 'vue'
import Toast from '../components/Toast.vue'

let toastContainer = null

function getToastContainer() {
  if (!toastContainer) {
    toastContainer = document.createElement('div')
    toastContainer.id = 'toast-container'
    toastContainer.style.cssText = 'position: fixed; top: 0; right: 0; z-index: 9999; pointer-events: none;'
    document.body.appendChild(toastContainer)
  }
  return toastContainer
}

function showToast(options) {
  const container = getToastContainer()
  const toastWrapper = document.createElement('div')
  toastWrapper.style.pointerEvents = 'auto'
  container.appendChild(toastWrapper)

  const app = createApp(Toast, {
    ...options,
    onClose: () => {
      app.unmount()
      container.removeChild(toastWrapper)
    }
  })

  app.mount(toastWrapper)
}

export default {
  success(title, message = '', duration = 3000) {
    showToast({ type: 'success', title, message, duration })
  },
  error(title, message = '', duration = 5000) {
    showToast({ type: 'error', title, message, duration })
  },
  warning(title, message = '', duration = 4000) {
    showToast({ type: 'warning', title, message, duration })
  },
  info(title, message = '', duration = 3000) {
    showToast({ type: 'info', title, message, duration })
  }
}
