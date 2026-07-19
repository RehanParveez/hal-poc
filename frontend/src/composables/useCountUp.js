import { ref, watch } from 'vue'

const prefersReducedMotion = typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches

export function useCountUp(sourceValue, duration = 600) {
  const displayValue = ref(Number(sourceValue.value) || 0)
  let rafId = null

  watch(sourceValue, (newVal, oldVal) => {
    const from = Number(oldVal) || 0
    const to = Number(newVal) || 0
    if (from === to) return
    if (prefersReducedMotion) { displayValue.value = to; return }

    const start = performance.now()
    cancelAnimationFrame(rafId)
    function tick(now) {
      const progress = Math.min((now - start) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      displayValue.value = from + (to - from) * eased
      if (progress < 1) rafId = requestAnimationFrame(tick)
      else displayValue.value = to
    }
    rafId = requestAnimationFrame(tick)
  })

  return displayValue
}