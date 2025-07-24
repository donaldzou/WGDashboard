<script setup lang="ts">
import LocaleText from "@/components/text/localeText.vue";
import { fetchGet, fetchPost } from "@/utilities/fetch.js"
import {ref} from "vue";
const props = defineProps(['client'])

const alert = ref(false)
const alertStatus = ref(false)
const alertMessage = ref(false)

const sendResetLink = async () => {
	let smtpReady = false;
	let token = undefined;
	await fetchPost('/api/clients/generatePasswordResetLink', {
		ClientID: props.client.ClientID
	},(res) => {
		if (res.status){
			token = res.data
			alertStatus.value = true
		}else{
			alertStatus.value = false
			alertMessage.value = res.message
			alert.value = true
		}
	})
	if (token){
		await fetchGet('/api/email/ready', {}, (res) => {
			smtpReady = res.status
		});
		if (smtpReady){
			await fetchPost('/api/email/send', {
				"Receiver": props.client.Email,
				"Body":
					`Hi${props.client.Name ? ' ' + props.client.Name: ''},\n`
			}, (res) => {

			});
		}else{

		}
	}
}

</script>

<template>
<div class="p-3 d-flex gap-3 flex-column border-bottom">
	<div class="d-flex align-items-center">
		<h6 class="mb-0">
			<LocaleText t="Reset Password"></LocaleText>
		</h6>
		<button class="btn btn-sm bg-primary-subtle text-primary-emphasis rounded-3 ms-auto"
			@click="sendResetLink()"
		>
			<i class="bi bi-send me-2"></i>
			<LocaleText t="Send Password Reset Link"></LocaleText>
		</button>
	</div>
	<div class="alert rounded-3 mb-0"
		 :class="[alertStatus ? 'alert-success' : 'alert-danger']"
		 v-if="alert">
		{{ alertMessage }}
	</div>
</div>
</template>

<style scoped>

</style>