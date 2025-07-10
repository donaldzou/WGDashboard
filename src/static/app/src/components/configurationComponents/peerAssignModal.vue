<script setup async>
import LocaleText from "@/components/text/localeText.vue";
import {onMounted, ref} from "vue";
import {GetLocale} from "@/utilities/locale.js";
import {fetchGet, fetchPost} from "@/utilities/fetch.js";
import SearchClients from "@/components/configurationComponents/peerAssignModalComponents/searchClients.vue";
import AssignedClients from "@/components/configurationComponents/peerAssignModalComponents/assignedClients.vue";

const props = defineProps({
	selectedPeer: Object
})
const emits = defineEmits([
	'close'
])
const assignments = ref([])
const clients = ref([])
await fetchGet('/api/clients/allClients', {},(res) => {
	clients.value = res.data;
	console.log(clients.value)
})

const getAssignedClients = async () => {
	await fetchGet('/api/clients/assignedClients', {
		ConfigurationName: props.selectedPeer.configuration.Name,
		Peer: props.selectedPeer.id
	}, (res) => {
		assignments.value = res.data
	})
}

await getAssignedClients()

const assignClient = async (clientID) => {
	await fetchPost('/api/clients/assignClient', {
		ConfigurationName: props.selectedPeer.configuration.Name,
		Peer: props.selectedPeer.id,
		ClientID: clientID
	}, async (res) => {
		if (res.status){
			await getAssignedClients()
		}
	})
}

const unassignClient = async (assignmentID) => {
	await fetchPost('/api/clients/unassignClient', {
		AssignmentID: assignmentID
	}, async (res) => {
		if (res.status){
			await getAssignedClients()
		}
	})
}
</script>

<template>
	<div class="peerSettingContainer w-100 h-100 position-absolute top-0 start-0 overflow-y-scroll">
		<div class="container d-flex h-100 w-100">
			<div class="m-auto modal-dialog-centered dashboardModal" style="width: 700px">
				<div class="card rounded-3 shadow flex-grow-1">
					<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4">
						<h4 class="mb-0">
							<LocaleText t="Assign Peer to Client"></LocaleText>
						</h4>
						<button type="button" class="btn-close ms-auto" @click="emits('close')"></button>
					</div>
					<div class="card-body px-4 pb-4 d-flex gap-2 flex-column">
						<AssignedClients 
							@unassign="args => unassignClient(args)"
							:assignments="assignments"></AssignedClients>
						<SearchClients
							:assignments="assignments"
							@assign="args => assignClient(args)"
							:clients="clients"></SearchClients>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
*:focus {
	outline: none;
}
</style>