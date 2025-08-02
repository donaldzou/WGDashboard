<script setup lang="ts">
import LocaleText from "@/components/text/localeText.vue";
const props = defineProps(['mode'])
import { fetchGet } from "@/utilities/fetch.js"
await fetchGet("/api/oidc/status", {
	mode: "Client"
}, (res) => {
	console.log(res)
})

</script>

<template>
<div class="d-flex flex-column gap-2">
	<div class="d-flex align-items-center">
		<h6 class="mb-0">
			<LocaleText t="OpenID Connect (OIDC)"></LocaleText>
		</h6>
		<div class="form-check form-switch ms-auto">
			<label class="form-check-label" for="oidc_switch">
				<LocaleText t="Enable"></LocaleText>
			</label>
			<input class="form-check-input" type="checkbox" role="switch" id="oidc_switch">
		</div>
	</div>
	<div>
		<div class="alert alert-dark rounded-3 mb-0">
			<LocaleText t="Due to security reason, in order to edit OIDC configuration, you will need to edit "></LocaleText>
			<code>wg-dashboard-oidc-providers.json</code> directly. If you updated the file, click the update button below to reload the configuration.
		</div>
	</div>
	<button class="rounded-3 btn bg-success-subtle text-success-emphasis border-success-subtle">
		<i class="bi bi-arrow-clockwise me-2"></i><LocaleText t="Refresh"></LocaleText>
	</button>
</div>
</template>

<style scoped>

</style>