<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
      <div class="text-center mb-2">
        <h1 class="text-2xl font-bold text-gray-900">Create Account</h1>
        <p class="text-sm text-gray-500 mt-1">Join the HAL AgroChain Platform</p>
      </div>

      <StepWizard
        v-if="wizardSteps && currentStep > 0"
        :steps="wizardSteps"
        :current-step="currentStep"
        :completed-steps="completedSteps"
        class="mb-4"
      />

      <p v-if="errorMessage" class="text-red-600 text-sm font-medium bg-red-50 p-2 rounded border border-red-200 mb-4">
        {{ errorMessage }}
      </p>
      <Transition name="step-fade" mode="out-in">
        <form v-if="currentStep === 0" :key="0" @submit.prevent="handleStep0Continue" class="space-y-4">

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
        <input v-model="form.full_name" type="text" placeholder="e.g., Muhammad Ali" required class="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-green-600 focus:outline-none" />
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
          <input v-model="form.phone" type="text" placeholder="03001234567" required class="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-green-600 focus:outline-none" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">CNIC Number</label>
          <input v-model="form.cnic" type="text" placeholder="35202-1234567-1" required class="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-green-600 focus:outline-none" />
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
        <input v-model="form.password" type="password" placeholder="••••••••" required class="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-green-600 focus:outline-none" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Platform Role</label>
        <select v-model="form.role" required class="w-full border border-gray-300 rounded px-3 py-2 bg-white focus:ring-2 focus:ring-green-600 focus:outline-none">
          <option value="">Select System Access Level</option>
          <option value="smallholder">Smallholder Farmer</option>
          <option value="tenant">Tenant Farmer</option>
          <option value="landowner">Landowner</option>
          <option value="shopkeeper">Shopkeeper</option>
        </select>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">District</label>
            <input v-model="form.district" type="text" placeholder="e.g., Faisalabad" required
              class="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-green-600 focus:outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Province</label>
            <input v-model="form.province" type="text" placeholder="punjab"
              class="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-green-600 focus:outline-none" />
          </div>
        </div>

        <button type="submit" :disabled="isSubmitting"
          class="w-full bg-green-700 hover:bg-green-800 text-white font-medium py-2.5 rounded transition disabled:opacity-50 mt-2">
          {{ isSubmitting ? 'Please wait...' : (isLandownerRole || !form.role ? 'Register' : 'Continue') }}
        </button>

        <router-link to="/login" class="block text-center text-sm text-gray-600 hover:text-green-700 transition mt-2">
          Already have an account? Login
        </router-link>
      </form>

      <div v-else-if="currentStep === 1 && isFarmerRole" :key="'farmer-1'">
        <h3 class="font-bold text-gray-800 mb-2">Find Your Local Numberdar</h3>
        <p class="text-sm text-gray-500 mb-3">
          Your local Numberdar verifies your account before you can apply for a loan. You can select one now, or skip and do this later.
        </p>
        <div v-if="community.numberdars.length > 0" class="space-y-2 mb-4 max-h-64 overflow-y-auto">
          <label v-for="nd in community.numberdars" :key="nd.id"
            :class="['flex items-center justify-between p-3 border rounded cursor-pointer',
              selectedNumberdarId === nd.id ? 'border-green-600 bg-green-50' : 'border-gray-200']">
            <div>
              <p class="text-sm font-medium">{{ nd.full_name }}</p>
              <p class="text-xs text-gray-500">{{ nd.jurisdiction_district }} — {{ nd.total_farmers_verified }} farmers verified</p>
            </div>
            <input type="radio" :value="nd.id" v-model="selectedNumberdarId" class="ml-2" />
          </label>
        </div>
        <p v-else class="text-sm text-gray-400 mb-4">No Numberdars found in {{ form.district }} yet.</p>

        <button @click="handleSubmitVerificationRequest" :disabled="!selectedNumberdarId"
          class="w-full bg-green-700 text-white py-2.5 rounded font-medium disabled:opacity-50 mb-2">
          Submit Request
        </button>

        <p class="text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded p-2 mb-2">
          ⚠ If you skip this step, you won't be able to apply for a loan until a Numberdar verifies your account later from your dashboard.
        </p>
        <button @click="handleSkipVerification" type="button" class="w-full text-sm text-gray-500 hover:text-gray-700 py-1">
          Skip for now
        </button>
      </div>

      <div v-else-if="currentStep === 1 && isCorporateRole" :key="'corp-1'" class="space-y-4">
        <h3 class="font-bold text-gray-800 mb-1">Business Details</h3>
         <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Shop Name</label>
          <input v-model="form.shop_name" type="text" placeholder="e.g., Ali Traders" class="w-full border border-gray-300 rounded px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">SECP Registration Number</label>
          <input v-model="form.secp_registration_number" type="text" placeholder="SECP-NTN-XXXXXXXX" class="w-full border border-gray-300 rounded px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">NTN Number</label>
          <input v-model="form.ntn_number" type="text" placeholder="7 digits" class="w-full border border-gray-300 rounded px-3 py-2" />
        </div>

       <button @click="handleBusinessDetailsContinue" :disabled="isSubmitting"
          class="w-full bg-green-700 text-white py-2.5 rounded font-medium disabled:opacity-50">
          {{ isSubmitting ? 'Please wait...' : 'Continue' }}
        </button>
      </div>

      <div v-else-if="currentStep === 2 && isFarmerRole" :key="'farmer-2'">
        <h3 class="font-bold text-gray-800 mb-2">Before You Continue</h3>
        <p class="text-sm text-gray-500 mb-3">
          Before your first loan, your bank will need to run a credit history check (through eCIB and Tasdeeq) with your
          explicit consent. You'll be asked to confirm this separately, with an OTP, at that time.
        </p>
        <label class="flex items-start gap-2 text-sm mb-2">
          <input type="checkbox" v-model="consent1" class="mt-1" />
          <span>I understand a credit check will be required before my first loan</span>
        </label>
        <label class="flex items-start gap-2 text-sm mb-4">
          <input type="checkbox" v-model="consent2" class="mt-1" />
          <span>I agree to FasalPay's Terms & Privacy Policy</span>
        </label>
        <button @click="handleCompleteFarmerRegistration" :disabled="!allConsented"
          class="w-full bg-green-700 text-white py-2.5 rounded font-medium disabled:opacity-50">
          Complete Registration
        </button>
      </div>

      <div v-else-if="currentStep === 2 && isCorporateRole" :key="'corp-2'" class="space-y-4">
        <h3 class="font-bold text-gray-800 mb-1">Verification Documents</h3>
        <p class="text-sm text-gray-500 mb-2">
          Upload these documents for an admin to verify your business before you can receive payments.
        </p>
        <DocumentUpload v-model="secpDocument" label="SECP Certificate" />
        <DocumentUpload v-model="incorporationDocument" label="Incorporation Certificate" />
        <button @click="handleFinishCorporateRegistration" :disabled="!documentsReady"
          class="w-full bg-green-700 text-white py-2.5 rounded font-medium disabled:opacity-50">
          Submit for Verification
        </button>
        <p class="text-xs text-gray-500 text-center">
          Your account is created — an admin will confirm your SECP/NTN details before you can transact.
        </p>
      </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useCommunityStore } from '@/stores/community.js'
