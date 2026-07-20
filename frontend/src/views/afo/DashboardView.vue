<template>
  <DashboardHero eyebrow="Hal" :title="$t('afo.dashboardTitle')" />
 
  <div class="content-container -mt-8 relative z-20">
    <QuickActionsBar :actions="quickActions" />
  </div>
 
  <DashboardSection id="crop-types-section" tone="white" :eyebrow="$t('afo.configEyebrow')" :title="$t('afo.cropTypesTitle')">
    <div class="bg-white p-4 rounded shadow mb-4 space-y-2">
      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('afo.cropName') }}</label>
      <input v-model="cropForm.name" type="text" :placeholder="$t('afo.cropNamePlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />
      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('afo.cropCode') }}</label>
      <input v-model="cropForm.code" type="text" :placeholder="$t('afo.cropCodePlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />
      <select v-model="cropForm.season" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">{{ $t('afo.selectSeason') }}</option>
        <option value="rabi">{{ $t('afo.seasonRabi') }}</option>
        <option value="kharif">{{ $t('afo.seasonKharif') }}</option>
      </select>
      <button @click="submitCrop" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">{{ $t('afo.addCropType') }}</button>
    </div>
    <div class="space-y-1">
      <div v-for="c in crops.cropTypes" :key="c.id" class="bg-white p-2 rounded shadow text-sm flex justify-between">
        <span>{{ c.name }} ({{ c.code }})</span>
        <span class="text-gray-500 capitalize">{{ c.season }}</span>
      </div>
    </div>
  </DashboardSection>
 
  <DashboardSection id="input-caps-section" tone="tint" :eyebrow="$t('afo.financialsEyebrow')" :title="$t('afo.spendingCapsTitle')">
    <div class="bg-white p-4 rounded shadow mb-4 space-y-2">
      <select v-model="capForm.crop" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">{{ $t('afo.selectCrop') }}</option>
        <option v-for="c in crops.cropTypes" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
      </select>
      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('common.district') }}</label>
      <input v-model="capForm.district" type="text" :placeholder="$t('afo.districtPlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />
      <select v-model="capForm.input_category" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">{{ $t('afo.selectCategory') }}</option>
        <option value="seed">{{ $t('afo.categorySeed') }}</option>
        <option value="fertilizer">{{ $t('afo.categoryFertilizer') }}</option>
        <option value="pesticide">{{ $t('afo.categoryPesticide') }}</option>
        <option value="irrigation">{{ $t('afo.categoryIrrigation') }}</option>
        <option value="labour">{{ $t('afo.categoryLabour') }}</option>
      </select>
      <select v-model="capForm.valid_season" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">{{ $t('afo.selectSeason') }}</option>
        <option value="rabi">{{ $t('afo.seasonRabi') }}</option>
        <option value="kharif">{{ $t('afo.seasonKharif') }}</option>
      </select>
      <input v-model.number="capForm.max_cost_per_acre" type="number" :placeholder="$t('afo.maxCostPerAcrePlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />
      <button @click="submitCap" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">{{ $t('afo.saveCap') }}</button>
    </div>
    <div class="space-y-1">
      <div v-for="cap in crops.inputCaps" :key="cap.id" class="bg-white p-2 rounded shadow text-sm flex justify-between">
        <span>{{ cap.crop_code }} — {{ cap.district }} — {{ cap.input_category }}</span>
        <span class="text-gray-500">PKR {{ cap.max_cost_per_acre }}/acre</span>
      </div>
    </div>
  </DashboardSection>
 
  <DashboardSection id="crop-types-section" tone="white" :eyebrow="$t('afo.configEyebrow')" :title="$t('afo.cropTypesTitle')">
    <div class="bg-white p-4 rounded shadow mb-4 space-y-2">
      <select v-model="milestoneForm.crop" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">{{ $t('afo.selectCrop') }}</option>
        <option v-for="c in crops.cropTypes" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
      </select>
      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('afo.phaseNumber') }}</label>
      <input v-model.number="milestoneForm.phase_number" type="number" :placeholder="$t('afo.phaseNumberPlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />
      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('afo.phaseName') }}</label>
      <input v-model="milestoneForm.phase_name" type="text" :placeholder="$t('afo.phaseNamePlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />
      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('afo.dayOffset') }}</label>
      <input v-model.number="milestoneForm.day_offset" type="number" :placeholder="$t('afo.dayOffsetPlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />
      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('afo.unlockPercentage') }}</label>
      <input v-model.number="milestoneForm.unlock_pct" type="number" :about="$t('afo.unlockPercentagePlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />
      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('afo.allowedCategories') }}</label>
      <div class="flex gap-2 flex-wrap">
        <label
         v-for="cat in ['seed', 'fertilizer', 'pesticide', 'irrigation', 'labour']"
         :key="cat"
         class="text-sm px-3 py-1.5 border rounded-full cursor-pointer flex items-center gap-1.5"
         :class="milestoneForm.allowed_input_categories.includes(cat) ? 'bg-green-600 text-white border-green-600' : 'bg-white text-gray-700 border-gray-300'">
         <input type="checkbox" :value="cat" v-model="milestoneForm.allowed_input_categories" class="hidden" />
         {{ $t('afo.category' + cat.charAt(0).toUpperCase() + cat.slice(1)) }}
         </label>
      </div>
      <button @click="submitMilestone" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">{{ $t('afo.saveMilestone') }}</button>
    </div>
    <div class="space-y-1">
      <div v-for="m in crops.milestones" :key="m.id" class="bg-white p-2 rounded shadow text-sm flex justify-between">
        <span>{{ m.crop_code }} — {{ $t('afo.phaseLabel') }} {{ m.phase_number }}: {{ m.phase_name }}</span>
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
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const crops = useCropsStore()
const notify = useNotificationsStore()
 
