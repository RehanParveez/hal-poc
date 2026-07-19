
<template>
  <DashboardHero
    eyebrow="AFO Portal"
    :title="`${greeting}, ${firstName}`"
    subtitle="Configure crop types, input spending caps, and define growth lifecycle milestones."
    :stats="heroStats"
  />
 
  <div class="content-container -mt-8 relative z-20">
    <QuickActionsBar :actions="quickActions" />
  </div>
 
  <DashboardSection id="crop-types-section" tone="white" eyebrow="Configuration" title="Crop Types">
    <div class="bg-white p-4 rounded shadow mb-4 space-y-2">
      <label class="block text-xs font-medium text-gray-600 mb-1">Crop Name</label>
      <input v-model="cropForm.name" type="text" placeholder="e.g. Maize" class="w-full border rounded px-2 py-1 text-sm" />
      <label class="block text-xs font-medium text-gray-600 mb-1">Crop Code</label>
      <input v-model="cropForm.code" type="text" placeholder="e.g. MAIZE" class="w-full border rounded px-2 py-1 text-sm" />
      <select v-model="cropForm.season" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Season</option>
        <option value="rabi">Rabi</option>
        <option value="kharif">Kharif</option>
      </select>
      <button @click="submitCrop" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">Add Crop Type</button>
    </div>
    <div class="space-y-1">
      <div v-for="c in crops.cropTypes" :key="c.id" class="bg-white p-2 rounded shadow text-sm flex justify-between">
        <span>{{ c.name }} ({{ c.code }})</span>
        <span class="text-gray-500 capitalize">{{ c.season }}</span>
      </div>
    </div>
  </DashboardSection>
 
  <DashboardSection id="input-caps-section" tone="tint" eyebrow="Financials" title="AFO Spending Caps">
    <div class="bg-white p-4 rounded shadow mb-4 space-y-2">
      <select v-model="capForm.crop" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Crop</option>
        <option v-for="c in crops.cropTypes" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
      </select>
      <label class="block text-xs font-medium text-gray-600 mb-1">District</label>
      <input v-model="capForm.district" type="text" placeholder="e.g. Multan" class="w-full border rounded px-2 py-1 text-sm" />
      <select v-model="capForm.input_category" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Category</option>
        <option value="seed">Seed</option>
        <option value="fertilizer">Fertilizer</option>
        <option value="pesticide">Pesticide</option>
        <option value="irrigation">Irrigation</option>
        <option value="labour">Labour</option>
      </select>
      <select v-model="capForm.valid_season" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Season</option>
        <option value="rabi">Rabi</option>
        <option value="kharif">Kharif</option>
      </select>
      <input v-model.number="capForm.max_cost_per_acre" type="number" placeholder="Max Cost per Acre (PKR)" class="w-full border rounded px-2 py-1 text-sm" />
      <button @click="submitCap" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">Save Cap</button>
    </div>
    <div class="space-y-1">
      <div v-for="cap in crops.inputCaps" :key="cap.id" class="bg-white p-2 rounded shadow text-sm flex justify-between">
        <span>{{ cap.crop_code }} — {{ cap.district }} — {{ cap.input_category }}</span>
        <span class="text-gray-500">PKR {{ cap.max_cost_per_acre }}/acre</span>
      </div>
    </div>
  </DashboardSection>
 
  <DashboardSection id="milestones-section" tone="white" eyebrow="Growth" title="Crop Lifecycle Milestones">
    <div class="bg-white p-4 rounded shadow mb-4 space-y-2">
      <select v-model="milestoneForm.crop" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Crop</option>
        <option v-for="c in crops.cropTypes" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
      </select>
      <label class="block text-xs font-medium text-gray-600 mb-1">Phase Number</label>
      <input v-model.number="milestoneForm.phase_number" type="number" placeholder="e.g. 1" class="w-full border rounded px-2 py-1 text-sm" />
      <label class="block text-xs font-medium text-gray-600 mb-1">Phase Name</label>
      <input v-model="milestoneForm.phase_name" type="text" placeholder="e.g. Mid-Season Growth" class="w-full border rounded px-2 py-1 text-sm" />
      <label class="block text-xs font-medium text-gray-600 mb-1">Day Offset (days after sowing)</label>
      <input v-model.number="milestoneForm.day_offset" type="number" placeholder="e.g. 30" class="w-full border rounded px-2 py-1 text-sm" />
      <label class="block text-xs font-medium text-gray-600 mb-1">Unlock Percentage (0-100)</label>
      <input v-model.number="milestoneForm.unlock_pct" type="number" placeholder="e.g. 40" class="w-full border rounded px-2 py-1 text-sm" />
      <label class="block text-xs font-medium text-gray-600 mb-1">Allowed Categories This Phase</label>
      <div class="flex gap-2 flex-wrap">
        <label
          v-for="cat in ['seed', 'fertilizer', 'pesticide', 'irrigation', 'labour']"
          :key="cat"
          class="text-sm px-3 py-1.5 border rounded-full cursor-pointer flex items-center gap-1.5"
          :class="milestoneForm.allowed_input_categories.includes(cat) ? 'bg-green-600 text-white border-green-600' : 'bg-white text-gray-700 border-gray-300'"
        >
          <input type="checkbox" :value="cat" v-model="milestoneForm.allowed_input_categories" class="hidden" />
          {{ cat }}
        </label>
      </div>
      <button @click="submitMilestone" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">Save Milestone</button>
    </div>
    <div class="space-y-1">
      <div v-for="m in crops.milestones" :key="m.id" class="bg-white p-2 rounded shadow text-sm flex justify-between">
        <span>{{ m.crop_code }} — Phase {{ m.phase_number }}: {{ m.phase_name }}</span>
        <span class="text-gray-500">{{ m.unlock_pct }}%</span>
      </div>
    </div>
  </DashboardSection>
