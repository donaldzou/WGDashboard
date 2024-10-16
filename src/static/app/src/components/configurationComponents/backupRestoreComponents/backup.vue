<script setup>
import dayjs from "dayjs";
import {computed, ref} from "vue";
import {fetchPost} from "@/utilities/fetch.js";
import {useRoute} from "vue-router";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
const props = defineProps(["b", "delay"])
const deleteConfirmation = ref(false)
const restoreConfirmation = ref(false)
const route = useRoute()
const emit = defineEmits(["refresh", "refreshPeersList"])
const store = DashboardConfigurationStore()
const loading = ref(false);
const deleteBackup = () => {
	loading.value = true;
	fetchPost("/api/deleteWireguardConfigurationBackup", {
		configurationName: route.params.id,
		backupFileName: props.b.filename
	}, (res) => {
		loading.value = false;
		if (res.status){
			emit("refresh")
			store.newMessage("Server", "Backup deleted", "success")
		}else{
			store.newMessage("Server", "Backup failed to delete", "danger")
		}
	})
}

const restoreBackup = () => {
	loading.value = true;
	fetchPost("/api/restoreWireguardConfigurationBackup", {
		configurationName: route.params.id,
		backupFileName: props.b.filename
	}, (res) => {
		loading.value = false;
		restoreConfirmation.value = false;
		if (res.status){
			emit("refresh")
			store.newMessage("Server", "Backup restored with " + props.b.filename, "success")
		}else{
			store.newMessage("Server", "Backup failed to restore", "danger")
		}
	})
}

const delaySeconds = computed(() => {
	return props.delay + 's'
})
</script>
 
<template>
	<div class="card my-0 rounded-3">
		<div class="card-body position-relative">
			<Transition name="zoomReversed">
				<div 
					v-if="deleteConfirmation"
					class="position-absolute w-100 h-100 confirmationContainer start-0 top-0 rounded-3 d-flex p-2">
					<div class="m-auto">
						<h5>Are you sure to delete this backup?</h5>
						<div class="d-flex gap-2 align-items-center justify-content-center">
							<button class="btn btn-danger rounded-3" 
							        :disabled="loading"
							        @click='deleteBackup()'>
								Yes
							</button>
							<button
								@click="deleteConfirmation = false"
								:disabled="loading"
								class="btn bg-secondary-subtle text-secondary-emphasis border-secondary-subtle rounded-3">
								No
							</button>
						</div>
					</div>
				</div>
			</Transition>
			<Transition name="zoomReversed">
				<div
					v-if="restoreConfirmation"
					class="position-absolute w-100 h-100 confirmationContainer start-0 top-0 rounded-3 d-flex p-2">
					<div class="m-auto">
						<h5>Are you sure to restore this backup?</h5>
						<div class="d-flex gap-2 align-items-center justify-content-center">
							<button
								:disabled="loading"
								@click="restoreBackup()"
								class="btn btn-success rounded-3">
								Yes
							</button>
							<button
								@click="restoreConfirmation = false"
								:disabled="loading"
								class="btn bg-secondary-subtle text-secondary-emphasis border-secondary-subtle rounded-3">
								No
							</button>
						</div>
					</div>
				</div>
			</Transition>
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
					<button 
						@click="restoreConfirmation = true"
						class="btn bg-warning-subtle text-warning-emphasis border-warning-subtle rounded-3 btn-sm">
						<i class="bi bi-clock-history"></i>
					</button>
					<button 
						@click="deleteConfirmation = true"
						class="btn bg-danger-subtle text-danger-emphasis border-danger-subtle rounded-3 btn-sm">
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
</template>

<style scoped>
.confirmationContainer{
	background-color: rgba(0, 0, 0, 0.53);
	z-index: 9999;
	backdrop-filter: blur(1px);
	-webkit-backdrop-filter: blur(1px);
}

.list1-enter-active{
	transition-delay: v-bind(delaySeconds) !important;
}
</style>