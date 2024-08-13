<script>
import {fetchPost} from "@/utilities/fetch.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

export default {
	name: "dashboardAPIKey",
	props: {
		apiKey: Object
	},
	setup(){
		const store = DashboardConfigurationStore();
		return {store};
	},
	data(){
		return {
			confirmDelete: false
		}
	},
	methods: {
		deleteAPIKey(){
			fetchPost(`${apiUrl}/deleteDashboardAPIKey`, {
				Key: this.apiKey.Key
			}, (res) => {
				if (res.status){
					this.$emit('deleted', res.data);
					this.store.newMessage("Server", "API Key deleted", "success");
				}else{
					this.store.newMessage("Server", res.message, "danger")
				}
			})
		}
	}
}
</script>

<template>
	<div class="card rounded-3 shadow-sm">
		<div class="card-body d-flex gap-3 align-items-center apiKey-card-body" v-if="!this.confirmDelete">
			<div class="d-flex align-items-center gap-2">
				<small class="text-muted">Key</small>
				<span style="word-break: break-all">{{this.apiKey.Key}}</span>
			</div>
			<div class="d-flex align-items-center gap-2 ms-auto">
				<small class="text-muted">Expire At</small>
				{{this.apiKey.ExpiredAt ? this.apiKey.ExpiredAt : 'Never'}}
			</div>
			<a role="button" class="btn btn-sm bg-danger-subtle text-danger-emphasis rounded-3"
			   v-if="!this.store.getActiveCrossServer()"
			   @click="this.confirmDelete = true">
				<i class="bi bi-trash-fill"></i>
			</a>
		</div>
		<div v-else class="card-body d-flex gap-3 align-items-center justify-content-end" 
		     v-if="!this.store.getActiveCrossServer()">
			Are you sure to delete this API key?
			<a role="button" class="btn btn-sm bg-success-subtle text-success-emphasis rounded-3"
				@click="this.deleteAPIKey()"
			>
				<i class="bi bi-check-lg"></i>
			</a>
			<a role="button" class="btn btn-sm bg-secondary-subtle text-secondary-emphasis rounded-3" 
			   @click="this.confirmDelete = false">
				<i class="bi bi-x-lg"></i>
			</a>
		</div>
	</div>
</template>

<style scoped>
@media screen and (max-width: 992px) {
	.apiKey-card-body{
		flex-direction: column !important;
		align-items: start !important;
		
		div.ms-auto{
			margin-left: 0 !important;
		}
		
		div{
			width: 100%;
			align-items: start !important;
		}
		
		small{
			margin-right: auto;
		}
	}
}
</style>