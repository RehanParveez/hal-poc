<template>
  <div class="space-y-0">
    <div v-for="(milestone, index) in milestones" :key="milestone.id" class="flex gap-4">
      <div class="flex flex-col items-center">
        <div :class="['w-9 h-9 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors',
          milestoneState(milestone) === 'completed' ? 'bg-green-700 border-green-700 text-white' :
          milestoneState(milestone) === 'active' ? 'bg-white border-gold-400 text-gold-600 animate-pulse-glow' :
          'bg-gray-100 border-gray-300 text-gray-400']">
          <CheckCircle2 v-if="milestoneState(milestone) === 'completed'" :size="18" />
          <Sprout v-else-if="milestoneState(milestone) === 'active'" :size="18" />
          <Lock v-else :size="14" />
        </div>
        <div v-if="index < milestones.length - 1" class="w-0.5 flex-1 mt-1"
          :class="milestoneState(milestone) === 'completed' ? 'bg-green-700 animate-grow-fill' : 'bg-gray-200'"
          style="min-height: 28px" />
      </div>
      <div class="pb-6 flex-1">
        <div class="flex items-center gap-2 flex-wrap">
          <p :class="['font-semibold text-sm', milestoneState(milestone) === 'active' ? 'text-green-800' : 'text-gray-800']">
            Phase {{ milestone.phase_number }}: {{ milestone.phase_name }}
          </p>
          <span v-if="milestoneState(milestone) === 'active'" class="text-xs bg-gold-400 text-slate-950 px-2 py-0.5 rounded-full font-semibold">GROWING</span>
          <span v-if="milestoneState(milestone) === 'locked'" class="text-xs text-gray-400">unlocks Day {{ milestone.day_offset }}</span>
        </div>
        <div v-if="milestoneState(milestone) === 'active'" class="mt-2 flex flex-wrap gap-1">
          <span v-for="cat in milestone.allowed_input_categories" :key="cat" class="text-xs bg-green-50 text-green-800 px-2 py-0.5 rounded-full capitalize">{{ cat }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useEscrowStore } from '@/stores/escrow.js'
import { CheckCircle2, Sprout, Lock } from 'lucide-vue-next'  

const escrow = useEscrowStore()
const milestones = computed(() => escrow.milestones)

function milestoneState(m) {
  if (m.is_active) return 'active'
  if (m.unlocked_at && !m.is_active) return 'completed'
  return 'locked'
}
</script>