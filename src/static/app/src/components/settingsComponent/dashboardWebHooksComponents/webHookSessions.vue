<script setup lang="ts">
import { fetchGet } from "@/utilities/fetch.js"
import LocaleText from "@/components/text/localeText.vue";
import {computed, ref, watch} from "vue";
const props = defineProps(['webHook'])
const sessions = ref([])

const refreshInterval = ref(undefined);

const getSessions = async () => {
	await fetchGet("/api/webHooks/getWebHookSessions", {
		WebHookID: props.webHook.WebHookID
	}, (res) => {
		sessions.value = res.data
	})
}

await getSessions()

const latestSession = computed(() => {
	if (!sessions.value){
		return undefined
	}
	return sessions.value[0]
})

watch(() => latestSession.value.Status, () => {
	if (latestSession.value.Status > -1) clearInterval(refreshInterval.value)
})



if (latestSession.value.Status === -1){
	refreshInterval.value = setInterval(() => {
		getSessions()
	}, 5000)
}
</script>

<template>
	<div class="p-3" v-if="latestSession">
		<h6 class="mb-3">
			<LocaleText t="Latest Session"></LocaleText>
		</h6>
		<h3 :class="{'text-success': latestSession.Status === 0, 'text-danger': latestSession.Status === 1}">
			<span v-if="latestSession.Status === 0">
				<i class="bi bi-check-circle-fill me-2"></i><LocaleText t="Success"></LocaleText>
			</span>
			<span v-else-if="latestSession.Status === 1">
				<i class="bi bi-x-circle-fill me-2"></i><LocaleText t="Failed"></LocaleText>
			</span>
			<span v-else-if="latestSession.Status === -1">
				<i class="spinner-border me-2"></i><LocaleText t="Requesting..."></LocaleText>
			</span>
		</h3>
		<div class="d-flex gap-4 align-items-center">
			<div>
				<small class="text-muted">
					<LocaleText t="Started At"></LocaleText>
				</small>
				<h6>
					{{ latestSession.StartDate }}
				</h6>
			</div>
			<div v-if="latestSession.EndDate">
				<i class="bi bi-arrow-right"></i>
			</div>
			<div v-if="latestSession.EndDate">
				<small class="text-muted">
					<LocaleText t="Ended At"></LocaleText>
				</small>
				<h6>
					{{ latestSession.EndDate }}
				</h6>
			</div>
		</div>
		<hr>
		<div>
			<h6>
				<LocaleText t="Logs"></LocaleText>
			</h6>
			<div class="table-responsive">
				<table class="table">
					<thead>
					<tr>
						<th scope="col">
							<LocaleText t="Datetime"></LocaleText>
						</th>
						<th scope="col">
							<LocaleText t="Status"></LocaleText>
						</th>
						<th scope="col">
							<LocaleText t="Message"></LocaleText>
						</th>
					</tr>
					</thead>
					<tbody>
					<tr v-for="log in [...latestSession.Logs.Logs].reverse()">
						<td style="white-space: nowrap">
							{{ log.LogTime }}
						</td>
						<td style="white-space: nowrap" :class="{'text-success': log.Status === 0, 'text-danger': log.Status === 1}">
							<span v-if="log.Status === 0">
								<i class="bi bi-check-circle-fill me-2"></i>
							</span>
							<span v-else-if="log.Status === 1">
								<i class="bi bi-x-circle-fill me-2"></i>
							</span>
							<span v-else-if="log.Status === -1">
								<i class="bi bi-circle me-2"></i>
							</span>
						</td>
						<td>
							{{ log.Message }}
						</td>
					</tr>
					</tbody>
				</table>
			</div>
		</div>

		<div>
			<h6>
				<LocaleText t="Data"></LocaleText>
			</h6>
			<div class="bg-body-tertiary p-3 rounded-3" style="max-height: 200px; overflow: scroll">
				<pre><code>{{ JSON.stringify(latestSession.Data, null, 4) }}</code></pre>
			</div>
		</div>
	</div>
	<div v-else class="p-3">
		<div class="bg-body-tertiary p-3 w-100 d-flex rounded-3" >
			<h6 class="mb-0 m-auto">No Sessions</h6>
		</div>
 	</div>
</template>

<style scoped>
.table > :not(caption) > * > *{
	padding-left: 0 !important;
	padding-right: 1rem !important;
}
</style>