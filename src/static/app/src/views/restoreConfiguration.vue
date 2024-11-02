<script setup>
import LocaleText from "@/components/text/localeText.vue";
import {onMounted, reactive, ref, watch} from "vue";
import {fetchGet} from "@/utilities/fetch.js";
import BackupGroup from "@/components/restoreConfigurationComponents/backupGroup.vue";
import ConfirmBackup from "@/components/restoreConfigurationComponents/confirmBackup.vue";
const backups = ref(undefined)
onMounted(() => {
	fetchGet("/api/getAllWireguardConfigurationBackup", {}, (res) => {
		backups.value = res.data
	})
})
const confirm = ref(false)
const selectedConfigurationBackup = ref(undefined)
const selectedConfiguration = ref("")
</script>

<template>
	<div class="mt-5 text-body">
		<div class="container mb-4">
			<div class="mb-5 d-flex align-items-center gap-4">
				<RouterLink to="/"
				            class="btn btn-dark btn-brand p-2 shadow" style="border-radius: 100%">
					<h2 class="mb-0" style="line-height: 0">
						<i class="bi bi-arrow-left-circle"></i>
					</h2>
				</RouterLink>
				<h2 class="mb-0">
					<LocaleText t="Restore Configuration"></LocaleText>
				</h2>
			</div>
			<div v-if="backups" >
				<div class="d-flex mb-5 align-items-center steps" role="button"
				     :class="{active: !confirm}"
				     @click="confirm = false" key="step1">
					<div class=" d-flex text-decoration-none text-body flex-grow-1 align-items-center gap-3"
					     
					>
						<h1 class="mb-0"
						    style="line-height: 0">
							<i class="bi bi-1-circle-fill"></i>
						</h1>
						<div>
							<h4 class="mb-0">
								<LocaleText t="Step 1"></LocaleText>
							</h4>
							<small class="text-muted">
								<LocaleText t="Select a backup you want to restore" v-if="!confirm"></LocaleText>
								<LocaleText t="Click to change a backup" v-else></LocaleText>
							</small>
						</div>
					</div>
					<Transition name="zoomReversed">
						<div class="ms-sm-auto" v-if="confirm">
							<small class="text-muted">
								<LocaleText t="Selected Backup"></LocaleText>
							</small>
							<h6>
								<samp>{{selectedConfigurationBackup.filename}}</samp>
							</h6>
						</div>
					</Transition>
				</div>
				<div id="step1Detail" v-if="!confirm">
					<div class="mb-4">
						<div class="d-flex gap-3 flex-column">
							<BackupGroup
								@select="(b) => {selectedConfigurationBackup = b; selectedConfiguration = c; confirm = true}"
								:selectedConfigurationBackup="selectedConfigurationBackup"
								:open="selectedConfiguration === c"
								v-for="c in Object.keys(backups.NonExistingConfigurations)"
								:configuration-name="c" :backups="backups.NonExistingConfigurations[c]"></BackupGroup>
							<div v-if="Object.keys(backups.NonExistingConfigurations).length === 0">
								<div class="card rounded-3">
									<div class="card-body">
										<p class="mb-0">
											<LocaleText t="You don't have any configuration to restore"></LocaleText>
										</p>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
				
				<div class="my-5" key="step2" id="step2">
					<div class="steps d-flex text-decoration-none text-body flex-grow-1 align-items-center gap-3"
					     :class="{active: confirm}"
					>
						<h1 class="mb-0"
						    style="line-height: 0">
							<i class="bi bi-2-circle-fill"></i>
						</h1>
						<div>
							<h4 class="mb-0">Step 2</h4>
							<small class="text-muted">
								<LocaleText t="Backup not selected" v-if="!confirm"></LocaleText>
								<LocaleText t="Confirm & edit restore information" v-else></LocaleText>
							</small>

						</div>
					</div>
				</div>
				<ConfirmBackup :selectedConfigurationBackup="selectedConfigurationBackup" v-if="confirm" key="confirm"></ConfirmBackup>
			</div>

			
			
		</div>
	</div>
</template>

<style scoped>
.steps{
	transition: all 0.3s ease-in-out;
	opacity: 0.3;
	
	&.active{
		opacity: 1;
	}
}
</style>