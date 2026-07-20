<template>
  <div>
    <DashboardHero
      eyebrow="Numberdar Portal"
      :title="`${$t('numberdar.welcome')}، ${firstName}`"
      :subtitle="auth.user?.district ? `${auth.user.district} ${$t('numberdar.communityRegion')}` : $t('numberdar.communityPortal')"
      :stats="heroStats"
    />

    <div class="content-container -mt-8 relative z-20">
      <QuickActionsBar :actions="quickActions" />
    </div>

    <DashboardSection id="queue-section" tone="white" :eyebrow="$t('numberdar.communityEyebrow')" :title="$t('numberdar.farmerVerificationQueue')">
      <div class="max-w-xl">
        <div :class="['p-4 rounded-xl shadow-sm bg-white border mb-6', community.pendingQueueCount > 0 ? 'border-amber-400' : 'border-gray-100']">
          <p class="text-xs font-medium text-gray-500 mb-1">{{ $t('numberdar.pendingApprovals') }}</p>
          <p class="text-3xl font-bold" :class="community.pendingQueueCount > 0 ? 'text-amber-600' : 'text-gray-800'">{{ community.pendingQueueCount }}</p>
        </div>
        <router-link to="/numberdar/queue" class="btn-primary inline-flex items-center gap-2">
          {{ $t('numberdar.goToQueue') }}
        </router-link>
      </div>
    </DashboardSection>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { Users, ClipboardCheck, ArrowRight } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth.js'
import { useCommunityStore } from '@/stores/community.js'
import { useScrollTo } from '@/composables/useScrollTo.js'
import DashboardHero from '@/components/layout/DashboardHero.vue'
import DashboardSection from '@/components/layout/DashboardSection.vue'
import QuickActionsBar from '@/components/shared/QuickActionsBar.vue'
import { useI18n } from 'vue-i18n' 

const auth = useAuthStore()
const community = useCommunityStore()
const scrollToSection = useScrollTo()
const { t } = useI18n()

const firstName = computed(() => auth.user?.full_name || 'Numberdar')

const heroStats = computed(() => [
  { icon: ClipboardCheck, label: t('numberdar.pendingApprovals'), value: community.pendingQueueCount },
  { icon: Users, label: t('numberdar.districtLabel'), value: auth.user?.district || t('numberdar.assignedArea') }
])

const quickActions = computed(() => [
  { label: t('numberdar.qaVerificationQueue'), icon: ClipboardCheck, onClick: () => scrollToSection('queue-section') },
])

onMounted(() => community.fetchQueue())
</script>