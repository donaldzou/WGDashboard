<script>
import ScheduleDropdown from "@/components/configurationComponents/peerScheduleJobsComponents/scheduleDropdown.vue";

export default {
	name: "schedulePeerJob",
	components: {ScheduleDropdown},
	props: {
		dropdowns: Array[Object],
		pjob: Object
	},
	data(){
		return {
			job: Object,
			inputType: undefined,
			edit: false
		}
	},
	beforeMount() {
		this.job = JSON.parse(JSON.stringify(this.pjob))
	},
	methods: {
		save(){
			if (this.job.Field && this.job.Operator && this.job.Action && this.job.Value){
				if (this.job.Field === 'date'){
					this.job.Value = new Date(this.job.Value).getTime();
				}
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
			this.job = JSON.parse(JSON.stringify(this.pjob));
			this.edit = false;
		}
	},
}
</script>

<template>
	<div class="card shadow-sm rounded-3">
		<div class="card-header bg-transparent text-muted border-0">
			<small class="d-flex">
				<strong class="me-auto">Job ID</strong>
				<samp>{{this.job.JobID}}</samp>
			</small>
		</div>
		<div class="card-body pt-1" style="font-family: var(--bs-font-monospace)">
			<div class="d-flex gap-3 align-items-center mb-2">
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
					{{this.dropdowns.Field.find(x => x.value === this.job.Field).unit}} {
				</samp>
			</div>
			<div class="px-5 d-flex gap-3 align-items-center">
				<samp>execute</samp>
				<ScheduleDropdown
					:edit="edit"
					:options="this.dropdowns.Action"
					:data="this.job.Action"
					@update="(value) => this.job.Action = value"
				></ScheduleDropdown>
				<samp>;</samp>
			</div>
			<div class="d-flex gap-3">
				<samp>}</samp>
				<div class="ms-auto d-flex gap-3" v-if="!this.edit">
					<a role="button"
					   class="ms-auto text-decoration-none"
					   @click="this.edit = true">[E] Edit</a>
					<a role="button"
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

</style>