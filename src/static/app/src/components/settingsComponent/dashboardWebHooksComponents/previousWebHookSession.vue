<script setup lang="ts">
import WebHookSession from "@/components/settingsComponent/dashboardWebHooksComponents/webHookSession.vue";
import {ref} from "vue";
const props = defineProps(['session'])
const collapse = ref(true)
</script>

<template>
<div class="card">
	<div class="card-body">
		<p class="d-flex mb-0" role="button" @click="collapse = !collapse">
			<span :class="{'text-success': session.Status === 0, 'text-danger': session.Status === 1, 'text-warning': session.Status === 2}">
				<span v-if="session.Status === 0">
					<i class="bi bi-check-circle-fill me-2"></i>
				</span>
				<span v-else-if="session.Status === 2">
					<i class="bi bi-trash3-fill me-2"></i>
				</span>
				<span v-else-if="session.Status === 1">
					<i class="bi bi-x-circle-fill me-2"></i>
				</span>
				<span v-else-if="session.Status === -1">
					<i class="spinner-border spinner-border-sm me-2"></i>
				</span>
			</span>
			{{ session.StartDate }}
			<i class="bi bi-chevron-right ms-auto"></i>
		</p>

		<WebHookSession :session="session" v-if="!collapse" class="mt-2"></WebHookSession>
	</div>
</div>
</template>

<style scoped>

</style>