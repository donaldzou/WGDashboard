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
			endTime: undefined,
			errorMsg: "",
			refreshing: false
		}
	},
	methods: {
		async handshake(){
			this.active = false;
			this.refreshing = true;
			if (this.server.host && this.server.apiKey){
				this.startTime = undefined;
				this.endTime = undefined;
				this.startTime = dayjs()
				await fetch(`${this.server.host}/api/handshake`, {
					headers: {
						"content-type": "application/json",
						"wg-dashboard-apikey": this.server.apiKey
					},
					method: "GET",
					signal: AbortSignal.timeout(5000)
				}).then(res => {
					if (res.status === 200){
						return res.json()
					}
					throw new Error(res.statusText)
				}).then(() => {
					this.endTime = dayjs()
					this.active = true;
				}).catch((res) => {
					this.active = false;
					this.errorMsg = res;
				});
					
				this.refreshing = false;
			}
		},
		async connect(){
			await fetch(`${this.server.host}/api/authenticate`, {
				headers: {
					"content-type": "application/json",
					"wg-dashboard-apikey": this.server.apiKey
				},
				body: JSON.stringify({
					host: window.location.hostname
				}),
				method: "POST",
				signal: AbortSignal.timeout(5000),
			}).then(res => res.json()).then(res => {
				this.$emit("setActiveServer")
				this.$router.push('/')
			})
		}
	},
	mounted() {
		this.handshake()
	},
	computed: {
		getHandshakeTime(){
			if (this.startTime && this.endTime){
				return `${dayjs().subtract(this.startTime).millisecond()}ms`
			}else{
				if (this.refreshing){
					return `Pinging...`
				}
				return this.errorMsg ? this.errorMsg : "N/A"
			}
		}
	}
}
</script>

<template>
	<div class="card rounded-3">
		<div class="card-body">
			<div class="d-flex gap-3 w-100 remoteServerContainer">
				<div class="d-flex gap-3 align-items-center flex-grow-1">
					<i class="bi bi-server"></i>
					<input class="form-control form-control-sm"
					       @blur="this.handshake()"
					       v-model="this.server.host"
					       type="url">
				</div>
				<div class="d-flex gap-3 align-items-center flex-grow-1">
					<i class="bi bi-key-fill"></i>
					<input class="form-control form-control-sm"
					       @blur="this.handshake()"
					       v-model="this.server.apiKey"
					       type="text">
				</div>
				<div class="d-flex gap-2 button-group">
					<button 
						@click="this.$emit('delete')"
						class="ms-auto btn btn-sm bg-danger-subtle text-danger-emphasis border-1 border-danger-subtle">
						<i class="bi bi-trash"></i>
					</button>
					<button
						@click="this.connect()"
						:class="{disabled: !this.active}"
						class="ms-auto btn btn-sm bg-success-subtle text-success-emphasis border-1 border-success-subtle">
						<i class="bi bi-arrow-right-circle"></i>
					</button>
				</div>
			</div>
		</div>
		<div class="card-footer gap-2 d-flex align-items-center">
			<span class="dot ms-0 me-2" :class="[this.active ? 'active':'inactive']"></span>
			<small>{{this.getHandshakeTime}}</small>

			<div class="spin ms-auto text-primary-emphasis" v-if="this.refreshing">
				<i class="bi bi-arrow-clockwise"></i>
			</div>

			<a role="button"
			   v-else
			   @click="this.handshake()"

			   class="text-primary-emphasis text-decoration-none ms-auto disabled">
				<i class="bi bi-arrow-clockwise me"></i>
			</a>
		</div>
	</div>
</template>

<style scoped>
	.dot.inactive{
		background-color: #dc3545;
		box-shadow: 0 0 0 0.2rem #dc354545;
	}
	
	.spin{
		animation: spin 1s infinite cubic-bezier(0.82, 0.58, 0.17, 0.9);
	}
	
	@keyframes spin {
		0%{
			transform: rotate(0deg);
		}
		100%{
			transform: rotate(360deg);
		}
	}
	
	@media screen and (max-width: 768px) {
		.remoteServerContainer{
			flex-direction: column;
		}
		
		.remoteServerContainer .button-group button{
			width: 100%;
		}
	}
</style>