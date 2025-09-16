<script setup>

import {fetchPost} from "@/utilities/fetch.js";
import {ref, watch} from "vue";
import LocaleText from "@/components/text/localeText.vue";

const props = defineProps(['email', 'selectedPeer'])
const preview = ref("")
const error = ref(false)
const errorMsg = ref("")


const getPreview = async () => {
	if (props.email){
		error.value = false;

		await fetchPost('/api/email/preview', {
			Subject: props.email.Subject,
			Body: props.email.Body,
			ConfigurationName: props.selectedPeer.configuration.Name,
			Peer: props.selectedPeer.id
		}, (res) => {
			if (res.status){
				preview.value = res.data;
			}else{
				preview.value = ("")
				errorMsg.value = res.message
			}
			error.value = !res.status
		})
	}
}

await getPreview();
let timeout = undefined
watch(() => {
	return props.email
}, async () => {
	if (timeout === undefined){
		timeout = setTimeout(async () => {
			await getPreview();
		}, 500)
	}else{
		clearTimeout(timeout)
		timeout = setTimeout(async () => {
			await getPreview();
		}, 500)
	}
}, {
	deep: true
})
</script>

<template>
	<div class="card rounded-0 border-start-0 border-bottom-0 bg-body-secondary" style="height: 400px; overflow: scroll">
		<div class="card-body">
			<div class="alert alert-danger rounded-3" v-if="error && email.Body">
				<i class="bi bi-exclamation-triangle-fill me-2"></i>
				<span class="font-monospace">
					{{errorMsg}}
				</span>
			</div>
			<div>
				<div v-if="preview">
					<strong><LocaleText t="Subject"></LocaleText>: </strong>{{ preview.Subject }}
				</div>
				<hr>
				<div :class="{'opacity-50': error}" v-bind:innerText="preview.Body"></div>
			</div>
		</div>
	</div>
</template>

<style scoped>
	.card{
		border-color: var(--bs-border-color) !important;
	}
</style>