<script setup>

import {fetchPost} from "@/utilities/fetch.js";
import {ref, watch} from "vue";

const props = defineProps(['body', 'selectedPeer'])
const preview = ref("")
const error = ref(false)
const errorMsg = ref("")


const getPreview = async () => {
	if (props.body){
		error.value = false;
		preview.value = ("")
		await fetchPost('/api/email/previewBody', {
			Body: props.body,
			ConfigurationName: props.selectedPeer.configuration.Name,
			Peer: props.selectedPeer.id
		}, (res) => {

			if (res.status){
				preview.value = res.data;
			}else{
				errorMsg.value = res.message
			}
			error.value = !res.status
		})
	}
}

await getPreview();
let timeout = undefined
watch(() => {
	return props.body
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
})
</script>

<template>
	<div class="card rounded-0 border-start-0 border-bottom-0 bg-body-secondary" style="height: 400px; overflow: scroll">
		<div class="card-body">
			<div class="alert alert-danger rounded-3" v-if="error && body">
				<i class="bi bi-exclamation-triangle-fill me-2"></i>
				<span class="font-monospace">
					{{errorMsg}}
				</span>
			</div>
			<div  v-if="body"
			     :class="{'opacity-50': error}"
			     :innerText="preview"></div>
		</div>
	</div>
</template>

<style scoped>
	.card{
		border-color: var(--bs-border-color) !important;
	}
</style>