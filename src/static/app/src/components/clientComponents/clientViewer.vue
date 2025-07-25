<script setup lang="ts" async>
import {useRoute} from "vue-router";
import { fetchGet } from "@/utilities/fetch.js"


import {DashboardClientAssignmentStore} from "@/stores/DashboardClientAssignmentStore.js";
import {computed, ref, watch} from "vue";
import LocaleText from "@/components/text/localeText.vue";
import ClientAssignedPeers from "@/components/clientComponents/clientAssignedPeers.vue";
import ClientResetPassword from "@/components/clientComponents/clientResetPassword.vue";
const assignmentStore = DashboardClientAssignmentStore()
const route = useRoute()

const client = computed(() => {
	return assignmentStore.getClientById(route.params.id)
})

const clientAssignedPeers = ref({})
const getAssignedPeers = async () => {
	await fetchGet('/api/clients/assignedPeers', {
		ClientID: client.value.ClientID
	}, (res) => {
		clientAssignedPeers.value = res.data;
	})
}

if (client.value){
	watch(() => client.value.ClientID, async () => {
		await getAssignedPeers()
	})
	await getAssignedPeers()
}
</script>

<template>
	<div class="text-body d-flex flex-column overflow-y-scroll h-100" v-if="client" :key="client.ClientID">
		<div class="p-4 border-bottom bg-body-tertiary">
			<small class="text-muted">
				<LocaleText t="Email"></LocaleText>
			</small>
			<h1>
				{{ client.Email }}
			</h1>
			<div class="d-flex align-items-center">
				<small class="text-muted">
					<LocaleText t="Client ID"></LocaleText>
				</small>
				<small class="ms-auto">
					<samp>{{ client.ClientID }}</samp>
				</small>
			</div>
		</div>
		<div style="flex: 1 0 0; overflow-y: scroll;">
			<ClientAssignedPeers

				@refresh="getAssignedPeers()"
				:clientAssignedPeers="clientAssignedPeers"
				:client="client"></ClientAssignedPeers>
			<ClientResetPassword
				:client="client" v-if="client.ClientGroup === 'Local'"></ClientResetPassword>
		</div>
	</div>
	<div v-else class="d-flex w-100 h-100 text-muted">
		<div class="m-auto text-center">
			<h1>
				<i class="bi bi-person-x"></i>
			</h1>
			<p>
				<LocaleText t="Client does not exist"></LocaleText>
			</p>
		</div>
	</div>
</template>

<style scoped>

</style>