import { ROLE_HOME } from '@/constants/roles.js'
import StepWizard from '@/components/shared/StepWizard.vue'
import DocumentUpload from '@/components/shared/DocumentUpload.vue'

const router = useRouter()
const auth = useAuthStore()
const community = useCommunityStore()
const isSubmitting = ref(false)
const errorMessage = ref('')
const currentStep = ref(0)
const completedSteps = ref([])

const form = reactive({ full_name: '', phone: '', cnic: '', password: '', role: '', district: '', province: 'Punjab', shop_name: '', secp_registration_number: '', ntn_number: '' })

const isFarmerRole = computed(() => ['smallholder', 'tenant'].includes(form.role))
const isCorporateRole = computed(() => form.role === 'shopkeeper')
const isLandownerRole = computed(() => form.role === 'landowner')

const wizardSteps = computed(() => {
  if (isFarmerRole.value) {
    return [
      { id: 'basic', label: 'Basic Info', icon: '📋' },
      { id: 'community', label: 'Community Link', icon: '👤' },
      { id: 'consent', label: 'Consent', icon: '✓' },
    ]
  }
  if (isCorporateRole.value) {
    return [
      { id: 'basic', label: 'Basic Info', icon: '📋' },
      { id: 'business', label: 'Business Details', icon: '🏪' },
      { id: 'documents', label: 'Documents', icon: '📄' },
    ]
  }
  return null
})

