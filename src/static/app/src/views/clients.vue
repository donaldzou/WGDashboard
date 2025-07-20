<script setup lang="ts">
import {DashboardClientAssignmentStore} from "@/stores/DashboardClientAssignmentStore.js";
import LocaleText from "@/components/text/localeText.vue";
import {ref} from "vue";
const assignmentStore = DashboardClientAssignmentStore()
import {GetLocale} from "@/utilities/locale.js";
import ClientGroup from "@/components/clientComponents/clientGroup.vue";
import { fetchGet } from "@/utilities/fetch.js"

await assignmentStore.getClients();
assignmentStore.getAllConfigurationsPeers();

const searchString = ref("")
</script>

<template>
	<div class="text-body w-100 h-100 pb-2">
		<div class="w-100 h-100 card rounded-3">
			<div class="row h-100 g-0">
				<div class="col-sm-4 border-end d-flex flex-column">
					<div class="d-flex text-body align-items-center sticky-top p-3 bg-body-tertiary rounded-top-3" style="border-top-right-radius: 0 !important;">
						<label for="searchClient"><i class="bi bi-search me-2"></i></label>
						<input
							v-model="searchString"
							id="searchClient"
							class="form-control rounded-3 form-control-sm"
							:placeholder="GetLocale('Search Clients...')"
							type="email" style="width: auto;">
						<button class="btn btn-body ms-auto bg-body-secondary rounded-3 btn-sm">
							<i class="bi bi-gear-fill me-2"></i>
							<LocaleText t="Settings"></LocaleText>
						</button>
					</div>
					<div class="d-flex flex-column overflow-y-scroll" style="flex: 1 0 0">
						<ClientGroup v-for="(clients, groupName) in assignmentStore.clients"
						             :searchString="searchString"
						             :clients="clients" :groupName="groupName"></ClientGroup>
					</div>
				</div>
				<div class="col-sm-8">
					<RouterView></RouterView>
				</div>
			</div>
			



		</div>
	</div>
</template>

<style scoped>

</style>