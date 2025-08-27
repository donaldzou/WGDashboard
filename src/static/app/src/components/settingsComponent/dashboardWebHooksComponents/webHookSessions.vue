<script setup lang="ts">
import { fetchGet } from "@/utilities/fetch.js"
import LocaleText from "@/components/text/localeText.vue";
import {computed, onBeforeUnmount, ref, watch} from "vue";
import WebHookSession from "@/components/settingsComponent/dashboardWebHooksComponents/webHookSession.vue";
import PreviousWebHookSession
	from "@/components/settingsComponent/dashboardWebHooksComponents/previousWebHookSession.vue";
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

// watch(() => latestSession.value.Status, () => {
// 	if (latestSession.value.Status > -1) clearInterval(refreshInterval.value)
// })

// if (latestSession.value.Status === -1){
//
// }
refreshInterval.value = setInterval(() => {
	getSessions()
}, 5000)
onBeforeUnmount(() => {
	clearInterval(refreshInterval.value)
})
</script>

<template>
	<div v-if="latestSession">
		<div class="p-3">
			<h6 class="mb-3">
				<LocaleText t="Latest Session"></LocaleText>
			</h6>
			<WebHookSession :session="latestSession" :key="latestSession.WebHookSessionID"></WebHookSession>
		</div>
		<div class="border-top p-3" v-if="sessions.length > 1">
			<h6>
				<LocaleText t="Previous Sessions"></LocaleText>
			</h6>
			<div class="d-flex flex-column gap-2">
				<PreviousWebHookSession :session="session"
										:key="session.WebHookSessionID"
										v-for="session in sessions.slice(1)"></PreviousWebHookSession>
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