<script setup>
import {onBeforeUnmount, onMounted, reactive, ref} from "vue";
import {fetchGet} from "@/utilities/fetch.js";
import {useRoute} from "vue-router";
import dayjs from "dayjs";
import LocaleText from "@/components/text/localeText.vue";

const route = useRoute()
const backups = ref([])
const loading = ref(false)
const emit = defineEmits(["close"])

onMounted(() => {
	loadBackup();
})

const loadBackup = () => {
	loading.value = true
	fetchGet("/api/getWireguardConfigurationBackup", {
		configurationName: route.params.id
	}, (res) => {
		backups.value = res.data;
		loading.value = false;
	})
}
</script>

<template>
<div class="peerSettingContainer w-100 h-100 position-absolute top-0 start-0 overflow-y-scroll" ref="editConfigurationContainer">
	<div class="d-flex h-100 w-100">
		<div class="modal-dialog-centered dashboardModal w-100 h-100 overflow-x-scroll flex-column gap-3 mx-3">
			<div class="my-5 d-flex gap-3 flex-column position-relative">
				<div class="title">
					<div class="d-flex mb-3">
						<h4 class="mb-0">
							<LocaleText t="Backup & Restore"></LocaleText>
						</h4>
						<button type="button" class="btn-close ms-auto" @click="$emit('close')"></button>
					</div>
					<button class="btn bg-primary-subtle text-primary-emphasis border-primary-subtle rounded-3 w-100">
						<i class="bi bi-plus-circle-fill me-2"></i> Create Backup
					</button>
				</div>
				
				<div class="position-relative d-flex gap-3 flex-column">
					<div class="text-center" v-if="loading">
						<div class="spinner-border"></div>
					</div>
					<div class="card animate__animated animate__fadeInUp animate__fast my-0 rounded-3" 
					     v-else-if="!loading && backups.length === 0">
						<div class="card-body text-center text-muted">
							<i class="bi bi-x-circle-fill me-2"></i> No backup yet, click the button above to create backup.
						</div>
					</div>
					<div class="card animate__animated animate__fadeInUp animate__fast my-0 rounded-3"
					     v-for="(b, index) in backups" :style="{'animation-delay': index*0.05 + 's'}">
						<div class="card-body">
							<div class="d-flex gap-3">
								<div class="d-flex flex-column">
									<small class="text-muted">
										Filename
									</small>
									<samp>{{b.filename}}</samp>
								</div>
								<div class="d-flex flex-column">
									<small class="text-muted">
										Backup Date
									</small>
									{{dayjs(b.backupDate, "YYYYMMDDHHmmss").format("YYYY-MM-DD HH:mm:ss")}}
								</div>
								<div class="d-flex gap-2 align-items-center ms-auto">
									<button class="btn bg-warning-subtle text-warning-emphasis border-warning-subtle rounded-3 btn-sm">
										<i class="bi bi-clock-history"></i>
									</button>
									<button class="btn bg-danger-subtle text-danger-emphasis border-danger-subtle rounded-3 btn-sm">
										<i class="bi bi-trash-fill"></i>
									</button>
								</div>
							</div>
							<hr>
							<textarea class="form-control rounded-3" :value="b.content"
							          disabled
							          style="height: 400px; font-family: var(--bs-font-monospace),sans-serif !important;"></textarea>
						</div>
					</div>
					
				</div>
			</div>

		</div>
	</div>
</div>
</template>

<style scoped>
.card, .title{
	width: 100%;
}

@media screen and (min-width: 700px) {
	.card, .title{
		width: 700px;
	}
}

.animate__fadeInUp{
	animation-timing-function: cubic-bezier(0.42, 0, 0.22, 1.0)
}
</style>