function validateBasicInfo() {
  if (!form.full_name.trim() || !form.phone.trim() || !form.cnic.trim() || !form.password || !form.role || !form.district.trim()) {
    errorMessage.value = 'All fields are required.'
    return false
  }
  return true
}

function handleError(err) {
  errorMessage.value = err.response?.data?.message || Object.values(err.response?.data || {})[0]?.[0] || 'Registration failed.'
}

async function submitRegistration() {
  const payload = {
    full_name: form.full_name, phone: form.phone, cnic: form.cnic, password: form.password,
    role: form.role, district: form.district, province: form.province,
  }
  if (isCorporateRole.value) {
    payload.shop_name = form.shop_name
    payload.secp_registration_number = form.secp_registration_number
    payload.ntn_number = form.ntn_number
  }
  return auth.register(payload)
}

async function handleStep0Continue() {
  errorMessage.value = ''
  if (!validateBasicInfo()) return

  if (isLandownerRole.value || !form.role) {
    isSubmitting.value = true
    try {
      await submitRegistration()
      router.push(ROLE_HOME[form.role] || '/login')
    } catch (err) {
      handleError(err)
    } finally {
      isSubmitting.value = false
    }
    return
  }

  if (isFarmerRole.value) {
    isSubmitting.value = true
    try {
      await submitRegistration()
      completedSteps.value = [0]
      currentStep.value = 1
    } catch (err) {
      handleError(err)
    } finally {
      isSubmitting.value = false
    }
    return
  }

  completedSteps.value = [0]
  currentStep.value = 1
}

const selectedNumberdarId = ref('')

watch(currentStep, (step) => {
  if (isFarmerRole.value && step === 1) {
    community.fetchNumberdars(form.district)
  }
})

async function handleSubmitVerificationRequest() {
  if (!selectedNumberdarId.value) return
  try {
    await community.submitRequest(selectedNumberdarId.value)
    completedSteps.value = [0, 1]
    currentStep.value = 2
  } catch (err) {
  
  }
}

function handleSkipVerification() {
  completedSteps.value = [0, 1]
  currentStep.value = 2
}

const consent1 = ref(false)
const consent2 = ref(false)
const allConsented = computed(() => consent1.value && consent2.value)

function handleCompleteFarmerRegistration() {
  router.push(ROLE_HOME[form.role] || '/login')
}

async function handleBusinessDetailsContinue() {
  errorMessage.value = ''
  if (!form.shop_name.trim() || !form.secp_registration_number.trim() || !form.ntn_number.trim()) {
    errorMessage.value = 'Shop name, SECP number, and NTN number are all required.'
    return
  }
  isSubmitting.value = true
  try {
    await submitRegistration()
    completedSteps.value = [0, 1]
    currentStep.value = 2
  } catch (err) {
    handleError(err)
  } finally {
    isSubmitting.value = false
  }
}

const secpDocument = ref(null)
const incorporationDocument = ref(null)
const documentsReady = computed(() => !!secpDocument.value && !!incorporationDocument.value)

function handleFinishCorporateRegistration() {
  router.push(ROLE_HOME[form.role] || '/login')
}
</script>