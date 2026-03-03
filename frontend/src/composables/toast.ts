import { reactive } from 'vue'

type ToastState = {
  message: string
  visible: boolean
}

export const toastState = reactive<ToastState>({
  message: '',
  visible: false
})

let timer: number | undefined

export function showToast(message: string): void {
  toastState.message = message
  toastState.visible = true
  if (timer) {
    window.clearTimeout(timer)
  }
  timer = window.setTimeout(() => {
    toastState.visible = false
  }, 2600)
}
