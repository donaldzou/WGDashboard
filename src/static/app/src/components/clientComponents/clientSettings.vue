<script setup lang="ts">
import LocaleText from "@/components/text/localeText.vue";
const emits = defineEmits(['close'])

</script>

<template>
<div class="position-absolute w-100 h-100 top-0 start-0 z-1 rounded-3 d-flex p-2" style="background-color: #00000070;">
	<div class="card m-auto rounded-3" style="width: 700px">
		<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4 pb-2">
			<h4 class="mb-0">
				<LocaleText t="Clients Settings"></LocaleText>
			</h4>
			<button type="button" class="btn-close ms-auto" @click="emits('close')"></button>
		</div>
		<div class="card-body px-4">
			<div class="py-2">
				<h6>
					<LocaleText t="OpenID Connect (OIDC)"></LocaleText>
				</h6>
				<hr>
				<div class="form-check form-switch">
					<label class="form-check-label" for="oidc_switch">
						<LocaleText t="Enable"></LocaleText>
					</label>
					<input class="form-check-input" type="checkbox" role="switch" id="oidc_switch">
				</div>
			</div>
		</div>
	</div>
</div>
</template>

<style scoped>

</style>