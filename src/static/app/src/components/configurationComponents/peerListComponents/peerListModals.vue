<script setup>
import {defineAsyncComponent} from "vue";
const props = defineProps({
	configurationModals: Object,
	configurationModalSelectedPeer: Object
})
const emits = defineEmits(["refresh"])


const DeleteConfigurationModal = defineAsyncComponent(() => import("@/components/configurationComponents/deleteConfiguration.vue"))
const ConfigurationBackupRestoreModal = defineAsyncComponent(() => import("@/components/configurationComponents/configurationBackupRestore.vue"))
const SelectPeersModal = defineAsyncComponent(() => import("@/components/configurationComponents/selectPeers.vue"))
const EditConfigurationModal = defineAsyncComponent(() => import("@/components/configurationComponents/editConfiguration.vue"))
const PeerShareLinkModal = defineAsyncComponent(() => import("@/components/configurationComponents/peerShareLinkModal.vue"))
const PeerJobsLogsModal = defineAsyncComponent(() => import("@/components/configurationComponents/peerJobsLogsModal.vue"))
const PeerJobsAllModal = defineAsyncComponent(() => import("@/components/configurationComponents/peerJobsAllModal.vue"))
const PeerJobsModal = defineAsyncComponent(() => import("@/components/configurationComponents/peerJobs.vue"))
const PeerQRCodeModal = defineAsyncComponent(() => import("@/components/configurationComponents/peerQRCode.vue"))
const PeerConfigurationFileModal = defineAsyncComponent(() => import("@/components/configurationComponents/peerConfigurationFile.vue"))
const PeerSettingsModal = defineAsyncComponent(() => import("@/components/configurationComponents/peerSettings.vue"))
</script>

<template>
	<Transition name="zoom">
		<PeerSettingsModal v-if="configurationModals.peerSetting.modalOpen"
		              key="settings"
		              :selectedPeer="configurationModalSelectedPeer"
		              @refresh="emits('refresh')"
		              @close="configurationModals.peerSetting.modalOpen = false">
		</PeerSettingsModal>
	</Transition>
</template>

<style scoped>

</style>