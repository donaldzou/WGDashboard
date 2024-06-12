<script>
import {wgdashboardStore} from "@/stores/wgdashboardStore.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

export default {
	name: "navbar",
	setup(){
		const wireguardConfigurationsStore = WireguardConfigurationsStore();
		const dashboardConfigurationStore = DashboardConfigurationStore();
		return {wireguardConfigurationsStore, dashboardConfigurationStore}
	}
}
</script>

<template>
	<div class="col-md-3 col-lg-2 d-md-block p-3">
		<nav id="sidebarMenu" class=" bg-body-tertiary sidebar border h-100 rounded-3 shadow" >
			<div class="sidebar-sticky pt-3">
				<ul class="nav flex-column">
					<li class="nav-item">
						<RouterLink class="nav-link" to="/" exact-active-class="active">Home</RouterLink></li>
					<li class="nav-item">
						<RouterLink class="nav-link" to="/settings" 
						            exact-active-class="active">Settings</RouterLink></li>
				</ul>
				<hr>
				<h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
					<span>Configurations</span>
				</h6>
				<ul class="nav flex-column">
					<li class="nav-item">
						<RouterLink :to="'/configuration/'+c.Name + '/peers'" class="nav-link nav-conf-link"
						            active-class="active"
						            
						            v-for="c in this.wireguardConfigurationsStore.Configurations">
							<samp>{{c.Name}}</samp>
						</RouterLink>
					</li>
				</ul>
				<hr>
				<h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
					<span>Tools</span>
				</h6>
				<ul class="nav flex-column">
					<li class="nav-item">
						<RouterLink to="/ping" class="nav-link">Ping</RouterLink></li>
					<li class="nav-item"><a class="nav-link" data-toggle="modal" data-target="#traceroute_modal" href="#">Traceroute</a></li>
				</ul>
				<hr>
				<ul class="nav flex-column">
					<li class="nav-item"><a class="nav-link text-danger" @click="this.dashboardConfigurationStore.signOut()" role="button" style="font-weight: bold">Sign Out</a></li>
				</ul>
				<ul class="nav flex-column">
					<li class="nav-item"><a href="https://github.com/donaldzou/WGDashboard/releases/tag/"><small class="nav-link text-muted"></small></a></li>
				</ul>
			</div>
		</nav>
	</div>
	
	
</template>

<style scoped>

</style>