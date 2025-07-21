<script setup lang="ts" async>
import {useRoute} from "vue-router";
import { fetchGet } from "@/utilities/fetch.js"


import {DashboardClientAssignmentStore} from "@/stores/DashboardClientAssignmentStore.js";
import {computed} from "vue";
import LocaleText from "@/components/text/localeText.vue";
import ClientAssignedPeers from "@/components/clientComponents/clientAssignedPeers.vue";
const assignmentStore = DashboardClientAssignmentStore()
const route = useRoute()

const client = computed(() => {
	return assignmentStore.getClientById(route.params.id)
})
</script>

<template>
	<div class="text-body d-flex flex-column gap-3" v-if="client">
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
		<div class="px-4">

			<ClientAssignedPeers :client="client"></ClientAssignedPeers>
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