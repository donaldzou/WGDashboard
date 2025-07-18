<script setup lang="ts">
import {DashboardClientAssignmentStore} from "@/stores/DashboardClientAssignmentStore.js";
import LocaleText from "@/components/text/localeText.vue";
import {ref} from "vue";
const assignmentStore = DashboardClientAssignmentStore()
import {GetLocale} from "@/utilities/locale.js";
import ClientGroup from "@/components/clientComponents/clientGroup.vue";
import * as sea from "node:sea";

await assignmentStore.getClients();

const searchString = ref("")
</script>

<template>
	<div class="w-100 h-100 pb-2 text-body">
		<div class="rounded-3 bg-body-tertiary d-flex text-body p-3 align-items-center shadow sticky-top mb-3">
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
		<div class="d-flex gap-3 flex-column">
			<ClientGroup v-for="(clients, groupName) in assignmentStore.clients" 
			             :searchString="searchString"
			             :clients="clients" :groupName="groupName"></ClientGroup>
		</div>
	</div>
</template>

<style scoped>

</style>