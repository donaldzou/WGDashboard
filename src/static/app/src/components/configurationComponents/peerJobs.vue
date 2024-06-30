<script>
import ScheduleDropdown from "@/components/configurationComponents/peerScheduleJobsComponents/scheduleDropdown.vue";
import SchedulePeerJob from "@/components/configurationComponents/peerScheduleJobsComponents/schedulePeerJob.vue";
export default {
	name: "peerJobs",
	
	props:{
		selectedPeer: Object
	},
	components:{
		SchedulePeerJob,
		ScheduleDropdown,
	},
	data(){
		return {
			dropdowns: {
				Field: [
					{
						display: "Total Received",
						value: "total_receive",
						unit: "GB",
						type: 'number'
					},
					{
						display: "Total Sent",
						value: "total_sent",
						unit: "GB",
						type: 'number'
					},
					{
						display: "Total Data",
						value: "total_data",
						unit: "GB",
						type: 'number'
					},
					{
						display: "Date",
						value: "date",
						type: 'date'
					}
				],
				Operator: [
					{
						display: "equal",
						value: "eq"
					},
					{
						display: "not equal",
						value: "neq"
					},
					{
						display: "larger than",
						value: "lgt"
					},
					{
						display: "less than",
						value: "lst"
					},
				],
				Action: [
					{
						display: "Restrict Peer",
						value: "restrict"
					},
					{
						display: "Delete Peer",
						value: "delete"
					}
				]
			},
		}
	},
	methods:{
		deleteJob(j){
			this.selectedPeer.jobs = this.selectedPeer.jobs.filter(x => x.JobID !== j.JobID)
		},
		addJob(){
			this.selectedPeer.jobs.unshift(JSON.parse(JSON.stringify({
				JobID: crypto.randomUUID(),
				Configuration: this.selectedPeer.configuration.Name,
				Peer: this.selectedPeer.id,
				Field: this.dropdowns.Field[0].value,
				Operator: this.dropdowns.Operator[0].value,
				Value: "",
				CreationDate: "",
				ExpireDate: "",
				Action: this.dropdowns.Action[0].value
			}))
			)
		}
	}
}
</script>

<template>
	<div class="peerSettingContainer w-100 h-100 position-absolute top-0 start-0 overflow-y-scroll">
		<div class="container d-flex h-100 w-100">
			<div class="m-auto modal-dialog-centered dashboardModal mt-0">
				<div class="card rounded-3 shadow" style="width: 700px">
					<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4 pb-2">
						<h4 class="mb-0 fw-normal">Schedule Jobs
							<strong></strong>
						</h4>
						<button type="button" class="btn-close ms-auto" @click="this.$emit('close')"></button>
					</div>
					<div class="card-body px-4 pb-4 pt-2 position-relative">
						<div class="d-flex align-items-center mb-3">
							<button class="btn btn-sm btn-primary rounded-3" @click="this.addJob()">
								<i class="bi bi-plus-lg me-2"></i> Job
							</button>
						</div>


						<TransitionGroup name="schedulePeerJobTransition" tag="div" class="position-relative">
							<SchedulePeerJob
								@refresh="(j) => job = j"
								@delete="this.deleteJob(job)"
								:dropdowns="this.dropdowns"
								:key="job.JobID"
								:pjob="job" v-for="(job) in this.selectedPeer.jobs">
							</SchedulePeerJob>
							
							<div class="card" key="none" v-if="this.selectedPeer.jobs.length === 0">
								<div class="card-body text-muted text-center">
									<h1><i class="bi bi-emoji-frown-fill"></i></h1>
									<h6 class="mb-0">This peer does not have any job yet.</h6>
								</div>
							</div>
						</TransitionGroup>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
.schedulePeerJobTransition-move, /* apply transition to moving elements */
.schedulePeerJobTransition-enter-active,
.schedulePeerJobTransition-leave-active {
	transition: all 0.4s cubic-bezier(0.82, 0.58, 0.17, 0.9);
}

.schedulePeerJobTransition-enter-from,
.schedulePeerJobTransition-leave-to {
	opacity: 0;
	transform: scale(0.9);
}

/* ensure leaving items are taken out of layout flow so that moving
   animations can be calculated correctly. */
.schedulePeerJobTransition-leave-active {
	position: absolute;
	width: 100%;
}
</style>