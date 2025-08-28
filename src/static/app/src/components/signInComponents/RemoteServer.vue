<script>
import dayjs from "dayjs";
import {GetLocale} from "@/utilities/locale.js";
import LocaleText from "@/components/text/localeText.vue";
import {v4} from "uuid";

export default {
	name: "RemoteServer",
	components: {LocaleText},
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
		addHeaders(){
			if (!this.server.headers){
				this.server.headers = {}
			}
			this.server.headers[v4().toString()] = {
				key: "",
				value: ""
			}
		},
		async handshake(){
			this.active = false;
			if (this.server.host && this.server.apiKey){
				this.refreshing = true;
				this.startTime = undefined;
				this.endTime = undefined;
				this.startTime = dayjs()
				await fetch(`${this.server.host}/api/handshake`, {
					headers: this.getHeaders,
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
				headers:  this.getHeaders,
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
					return GetLocale(`Pinging...`)
				}
				return this.errorMsg ? this.errorMsg : "N/A"
			}
		},
		getHeaders(){
			let headers = {
				'Content-Type': 'application/json',
				'wg-dashboard-apikey': this.server.apiKey
			}
			if (this.server.headers){
				for (let header of Object.values(this.server.headers)){
					if (header.key && header.value && !Object.keys(headers).includes(header.key)){
						headers[header.key] = header.value
					}
				}
			}
			return headers
		}
	}
}
</script>

<template>
	<div class="card rounded-3">
		<div class="card-header " :class="[this.active ? 'text-bg-success':'text-bg-danger']">
			<div class="gap-2 d-flex align-items-center">
				<i class="bi bi-person-walking"></i>
				<small>{{this.getHandshakeTime}}</small>

				<div class="spin ms-auto text-white" v-if="this.refreshing">
					<i class="bi bi-arrow-clockwise"></i>
				</div>
				<a role="button"
				   v-else
				   @click="this.handshake()"
				   class="text-white text-decoration-none ms-auto disabled">
					<i class="bi bi-arrow-clockwise me"></i>
				</a>
			</div>
		</div>
		<div class="card-body">
			<div class="d-flex gap-2 w-100 remoteServerContainer flex-column">
				<div class="d-flex gap-3 align-items-center flex-grow-1">
					<small>
						<i class="bi bi-hdd-rack-fill"></i>
					</small>
					<input class="form-control form-control-sm rounded-3"
					       @blur="this.handshake()"
					       v-model="this.server.host"
					       type="url">
				</div>
				<div class="d-flex gap-3 align-items-center flex-grow-1">
					<i class="bi bi-key-fill"></i>
					<input class="form-control form-control-sm rounded-3 font-monospace"
					       @blur="this.handshake()"
					       v-model="this.server.apiKey"
					       type="text">
				</div>
				<div class="d-flex gap-2 button-group">
					<button
						style="flex: 1 0 0"
						@click="this.$emit('delete')"
						class="ms-auto btn btn-sm bg-danger-subtle text-danger-emphasis border-1 border-danger-subtle rounded-3">
						<i class="bi bi-trash me-2"></i><LocaleText t="Delete"></LocaleText>
					</button>

					<button
						style="flex: 1 0 0"
						@click="this.connect()"
						:class="{disabled: !this.active}"
						class="ms-auto btn btn-sm bg-success-subtle text-success-emphasis border-1 border-success-subtle rounded-3">
						<i class="bi bi-arrow-right-circle me-2"></i><LocaleText t="Connect"></LocaleText>
					</button>
				</div>

				<div class="card rounded-3">
					<div class="card-body d-flex gap-2 flex-column">
						<button
							style="flex: 1 0 0"
							@click="addHeaders()"
							class="btn btn-sm bg-primary-subtle text-primary-emphasis border-1 border-primary-subtle rounded-3">
							<i class="bi bi-plus-lg me-2"></i><LocaleText t="Headers"></LocaleText>
						</button>
						<div class="d-flex gap-2" v-for="(header, headerKey) in this.server.headers" v-if="this.server.headers">
							<div class="flex-grow-1">
								<input class="form-control rounded-3 form-control-sm"
									   @blur="this.handshake()"
									   v-model="header.key"
									   placeholder="Key">
							</div>
							<div class="flex-grow-1">
								<input class="form-control rounded-3 form-control-sm"
									   @blur="this.handshake()"
									   v-model="header.value"
									   placeholder="Value">
							</div>
							<button
								type="button"
								@click="delete this.server.headers[headerKey]"
								class="btn btn-sm bg-danger-subtle text-danger-emphasis border-danger-subtle rounded-3">
								<i class="bi bi-trash-fill"></i>
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
	.card-header{
		transition: all 0.2s ease-in-out;
	}
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