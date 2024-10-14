<script setup>
import {onMounted, reactive, ref} from "vue";
import {fetchGet} from "@/utilities/fetch.js";
import {useRoute} from "vue-router";
import dayjs from "dayjs";

const route = useRoute()
const backups = ref([])

onMounted(() => {
	fetchGet("/api/getWireguardConfigurationBackup", {
		configurationName: route.params.id
	}, (res) => {
		backups.value = res.data;
	})
})
</script>

<template>
<div class="card rounded-3" style="height: 400px; overflow-y: scroll">
	<div class="card-body d-flex gap-2 flex-column">
		<div class="card" v-for="b in backups">
			<div class="card-body p-2 px-3">
				<div class="d-flex gap-3 align-items-center">
					<div class="d-flex flex-column">
						<small class="text-muted">
							Filename
						</small>
						<small>
							{{b.filename}}
						</small>
					</div>
					<div class="d-flex flex-column">
						<small class="text-muted">
							Backup Date
						</small>
						<small>
							{{dayjs(b.backupDate, "YYYYMMDDHHmmss").format("YYYY-MM-DD HH:mm:ss")}}
						</small>
					</div>
					<div class="d-flex gap-2 align-items-center ms-auto">
						<button class="btn bg-info-subtle text-info-emphasis border-info-subtle rounded-3 btn-sm">
							<i class="bi bi-eye-fill"></i>
						</button>
						<button class="btn bg-warning-subtle text-warning-emphasis border-warning-subtle rounded-3 btn-sm">
							<i class="bi bi-clock-history"></i>
						</button>
						<button class="btn bg-danger-subtle text-danger-emphasis border-danger-subtle rounded-3 btn-sm">
							<i class="bi bi-trash-fill"></i>
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
</template>

<style scoped>

</style>