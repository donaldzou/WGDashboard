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
						value: "total_receive"
					},
					{
						display: "Total Sent",
						value: "total_sent"
					},
					{
						display: "Total Data",
						value: "total_data"
					},
					{
						display: "Date",
						value: "date"
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
	
}
</script>

<template>
	<div class="peerSettingContainer w-100 h-100 position-absolute top-0 start-0">
		<div class="container d-flex h-100 w-100">
			<div class="card m-auto rounded-3 shadow" style="width: 700px">
				<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4 pb-2">
					<h4 class="mb-0 fw-normal">Schedule Jobs
						<strong></strong>
					</h4>
					<button type="button" class="btn-close ms-auto" @click="this.$emit('close')"></button>
				</div>
				<div class="card-body px-4 pb-4 pt-0">
					<div class="d-flex">
						<small class="text-muted">
							Name
						</small>
						<small class="ms-auto">{{selectedPeer.name ? selectedPeer.name : "Untitled Peer"}}</small>
					</div>					
					<div class="mb-4 d-flex">
						<small class="text-muted">
							Public Key
						</small>
						<small class="ms-auto"><samp>{{this.selectedPeer.id}}</samp></small>
					</div>
					
					<SchedulePeerJob 
						:dropdowns="this.dropdowns" 
						:job="job" v-for="job in this.selectedPeer.jobs">
					</SchedulePeerJob>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>