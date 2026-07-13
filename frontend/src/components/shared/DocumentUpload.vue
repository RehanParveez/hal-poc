<template>
  <div>
    <label class="block text-xs font-medium text-gray-600 mb-1">{{ label }}</label>
    <div
      class="border-2 border-dashed rounded-lg p-4 text-center cursor-pointer hover:border-green-500"
      @dragover.prevent
      @drop.prevent="onDrop"
      @click="$refs.fileInput.click()"
    >
      <template v-if="!file">
        <p class="text-sm text-gray-500">📄 Click or drag a file here</p>
        <p class="text-xs text-gray-400 mt-1">Max {{ maxSizeMB }}MB</p>
      </template>
      <template v-else>
        <p class="text-sm text-gray-800">{{ file.name }} ({{ (file.size / 1024 / 1024).toFixed(2) }}MB)</p>
        <button type="button" @click.stop="removeFile" class="text-xs text-red-600 mt-1">Remove</button>
      </template>
    </div>
    <input ref="fileInput" type="file" :accept="accept" class="hidden" @change="onSelect" />
    <p v-if="errorMsg" class="text-red-600 text-xs mt-1">{{ errorMsg }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  label: { type: String, default: 'Upload Document' },
  accept: { type: String, default: 'application/pdf,image/*' },
  maxSizeMB: { type: Number, default: 5 },
  modelValue: { type: [File, null], default: null },
})
const emit = defineEmits(['update:modelValue', 'validation-error'])

const file = ref(props.modelValue)
const errorMsg = ref('')

function validate(f) {
  errorMsg.value = ''
  if (f.size > props.maxSizeMB * 1024 * 1024) {
    errorMsg.value = `File must be under ${props.maxSizeMB}MB`
    emit('validation-error', errorMsg.value)
    return false
  }
  return true
}
function setFile(f) {
  if (!f || !validate(f)) return
  file.value = f
  emit('update:modelValue', f)
}
function onSelect(e) { setFile(e.target.files[0]) }
function onDrop(e) { setFile(e.dataTransfer.files[0]) }
function removeFile() {
  file.value = null
  errorMsg.value = ''
  emit('update:modelValue', null)
}
</script>