</template>
 
<script setup>
import { onMounted, reactive, computed } from 'vue'
import { useCropsStore } from '@/stores/crops.js'
import { useNotificationsStore } from '@/stores/notifications.js'
import { Sprout, BarChart3, Clock3 } from 'lucide-vue-next'
import DashboardHero from '@/components/layout/DashboardHero.vue'
import DashboardSection from '@/components/layout/DashboardSection.vue'
import QuickActionsBar from '@/components/shared/QuickActionsBar.vue'
import { useScrollTo } from '@/composables/useScrollTo.js'
import { useAuthStore } from '@/stores/auth.js'
 
const crops = useCropsStore()
const notify = useNotificationsStore()
 
const cropForm = reactive({ name: '', code: '', season: '' })
const capForm = reactive({ crop: '', district: '', input_category: '', valid_season: '', max_cost_per_acre: 0 })
const milestoneForm = reactive({ crop: '', phase_number: 1, phase_name: '', day_offset: 0, unlock_pct: 0, allowed_input_categories: [] })
 
const auth = useAuthStore()
const scrollToSection = useScrollTo()
 
const firstName = computed(() => auth.user?.full_name?.split(' ')[0] || 'Admin')
const greeting = computed(() => {
  const hour = new Date().getHours()
  return hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'
})
 
const heroStats = computed(() => [
  { icon: Sprout, label: 'Crop Types', value: crops.cropTypes.length },
  { icon: BarChart3, label: 'Spending Caps', value: crops.inputCaps.length },
  { icon: Clock3, label: 'Milestones', value: crops.milestones.length }
])
 
const quickActions = computed(() => [
  { label: 'Manage Crops', icon: Sprout, onClick: () => scrollToSection('crop-types-section') },
  { label: 'Spending Caps', icon: BarChart3, onClick: () => scrollToSection('input-caps-section') },
  { label: 'Lifecycle', icon: Clock3, onClick: () => scrollToSection('milestones-section') },
])
 
onMounted(async () => {
  await crops.fetchCropTypes()
  await crops.fetchInputCaps()
  await crops.fetchMilestones()
})
 
async function submitCrop() {
  if (!cropForm.name.trim() || !cropForm.code.trim() || !cropForm.season) {
    notify.showError({ message: 'Crop name, code, and season are all required.' })
    return
  }
  try {
    await crops.createCropType({ ...cropForm })
    cropForm.name = ''
    cropForm.code = ''
    cropForm.season = ''
  } catch (error) {
    const fieldError = Object.values(error.response?.data || {})[0]?.[0]
    notify.showError({ message: fieldError || 'Failed to add crop type.' })
  }
}
 
async function submitCap() {
  if (!capForm.crop || !capForm.district.trim() || !capForm.input_category || !capForm.valid_season) {
    notify.showError({ message: 'All cap fields are required.' })
    return
  }
  if (!capForm.max_cost_per_acre || capForm.max_cost_per_acre <= 0) {
    notify.showError({ message: 'Max cost per acre must be greater than zero.' })
    return
  }
  try {
    await crops.setInputCap({ ...capForm })
    capForm.district = ''
    capForm.max_cost_per_acre = 0
  } catch (error) {
    const fieldError = Object.values(error.response?.data || {})[0]?.[0]
    notify.showError({ message: fieldError || 'Failed to save cap.' })
  }
}
 
async function submitMilestone() {
  if (!milestoneForm.crop || !milestoneForm.phase_name.trim()) {
    notify.showError({ message: 'Crop and phase name are required.' })
    return
  }
  if (!milestoneForm.unlock_pct || milestoneForm.unlock_pct <= 0 || milestoneForm.unlock_pct > 100) {
    notify.showError({ message: 'Unlock percentage must be between 0 and 100.' })
    return
  }
  try {
    await crops.setMilestone({ ...milestoneForm })
    milestoneForm.phase_name = ''
    milestoneForm.day_offset = 0
    milestoneForm.unlock_pct = 0
    milestoneForm.allowed_input_categories = []
  } catch (error) {
    const fieldError = Object.values(error.response?.data || {})[0]?.[0]
    notify.showError({ message: fieldError || 'Failed to save milestone.' })
  }
}
</script>