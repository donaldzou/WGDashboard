<script setup async>
import LocaleText from "@/components/text/localeText.vue";
import {fetchGet, fetchPost} from "@/utilities/fetch.js";
import {reactive, ref} from "vue";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
const props = defineProps(['dataCopy', 'selectedPeer'])
const emailIsReady = ref(false)
await fetchGet("/api/email/ready", {}, (res) => {
	emailIsReady.value = res.status
})

const email = reactive({
	Receiver: "",
	Body: "",
	Subject: "",
	IncludeAttachment: false,
	ConfigurationName: props.selectedPeer.configuration.Name,
	Peer: props.selectedPeer.id
})
const store = DashboardConfigurationStore()
const sending = ref(false)

const sendEmail = async () => {
	sending.value = true;
	await fetchPost("/api/email/send", email, (res) => {
		if (res.status){
			store.newMessage("Server", "Email sent successfully!", "success")
		}else{
			store.newMessage("Server", `Email sent failed! Reason: ${res.message}`, "danger")
		}
		sending.value = false
	})
}

</script>

<template>
	<div v-if="emailIsReady">
		<h6 class="mb-3">
			<LocaleText t="Share with Email"></LocaleText>
		</h6>
		<form class="d-flex gap-3 flex-column"
			@submit="(e) => {e.preventDefault(); sendEmail()}"
		>
			<div>
				<div class="position-relative" >
					<i class="bi bi-person-circle" style="position: absolute; top: 0.4rem; left: 0.75rem;"></i>
					<input type="email" class="form-control rounded-top-3 rounded-bottom-0"
					       style="padding-left: calc( 0.75rem + 24px )"
					       v-model="email.Receiver"
					       :disabled="sending"
					       placeholder="Send to who?"
					       required
					       id="email_receiver" aria-describedby="emailHelp">
				</div>
				<div class="position-relative">
					<i class="bi bi-hash" style="position: absolute; top: 0.4rem; left: 0.75rem;"></i>
					<input type="text" class="form-control rounded-0 border-top-0 border-bottom-0"
					       style="padding-left: calc( 0.75rem + 24px )"
					       placeholder="Subject"
					       :disabled="sending"
					       v-model="email.Subject"
					       id="email_subject" aria-describedby="emailHelp">
				</div>
				<textarea class="form-control rounded-bottom-3 rounded-top-0" 
				          v-model="email.Body"
				          :disabled="sending"
				          placeholder="Body"
				          style="min-height: 300px"></textarea>
				
			</div>
			<div class="form-check form-switch">
				<input class="form-check-input" type="checkbox" 
				       v-model="email.IncludeAttachment"
				       role="switch" id="includeAttachment" checked>
				<label class="form-check-label" for="includeAttachment">
					<LocaleText t="Include configuration file as an attachment"></LocaleText>
				</label>
			</div>
			<button
				:disabled="sending"
				class="btn bg-primary-subtle text-primary-emphasis border-primary-subtle rounded-3">
				<span v-if="!sending">
					<i class="bi bi-send me-2"></i><LocaleText t="Send"></LocaleText>
				</span>
				<span v-else>
					<span class="spinner-border spinner-border-sm me-2"></span>
					<LocaleText t="Sending..."></LocaleText>
				</span>
			</button>
		</form>
	</div>
	<div v-else>
		<small>
			<LocaleText t="SMTP is not configured, please navigate to "></LocaleText>
			<RouterLink to="/settings">
				<LocaleText t="Settings"></LocaleText>
			</RouterLink>
			<LocaleText t=" to finish setup"></LocaleText>
		</small>
	</div>
</template>

<style scoped>

</style>