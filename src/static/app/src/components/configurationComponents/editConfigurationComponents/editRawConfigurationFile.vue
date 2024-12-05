<script setup>

import LocaleText from "@/components/text/localeText.vue";

const emits = defineEmits(['close'])
</script>

<template>
	<div class="peerSettingContainer w-100 h-100 position-absolute top-0 start-0 overflow-y-scroll">
		<div class="container d-flex h-100 w-100">
			<div class="m-auto modal-dialog-centered dashboardModal" style="width: 700px">
				<div class="card rounded-3 shadow flex-grow-1" id="deleteConfigurationContainer">
					<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4 pb-0">
						<h5 class="mb-0">
							<LocaleText t="Are you sure to delete this configuration?"></LocaleText>
						</h5>
						<button type="button" class="btn-close ms-auto" @click="emits('close')"></button>
					</div>
					<div class="card-body px-4 text-muted"></div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>