<script setup>
import {onMounted, ref} from "vue";
import dayjs from "dayjs";

const props = defineProps({
	configurationName: String,
	backups: Array,
	open: false,
	selectedConfigurationBackup: Object
})

const emit = defineEmits(["select"])
const showBackups = ref(props.open)



onMounted(() => {
	if (props.selectedConfigurationBackup){
		document.querySelector(`#${props.selectedConfigurationBackup.filename.replace('.conf', '')}`).scrollIntoView({
			behavior: "smooth"
		})
	}
	
})

</script>

<template>
	<div class="card rounded-3 shadow-sm">
		<a role="button" class="card-body d-flex align-items-center text-decoration-none" @click="showBackups = !showBackups">
			<div class="d-flex gap-3 align-items-center">
				<h6 class="mb-0">
					<samp>
						{{configurationName}}
					</samp>
				</h6>
				<small class="text-muted">
					{{backups.length}} {{backups.length > 1 ? "Backups": "Backup" }}
				</small>
			</div>
			<h5 class="ms-auto mb-0 dropdownIcon text-muted" :class="{active: showBackups}">
				<i class="bi bi-chevron-down"></i>
			</h5>
		</a>
		<div class="card-footer p-3 d-flex flex-column gap-2" v-if="showBackups">
			<div class="card rounded-3 shadow-sm animate__animated"
			     :key="b.filename"
			     @click="() => {emit('select', b)}"
			     :id="b.filename.replace('.conf', '')"
			     role="button" v-for="b in backups">
				<div class="card-body d-flex p-3 gap-3 align-items-center">
					<small>
						<i class="bi bi-file-earmark me-2"></i>
						<samp>{{b.filename}}</samp>
					</small>
					<small>
						<i class="bi bi-clock-history me-2"></i>
						<samp>{{dayjs(b.backupDate).format("YYYY-MM-DD HH:mm:ss")}}</samp>
					</small>
					<small >
						<i class="bi bi-database me-2"></i>
						{{b.database? "Yes" : "No" }}
					</small>
					<small class="text-muted ms-auto">
						<i class="bi bi-chevron-right"></i>
					</small>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
	.dropdownIcon{
		transition: all 0.2s ease-in-out;
	}
	.dropdownIcon.active{
		transform: rotate(180deg);
	}
</style>