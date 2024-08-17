<script>
import {wgdashboardStore} from "@/stores/wgdashboardStore.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {fetchGet} from "@/utilities/fetch.js";

export default {
	name: "navbar",
	setup(){
		const wireguardConfigurationsStore = WireguardConfigurationsStore();
		const dashboardConfigurationStore = DashboardConfigurationStore();
		return {wireguardConfigurationsStore, dashboardConfigurationStore}
	},
	data(){
		return {
			updateAvailable: false,
			updateMessage: "Checking for update...",
			updateUrl: ""
		}
	},
	mounted() {
		fetchGet("/api/getDashboardUpdate", {}, (res) => {
			if (res.status){
				if (res.data){
					this.updateAvailable = true
					this.updateUrl = res.data
				}
				this.updateMessage = res.message
			}else{
				this.updateMessage = "Failed to check available update"
				console.log(`Failed to get update: ${res.message}`)
			}
		})
	}
}
</script>

<template>
	<div class="col-md-3 col-lg-2 d-md-block p-3 navbar-container"
	     :class="{active: this.dashboardConfigurationStore.ShowNavBar}"
	     :data-bs-theme="dashboardConfigurationStore.Configuration.Server.dashboard_theme"
	     style="height: calc(-50px + 100vh);">
		<nav id="sidebarMenu" class=" bg-body-tertiary sidebar border h-100 rounded-3 shadow overflow-y-scroll" >
			<div class="sidebar-sticky pt-3">
				<ul class="nav flex-column px-2">
					<li class="nav-item">
						<RouterLink class="nav-link rounded-3"
						            to="/" exact-active-class="active">
							<i class="bi bi-house me-2"></i>
							Home</RouterLink></li>
					<li class="nav-item">
						<RouterLink class="nav-link rounded-3" to="/settings" 
						            exact-active-class="active">
							<i class="bi bi-gear me-2"></i>
							Settings</RouterLink></li>
				</ul>
				<hr class="text-body">
				<h6 class="sidebar-heading px-3 mt-4 mb-1 text-muted text-center">
					<i class="bi bi-body-text me-2"></i>
					Configurations
				</h6>
				<ul class="nav flex-column px-2">
					<li class="nav-item">
						<RouterLink :to="'/configuration/'+c.Name + '/peers'" class="nav-link nav-conf-link rounded-3"
						            active-class="active"
						            v-for="c in this.wireguardConfigurationsStore.Configurations">
							<span class="dot me-2" :class="{active: c.Status}"></span>
							{{c.Name}}
						</RouterLink>
					</li>
				</ul>
				<hr class="text-body">
				<h6 class="sidebar-heading px-3 mt-4 mb-1 text-muted text-center">
					<i class="bi bi-tools me-2"></i>
					Tools
				</h6>
				<ul class="nav flex-column px-2">
					<li class="nav-item">
						<RouterLink to="/ping" class="nav-link rounded-3" active-class="active">Ping</RouterLink></li>
					<li class="nav-item">
						<RouterLink to="/traceroute" class="nav-link rounded-3" active-class="active">Traceroute</RouterLink>
					</li>
				</ul>
				<hr class="text-body">
				<ul class="nav flex-column px-2">
					<li class="nav-item"><a class="nav-link text-danger rounded-3" 
					                        @click="this.dashboardConfigurationStore.signOut()" 
					                        role="button" style="font-weight: bold">
						<i class="bi bi-box-arrow-left me-2"></i>
						Sign Out</a>
					</li>
					<li class="nav-item" style="font-size: 0.8rem">
						<a :href="this.updateUrl" v-if="this.updateAvailable" class="text-decoration-none" target="_blank">
							<small class="nav-link text-muted rounded-3" >
								{{ this.updateMessage }}
							</small>
						</a>
						<small class="nav-link text-muted" v-else>
							{{ this.updateMessage }}
						</small>
					</li>
				</ul>
				
			</div>
		</nav>
	</div>
	
	
</template>

<style scoped>
@media screen and (max-width: 768px) {
	.navbar-container{
		position: absolute;
		z-index: 1000;
		animation-duration: 0.4s;
		animation-fill-mode: both;
		display: none;
		animation-timing-function: cubic-bezier(0.82, 0.58, 0.17, 0.9);
	}
	.navbar-container.active{
		animation-direction: normal;
		display: block !important;
		animation-name: zoomInFade
	}
}

@keyframes zoomInFade {
	0%{
		opacity: 0;
		transform: translateY(60px);
		filter: blur(3px);
	}
	100%{
		opacity: 1;
		transform: translateY(0px);
		filter: blur(0px);
	}
}
</style>