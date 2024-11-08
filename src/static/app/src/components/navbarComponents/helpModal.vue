<script setup>
import LocaleText from "@/components/text/localeText.vue";
import {onMounted, ref} from "vue";
import {fetchGet} from "@/utilities/fetch.js";

const discordLoading = ref(true)
const discord = ref(undefined)

onMounted(() => {
	discordLoading.value = true;
	fetch("https://discord.com/api/guilds/1276818723637956628/widget.json").then(res => res.json()).then(res => {
		discord.value = res;
		discordLoading.value = false;
	}).catch(() => {
		discordLoading.value = false;
	})
})
</script>

<template>
	<div class="peerSettingContainer w-100 h-100 position-absolute top-0 start-0 overflow-y-scroll">
		<div class="container d-flex h-100 w-100">
			<div class="m-auto modal-dialog-centered dashboardModal">
				<div class="card rounded-3 shadow flex-grow-1">
					<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4 pb-2">
						<h4 class="mb-0">
							<LocaleText t="Help"></LocaleText>
						</h4>
						<button type="button" class="btn-close ms-auto" @click="$emit('close')"></button>
					</div>
					<div class="card-body px-4 pb-4 d-flex flex-column gap-2">
						<a class="card text-decoration-none" target="_blank" role="button" href="https://discord.com/invite/ZkJSPAaQ">
							<div class="card-body d-flex gap-4 align-items-center">
								<h1 class="mb-0">
									<i class="bi bi-discord"></i>
								</h1>
								<div>
									<div class="d-flex align-items-center">
										<h5 class="mb-0">
											Discord Server
										</h5>
										<span class="badge rounded-pill text-bg-primary ms-2">
											<span v-if="discordLoading" class="spinner-border spinner-border-sm" style="width: 0.7rem; height: 0.7rem">
											</span>
											<span v-if="discord !== undefined && !discordLoading">
												<i class="bi bi-person-fill me-2"></i>{{discord.presence_count}} Online
											</span>
										</span>
									</div>
									<small class="text-muted">
										<LocaleText t="Join our Discord server for quick help or chat about WGDashboard!"></LocaleText>
									</small>
								</div>
							</div>
						</a>
						<a class="card text-decoration-none" href="https://donaldzou.github.io/WGDashboard-Documentation/" target="_blank">
							<div class="card-body d-flex gap-4 align-items-center">
								<h1 class="mb-0">
									<i class="bi bi-hash"></i>
								</h1>
								<div>
									<h5 class="mb-0">
										<LocaleText t="Official Documentation"></LocaleText>
									</h5>
									<small class="text-muted">
										<LocaleText t="Official documentation contains User Guides and more..."></LocaleText>
									</small>
								</div>
							</div>
						</a>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>