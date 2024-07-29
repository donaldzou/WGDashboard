<script>
import ScheduleDropdown from "@/components/configurationComponents/peerScheduleJobsComponents/scheduleDropdown.vue";
import {ref} from "vue";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {fetchPost} from "@/utilities/fetch.js";

export default {
	name: "schedulePeerJob",
	components: {ScheduleDropdown},
	props: {
		dropdowns: Array[Object],
		pjob: Object,
		viewOnly: false
	},
	setup(props){
		const job = ref({})
		const edit = ref(false)
		const newJob = ref(false)
		job.value = JSON.parse(JSON.stringify(props.pjob))
		if (!job.value.CreationDate){
			edit.value = true
			newJob.value = true
		}
		const store = DashboardConfigurationStore()
		return {job, edit, newJob, store}
	},
	data(){
		return {
			inputType: undefined,
		}
	},
	watch:{
		pjob: {
			deep: true,
			immediate: true,
			handler(newValue){
				if (!this.edit){
					this.job = JSON.parse(JSON.stringify(newValue))
				}
			}
		}	
	},
	methods: {
		save(){
			if (this.job.Field && this.job.Operator && this.job.Action && this.job.Value){
				fetchPost(`/api/savePeerScheduleJob/`, {
					Job: this.job
				}, (res) => {
					if (res.status){
						this.edit = false;
						this.store.newMessage("Server", "Job Saved!", "success")
						console.log(res.data)
						this.$emit("refresh", res.data[0])
						this.newJob = false;
					}else{
						this.store.newMessage("Server", res.message, "danger")
					}
				})
			}else{
				this.alert();
			}
		},
		alert(){
			let animation = "animate__flash";
			let dropdowns = this.$el.querySelectorAll(".scheduleDropdown");
			let inputs = this.$el.querySelectorAll("input");
			dropdowns.forEach(x => x.classList.add("animate__animated", animation))
			inputs.forEach(x => x.classList.add("animate__animated", animation))
			setTimeout(() => {
				dropdowns.forEach(x => x.classList.remove("animate__animated", animation))
				inputs.forEach(x => x.classList.remove("animate__animated", animation))
			}, 2000)
		},
		reset(){
			if(this.job.CreationDate){
				this.job = JSON.parse(JSON.stringify(this.pjob));
				this.edit = false;
			}else{
				this.$emit('delete')
			}
		},
		delete(){
			if(this.job.CreationDate){
				fetchPost(`/api/deletePeerScheduleJob/`, {
					Job: this.job
				}, (res) => {
					if (!res.status){
						this.store.newMessage("Server", res.message, "danger")
						this.$emit('delete')
					}else{
						this.store.newMessage("Server", "Job Deleted!", "success")
					}
					
				})
			}
			this.$emit('delete')
		}
	},
}
</script>

<template>
	<div class="card shadow-sm rounded-3 mb-2" :class="{'border-warning-subtle': this.newJob}">
		<div class="card-header bg-transparent text-muted border-0">
			<small class="d-flex" v-if="!this.newJob">
				<strong class="me-auto">Job ID</strong>
				<samp>{{this.job.JobID}}</samp>
			</small>
			<small v-else><span class="badge text-bg-warning">Unsaved Job</span></small>
		</div>
		<div class="card-body pt-1" style="font-family: var(--bs-font-monospace)">
			<div class="d-flex gap-2 align-items-center mb-2">
				<samp>
					if
				</samp>
				<ScheduleDropdown
					:edit="edit"
					:options="this.dropdowns.Field"
					:data="this.job.Field"
					@update="(value) => {this.job.Field = value}"
				></ScheduleDropdown>
				<samp>
					is
				</samp>
				<ScheduleDropdown
					:edit="edit"
					:options="this.dropdowns.Operator"
					:data="this.job.Operator"
					@update="(value) => this.job.Operator = value"
				></ScheduleDropdown>
				<input class="form-control form-control-sm form-control-dark rounded-3 flex-grow-1"
				       :disabled="!edit"
				       type="datetime-local"
				       v-if="this.job.Field === 'date'"
				       v-model="this.job.Value"
				       style="width: auto">
				<input class="form-control form-control-sm form-control-dark rounded-3 flex-grow-1" 
				       :disabled="!edit"
				       v-else
				       v-model="this.job.Value"
				       style="width: auto">
				<samp>
					{{this.dropdowns.Field.find(x => x.value === this.job.Field)?.unit}} {
				</samp>
			</div>
			<div class="px-5 d-flex gap-2 align-items-center">
				<samp>then</samp>
				<ScheduleDropdown
					:edit="edit"
					:options="this.dropdowns.Action"
					:data="this.job.Action"
					@update="(value) => this.job.Action = value"
				></ScheduleDropdown>
			</div>
			<div class="d-flex gap-3">
				<samp>}</samp>
				<div class="ms-auto d-flex gap-3" v-if="!this.edit">
					<a role="button"
					   class="ms-auto text-decoration-none"
					   @click="this.edit = true">[E] Edit</a>
					<a role="button"
					   @click="this.delete()"
					   class=" text-danger text-decoration-none">[D] Delete</a>
				</div>
				<div class="ms-auto d-flex gap-3" v-else>
					<a role="button"
					   class="text-secondary text-decoration-none"
					   @click="this.reset()">[C] Cancel</a>
					<a role="button"
					   class="text-primary ms-auto text-decoration-none"
					   @click="this.save()">[S] Save</a>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
*{
	font-size: 0.875rem;
}

input{
	padding: 0.1rem 0.4rem;
}
input:disabled{
	border-color: transparent;
	background-color: rgba(13, 110, 253, 0.09);
	color: #0d6efd;
}
</style>