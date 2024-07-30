<script>
import dayjs from "dayjs";
import {fetchPost} from "@/utilities/fetch.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

export default {
	name: "newDashboardAPIKey",
	data(){
		return{
			newKeyData:{
				ExpiredAt: dayjs().add(1, 'd').format("YYYY-MM-DDTHH:mm:ss"),
				neverExpire: false
			},
			submitting: false
		}
	},
	setup(){
		const store = DashboardConfigurationStore();
		return {store};
	},
	mounted() {
		console.log(this.newKeyData.ExpiredAt)
	},
	
	methods: {
		submitNewAPIKey(){
			this.submitting = true;
			fetchPost('/api/newDashboardAPIKey', this.newKeyData, (res) => {
				if (res.status){
					this.$emit('created', res.data);
					this.store.newMessage("Server", "New API Key created", "success");
					this.$emit('close')
				}else{
					this.store.newMessage("Server", res.message, "danger")
				}
				this.submitting = false;
			})
		},
		fixDate(date){
			console.log(dayjs(date).format("YYYY-MM-DDTHH:mm:ss"))
			return dayjs(date).format("YYYY-MM-DDTHH:mm:ss")
		}
	}
}
</script>

<template>
	<div class="position-absolute w-100 h-100 top-0 start-0 rounded-bottom-3 p-3 d-flex"
	     style="background-color: #00000060; backdrop-filter: blur(3px)">
		<div class="card m-auto rounded-3 mt-5">
			<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4 pb-0">
				Create API Key
				<button type="button" class="btn-close ms-auto" @click="this.$emit('close')"></button>
			</div>
			<div class="card-body d-flex gap-2 p-4 flex-column">
				<small class="text-muted">When should this API Key expire?</small>
				<div class="d-flex align-items-center gap-2">
					<input class="form-control" type="datetime-local"
					       @change="this.newKeyData.ExpiredAt = this.fixDate(this.newKeyData.ExpiredAt)"
					       :disabled="this.newKeyData.neverExpire || this.submitting"
					       v-model="this.newKeyData.ExpiredAt">
				</div>
				<div class="form-check">
					<input class="form-check-input" type="checkbox"
					       v-model="this.newKeyData.neverExpire" id="neverExpire" :disabled="this.submitting">
					<label class="form-check-label" for="neverExpire">
						Never Expire (<i class="bi bi-emoji-grimace-fill"></i> Don't think that's a good idea)
					</label>
				</div>
				<button class="ms-auto btn bg-success-subtle text-success-emphasis border-1 border-success-subtle rounded-3 shadow-sm"
					:class="{disabled: this.submitting}"
				        @click="this.submitNewAPIKey()"
				>
					<i class="bi bi-check-lg me-2" v-if="!this.submitting"></i>
					{{this.submitting ? 'Creating...':'Done'}}
				</button>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>