const cropForm = reactive({ name: '', code: '', season: '' })
const capForm = reactive({ crop: '', district: '', input_category: '', valid_season: '', max_cost_per_acre: 0 })
const milestoneForm = reactive({ crop: '', phase_number: 1, phase_name: '', day_offset: 0, unlock_pct: 0, allowed_input_categories: [] })
 
const auth = useAuthStore()
const scrollToSection = useScrollTo()
 
const firstName = computed(() => auth.user?.full_name?.split(' ')[0] || t('afo.adminFallback'))

const greeting = computed(() => {
  const hour = new Date().getHours()
  return hour < 12 ? t('afo.goodMorning') : hour < 17 ? t('afo.goodAfternoon') : t('afo.goodEvening')
})
 
const heroStats = computed(() => [
  { icon: Sprout, label: t('afo.cropTypes'), value: crops.cropTypes.length },
  { icon: BarChart3, label: t('afo.spendingCaps'), value: crops.inputCaps.length },
  { icon: Clock3, label: t('afo.milestones'), value: crops.milestones.length }
])
 
const quickActions = computed(() => [
  { label: t('afo.qaManageCrops'), icon: Sprout, onClick: () => scrollToSection('crop-types-section') },
  { label: t('afo.qaSpendingCaps'), icon: BarChart3, onClick: () => scrollToSection('input-caps-section') },
  { label: t('afo.qaLifecycle'), icon: Clock3, onClick: () => scrollToSection('milestones-section') },
])
 
onMounted(async () => {
  await crops.fetchCropTypes()
  await crops.fetchInputCaps()
  await crops.fetchMilestones()
})
 
async function submitCrop() {
  if (!cropForm.name.trim() || !cropForm.code.trim() || !cropForm.season) {
    notify.showError({ message: t('afo.errorCropRequired') })
    return
  }
  try {
    await crops.createCropType({ ...cropForm })
    cropForm.name = ''
    cropForm.code = ''
    cropForm.season = ''
  } catch (error) {
    const fieldError = Object.values(error.response?.data || {})[0]?.[0]
    notify.showError({ message: fieldError || t('afo.errorAddCropType') })
  }
}
 
async function submitCap() {
  if (!capForm.crop || !capForm.district.trim() || !capForm.input_category || !capForm.valid_season) {
    notify.showError({ message: t('afo.errorCapFieldsRequired') })
    return
  }
  if (!capForm.max_cost_per_acre || capForm.max_cost_per_acre <= 0) {
    notify.showError({ message: t('afo.errorMaxCostZero') })
    return
  }
  try {
    await crops.setInputCap({ ...capForm })
    capForm.district = ''
    capForm.max_cost_per_acre = 0
  } catch (error) {
    const fieldError = Object.values(error.response?.data || {})[0]?.[0]
    notify.showError({ message: fieldError || t('afo.errorSaveCap') })
  }
}
 
async function submitMilestone() {
  if (!milestoneForm.crop || !milestoneForm.phase_name.trim()) {
    notify.showError({ message: t('afo.errorMilestoneRequired') })
    return
  }
  if (!milestoneForm.unlock_pct || milestoneForm.unlock_pct <= 0 || milestoneForm.unlock_pct > 100) {
    notify.showError({ message: t('afo.errorUnlockPercentage') })
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
    notify.showError({ message: fieldError || t('afo.errorSaveMilestone') })
  }
}
</script>