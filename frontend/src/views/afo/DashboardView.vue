<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-4">AFO — Crop Configuration</h1>

    <div id="crop-types-section" class="mb-8">
      <h2 class="text-xl font-bold mb-3">Crop Types</h2>
      <div class="bg-white p-4 rounded shadow mb-4 space-y-2">
        <input v-model="cropForm.name" type="text" placeholder="Crop Name" class="w-full border rounded px-2 py-1 text-sm" />
        <input v-model="cropForm.code" type="text" placeholder="Code (e.g. MAIZE)" class="w-full border rounded px-2 py-1 text-sm" />
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
    </div>

    <div id="input-caps-section" class="mb-8">
      <h2 class="text-xl font-bold mb-3">AFO Spending Caps</h2>
      <div class="bg-white p-4 rounded shadow mb-4 space-y-2">
        <select v-model="capForm.crop" class="w-full border rounded px-2 py-1 text-sm">
          <option value="">Select Crop</option>
          <option v-for="c in crops.cropTypes" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
        </select>
        <input v-model="capForm.district" type="text" placeholder="District" class="w-full border rounded px-2 py-1 text-sm" />
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
    </div>

    <div id="milestones-section">
      <h2 class="text-xl font-bold mb-3">Crop Lifecycle Milestones</h2>
      <div class="bg-white p-4 rounded shadow mb-4 space-y-2">
        <select v-model="milestoneForm.crop" class="w-full border rounded px-2 py-1 text-sm">
          <option value="">Select Crop</option>
          <option v-for="c in crops.cropTypes" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
        </select>
        <input v-model.number="milestoneForm.phase_number" type="number" placeholder="Phase Number" class="w-full border rounded px-2 py-1 text-sm" />
        <input v-model="milestoneForm.phase_name" type="text" placeholder="Phase Name" class="w-full border rounded px-2 py-1 text-sm" />
        <input v-model.number="milestoneForm.day_offset" type="number" placeholder="Day Offset" class="w-full border rounded px-2 py-1 text-sm" />
        <input v-model.number="milestoneForm.unlock_pct" type="number" placeholder="Unlock % (0-100)" class="w-full border rounded px-2 py-1 text-sm" />
        <div class="flex gap-2 flex-wrap">
          <label v-for="cat in ['seed', 'fertilizer', 'pesticide', 'irrigation', 'labour']" :key="cat" class="text-sm flex items-center gap-1">
            <input type="checkbox" :value="cat" v-model="milestoneForm.allowed_input_categories" />
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
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive } from 'vue'
import { useCropsStore } from '@/stores/crops.js'

const crops = useCropsStore()

const cropForm = reactive({ name: '', code: '', season: '' })
const capForm = reactive({ crop: '', district: '', input_category: '', valid_season: '', max_cost_per_acre: 0 })
const milestoneForm = reactive({ crop: '', phase_number: 1, phase_name: '', day_offset: 0, unlock_pct: 0, allowed_input_categories: [] })

onMounted(async () => {
  await crops.fetchCropTypes()
  await crops.fetchInputCaps()
  await crops.fetchMilestones()
})

async function submitCrop() {
  await crops.createCropType({ ...cropForm })
  cropForm.name = ''
  cropForm.code = ''
  cropForm.season = ''
}

async function submitCap() {
  await crops.setInputCap({ ...capForm })
}

async function submitMilestone() {
  await crops.setMilestone({ ...milestoneForm })
}
</script>