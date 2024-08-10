<script>
import dayjs from "dayjs";

export default {
	name: "RemoteServer",
	props: {
		server: Object
	},
	data(){
		return{
			active: false,
			startTime: undefined,
			endTime: undefined
		}
	},
	methods: {
		handshake(){
			this.startTime = undefined;
			this.endTime = undefined;
			
			this.startTime = dayjs()
			fetch(`//${this.server.host}/api/handshake`, {
				headers: {
					"content-type": "application/json",
					"wg-dashboard-apikey": this.server.apiKey
				},
				method: "GET",
				signal: AbortSignal.timeout(5000)
			}).then(res => res.json()).then(res => {
				this.active = true;
				this.endTime = dayjs()
			}).catch((res) => {
				console.log(res)
			})
		}
	},
	
	mounted() {
		this.handshake()	
	},
	computed: {
		getHandshakeTime(){
			if (this.startTime && this.endTime){
				return dayjs().subtract(this.startTime).millisecond()
			}else{
				return "N/A"
			}
		}
	}
}
</script>

<template>
	<div class="card rounded-3">
		<div class="card-body">
			<div class="d-flex gap-3 w-100">
				<div class="d-flex gap-3 align-items-center flex-grow-1">
					<i class="bi bi-server"></i>
					<input class="form-control form-control-sm" 
					       v-model="this.server.host"
					       type="url">
				</div>
				<div class="d-flex gap-3 align-items-center flex-grow-1">
					<i class="bi bi-key-fill"></i>
					<input class="form-control form-control-sm" 
					       v-model="this.server.apiKey"
					       type="text">
				</div>
				<div class="d-flex gap-2">
					<button 
						@click="this.$emit('delete')"
						class="ms-auto btn btn-sm bg-danger-subtle text-danger-emphasis border-1 border-danger-subtle">
						<i class="bi bi-trash"></i>
					</button>
					<button class="ms-auto btn btn-sm bg-success-subtle text-success-emphasis border-1 border-success-subtle">
						<i class="bi bi-arrow-right-circle"></i>
					</button>
				</div>
			</div>
		</div>
		<div class="card-footer gap-2 d-flex align-items-center">
			<span class="dot ms-0 me-2" :class="[this.active ? 'active':'inactive']"></span>
			{{this.getHandshakeTime}}
		</div>
	</div>
</template>

<style scoped>
	.dot.inactive{
		background-color: #dc3545;
		box-shadow: 0 0 0 0.2rem #dc354545;
	}
</style>