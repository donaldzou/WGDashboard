<script setup lang="ts">
import {onMounted, watch, watchEffect} from "vue";
import { fetchGet } from "@/utilities/fetch.js"
import {DashboardClientAssignmentStore} from "@/stores/DashboardClientAssignmentStore.js";

const props = defineProps(['client'])
watchEffect(async () => {
	const clientId = props.client.ClientID;
	await fetchGet('/api/clients/assignedPeers', {
		ClientID: clientId
	}, (res) => {
		console.log(res)
	})
})

const assignmentStore = DashboardClientAssignmentStore()

</script>

<template>
<div class="border w-100 d-flex " style="height: 400px">
	<div style="flex: 1 0 0; overflow: scroll">
		<div class="card rounded-0 border-0" v-for="(peers, configuration) in assignmentStore.allConfigurationsPeers">
			<div class="card-header sticky-top z-5 bg-body-secondary border-0 rounded-0 shadow border-bottom btn-brand text-white">
				<samp>{{ configuration }}</samp>
			</div>
			<div class="card-body p-0">
				<div class="list-group list-group-flush" >
					<button
						class="list-group-item d-flex flex-column border-bottom list-group-item-action"
						v-for="peer in peers" >
						<small class="text-body">
							{{ peer.id }}
						</small>
						<small class="text-muted">
							{{ client.name ? client.name : 'Untitled Peer'}}
						</small>
					</button>
				</div>

			</div>
		</div>
	</div>
	<div class="px-3 border-start border-end d-flex flex-column justify-content-center gap-3">
		<button class="btn">
			<i class="bi bi-chevron-left"></i>
		</button>
		<button class="btn">
			<i class="bi bi-chevron-right"></i>
		</button>
	</div>
	<div style="flex: 1 0 0">
		hi
	</div>
</div>
</template>

<style scoped>
div .list-group-item:last-child{
	border-bottom: none !important;
}
</style>