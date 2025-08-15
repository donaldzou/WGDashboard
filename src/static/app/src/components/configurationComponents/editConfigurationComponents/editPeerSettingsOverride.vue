<script setup lang="ts">
import LocaleText from "@/components/text/localeText.vue";
import { fetchPost } from "@/utilities/fetch.js"
import {onMounted, reactive, ref} from "vue";
const props = defineProps(['configuration'])
const saving = ref(false)
const overridePeerSettings = ref({...props.configuration.Info.OverridePeerSettings})
const edited = ref(false)

onMounted(() => {
	document.querySelectorAll("#editPeerSettingsOverride input").forEach(
		x => x.addEventListener("change", () => {
			edited.value = true
		})
	)
})

const resetForm = () => {
	overridePeerSettings.value = props.configuration.Info.OverridePeerSettings
	edited.value = false
}

const submitForm = async () => {
	await fetchPost("/api/updateWireguardConfigurationInfo", {
		Name: props.configuration.Name,
		Key: "OverridePeerSettings",
		Value: overridePeerSettings.value
	}, (res) => {
		if (res.status){
			props.configuration.Info.OverridePeerSettings = overridePeerSettings.value
		}
	})
}
</script>

<template>
<div id="editPeerSettingsOverride">
	<h5 class="mb-0">
		<LocaleText t="Override Peer Settings"></LocaleText>
	</h5>
	<h6 class="mb-3 text-muted">
		<small>
			<LocaleText t="Only apply to peers in this configuration"></LocaleText>
		</small>
	</h6>
	<div class="d-flex gap-2 flex-column">
		<div>
			<label for="override_dns" class="form-label">
				<small class="text-muted">
					<LocaleText t="DNS"></LocaleText>
				</small>
			</label>
			<input type="text" class="form-control form-control-sm rounded-3"
				   :disabled="saving"
				   v-model="overridePeerSettings.DNS"
				   id="override_dns">
		</div>
		<div>
			<label for="override_endpoint_allowed_ips" class="form-label">
				<small class="text-muted">
					<LocaleText t="Endpoint Allowed IPs"></LocaleText>
				</small>
			</label>
			<input type="text" class="form-control form-control-sm rounded-3"
				   :disabled="saving"
				   v-model="overridePeerSettings.EndpointAllowedIPs"
				   id="override_endpoint_allowed_ips">
		</div>
		<div>
			<label for="override_listen_port" class="form-label">
				<small class="text-muted">
					<LocaleText t="Listen Port"></LocaleText>
				</small>
			</label>
			<input type="text" class="form-control form-control-sm rounded-3"
				   :disabled="saving"
				   v-model="overridePeerSettings.ListenPort"
				   id="override_listen_port">
		</div>
		<div>
			<label for="override_mtu" class="form-label">
				<small class="text-muted">
					<LocaleText t="MTU"></LocaleText>
				</small>
			</label>
			<input type="text"
				   class="form-control form-control-sm rounded-3"
				   :disabled="saving"
				   v-model="overridePeerSettings.MTU"
				   id="override_mtu">
		</div>
		<div>
			<label for="override_peer_remote_endpoint" class="form-label">
				<small class="text-muted">
					<LocaleText t="Peer Remote Endpoint"></LocaleText>
				</small>
			</label>
			<input type="text" class="form-control form-control-sm rounded-3"
				   :disabled="saving"
				   v-model="overridePeerSettings.PeerRemoteEndpoint"
				   id="override_peer_remote_endpoint">
		</div>
		<div>
			<label for="override_persistent_keepalive" class="form-label">
				<small class="text-muted">
					<LocaleText t="Persistent Keepalive"></LocaleText>
				</small>
			</label>
			<input type="text" class="form-control form-control-sm rounded-3"
				   :disabled="saving"
				   v-model="overridePeerSettings.PersistentKeepalive"
				   id="override_persistent_keepalive">
		</div>
		<div class="d-flex mt-1 gap-2">
			<button
				:class="{disabled: !edited}"
				@click="resetForm()"
				class="btn btn-sm bg-secondary-subtle border-secondary-subtle text-secondary-emphasis rounded-3 shadow ms-auto">
				<i class="bi bi-arrow-clockwise me-2"></i>
				<LocaleText t="Reset"></LocaleText>
			</button>
			<button
				:class="{disabled: !edited}"
				@click="submitForm()"
				class="btn btn-sm bg-primary-subtle border-primary-subtle text-primary-emphasis rounded-3 shadow">
				<i class="bi bi-save-fill me-2"></i>
				<LocaleText t="Save"></LocaleText>
			</button>
		</div>
	</div>
</div>
</template>

<style scoped>

</style>