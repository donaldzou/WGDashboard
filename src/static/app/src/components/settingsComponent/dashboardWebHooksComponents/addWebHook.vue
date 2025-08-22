<script setup lang="ts">
import {ref} from "vue";
import {fetchGet, fetchPost} from "@/utilities/fetch.js"
import LocaleText from "@/components/text/localeText.vue";
import { v4 } from "uuid";

const newWebHook = ref({
	ContentType: String,
	Headers: Object,
	IsActive: Boolean,
	Notes: String,
	PayloadURL: String,
	SubscribedActions: Array,
	VerifySSL: Boolean,
	WebHookID: String
})

const props = defineProps(['webHook'])

if (!props.webHook){
	await fetchGet("/api/webHooks/createWebHook", {}, (res) => {
		newWebHook.value = res.data
	})
}else{
	newWebHook.value = {...props.webHook}
}

const Actions = ref({
	'peer_created': "Peer Created",
	'peer_deleted': "Peer Deleted",
	'peer_updated': "Peer Updated"
})
const emits = defineEmits(['refresh'])

const alert = ref(false)
const alertMsg = ref("")
const submitting = ref(false)
const submitWebHook = async (e) => {
	if (e) e.preventDefault()
	submitting.value = true
	await fetchPost("/api/webHooks/updateWebHook", newWebHook.value, (res) => {
		if (res.status){
			emits('refresh')
		}else{
			alert.value = true
			alertMsg.value = res.message
		}
		submitting.value = false
	})
}
</script>

<template>
<div class="p-3">
	<div v-if="!webHook">
		<h6>
			<LocaleText t="Add Webhook"></LocaleText>
		</h6>
		<p>
			<LocaleText t="WGDashboard will sent a POST Request to the URL below with details of any subscribed events."></LocaleText>
		</p>
	</div>
	<form
		@submit="(e) => submitWebHook(e)"
		class="d-flex flex-column gap-2">
		<div>
			<label for="PayloadURL" class="form-label fw-bold text-muted">
				<small>
					<LocaleText t="Payload URL"></LocaleText>*
				</small>
			</label>
			<input
				required
				:disabled="submitting"
				id="PayloadURL" v-model="newWebHook.PayloadURL"
				class="form-control rounded-3" type="url">
		</div>
		<div>
			<label for="ContentType" class="form-label fw-bold text-muted">
				<small>
					<LocaleText t="Content Type"></LocaleText>*
				</small>
			</label>
			<select
				:disabled="submitting"
				id="ContentType" v-model="newWebHook.ContentType"
				class="form-select rounded-3" required>
				<option value="application/json">
					application/json
				</option>
				<option value="application/x-www-form-urlencoded">
					application/x-www-form-urlencoded
				</option>
			</select>
		</div>
		<div>
			<label class="form-label fw-bold text-muted">
				<small>
					<LocaleText t="Verify SSL"></LocaleText>
				</small>
			</label>
			<div>
				<div class="form-check form-switch mb-2">
					<input
						:disabled="submitting"
						v-model="newWebHook.VerifySSL"
						class="form-check-input" type="checkbox" role="switch" id="VerifySSL" >
					<label class="form-check-label" for="VerifySSL">
						<LocaleText :t="newWebHook.VerifySSL ? 'Enabled':'Disabled'"></LocaleText>
					</label>
				</div>
				<div class="alert-danger alert rounded-3" v-if="!newWebHook.VerifySSL">
					<i class="bi bi-exclamation-triangle-fill me-2"></i>
					<LocaleText t="We highly suggest to enable SSL verification"></LocaleText>
				</div>
			</div>
		</div>
		<div>
			<label class="form-label fw-bold text-muted">
				<small>
					<LocaleText t="Custom Headers"></LocaleText>
				</small>
			</label>
			<div class="card rounded-3">
				<div class="card-body d-flex gap-2 flex-column">
					<div class="d-flex gap-2" v-for="(header, headerKey) in newWebHook.Headers">
						<div class="flex-grow-1">
							<input class="form-control rounded-3 form-control-sm"
								   :disabled="submitting"
								   v-model="header.key"
								   placeholder="Key">
						</div>
						<div class="flex-grow-1">
							<input class="form-control rounded-3 form-control-sm"
								   :disabled="submitting"
								   v-model="header.value"
								   placeholder="Value">
						</div>
						<button
							:class="{disabled: submitting}"
							type="button"
							@click="delete newWebHook.Headers[headerKey]"
							class="btn btn-sm bg-danger-subtle text-danger-emphasis border-danger-subtle rounded-3">
							<i class="bi bi-trash-fill"></i>
						</button>
					</div>
					<button
						type="button"
						:class="{disabled: submitting}"
						@click="newWebHook.Headers[v4().toString()] = {key: '', value: ''}"
						class="btn btn-sm bg-primary-subtle text-primary-emphasis border-primary-subtle rounded-3">
						<i class="bi bi-plus-lg me-2"></i><LocaleText t="Header"></LocaleText>
					</button>
				</div>
			</div>
		</div>
		<hr>
		<div>
			<label class="form-label fw-bold text-muted">
				<small>
					<LocaleText t="Subscribed Actions"></LocaleText>
				</small>
			</label>
			<div>
				<div v-for="(action, key) in Actions" class="form-check form-check-inline">
					<input class="form-check-input"
						   :disabled="newWebHook.SubscribedActions.length === 1 && newWebHook.SubscribedActions.includes(key) || submitting"
						   type="checkbox" :id="key"
						   :value="key"
						   v-model="newWebHook.SubscribedActions">
					<label class="form-check-label" :for="key">{{ action }}</label>
				</div>
			</div>
		</div>
		<hr>
		<div>
			<label class="form-label fw-bold text-muted">
				<small>
					<LocaleText t="Enable Webhook"></LocaleText>
				</small>
			</label>
			<div>
				<div class="form-check form-switch mb-2">
					<input
						:disabled="submitting"
						v-model="newWebHook.IsActive"
						class="form-check-input" type="checkbox" role="switch" id="IsActive" >
					<label class="form-check-label" for="IsActive">
						<LocaleText :t="newWebHook.IsActive ? 'Yes':'No'"></LocaleText>
					</label>
				</div>
			</div>
		</div>
		<div class="alert alert-danger rounded-3" v-if="alert">
			{{ alertMsg }}
		</div>
		<div class="d-flex gap-2">
			<button
				type="submit"
				:class="{disabled: submitting}"
				class="ms-auto btn bg-success-subtle text-success-emphasis border-success-subtle rounded-3">
				<LocaleText t="Save"></LocaleText>
			</button>
		</div>
		<template v-if="webHook">
			<hr>
			<div class="d-flex align-items-center">
				<h6 class="mb-0">
					<LocaleText t="Danger Zone"></LocaleText></h6>
				<button
					@click="confirmDelete = true"
					type="button"
					:class="{disabled: submitting}"
					class="btn bg-danger-subtle text-danger-emphasis border-danger-subtle rounded-3 ms-auto">
					<LocaleText t="Delete"></LocaleText>
				</button>
			</div>
		</template>
	</form>
</div>
</template>

<style scoped>

</style>