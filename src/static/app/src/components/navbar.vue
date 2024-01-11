<script>
import {wgdashboardStore} from "@/stores/wgdashboardStore.js";

export default {
	name: "navbar",
	setup(){
		const store = wgdashboardStore()
		return {store}
	}
}
</script>

<template>
	<nav id="sidebarMenu" class="col-md-3 col-lg-2 d-md-block bg-body-tertiary sidebar border border-right p-0">
		<div class="sidebar-sticky pt-3">
			<ul class="nav flex-column">
				<li class="nav-item">
					<RouterLink class="nav-link" to="/" exact-active-class="active">Home</RouterLink></li>
				<li class="nav-item">
					<RouterLink class="nav-link" to="/settings" exact-active-class="active">Settings</RouterLink></li>
			</ul>
			<hr>
			<h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
				<span>Configurations</span>
				
			</h6>
			<ul class="nav flex-column">
				<li class="nav-item">
					<RouterLink :to="'/configuration/'+c.Name" class="nav-link nav-conf-link" v-for="c in this.store.WireguardConfigurations">
						<samp>{{c.Name}}</samp>
					</RouterLink>
				</li>
			</ul>
			<hr>
			<h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
				<span>Tools</span>
			</h6>
			<ul class="nav flex-column">
				<li class="nav-item"><a class="nav-link" data-toggle="modal" data-target="#ping_modal" href="#">Ping</a></li>
				<li class="nav-item"><a class="nav-link" data-toggle="modal" data-target="#traceroute_modal" href="#">Traceroute</a></li>
			</ul>
			<hr>
			<ul class="nav flex-column">
				<li class="nav-item"><a href="https://github.com/donaldzou/WGDashboard/releases/tag/"><small class="nav-link text-muted"></small></a></li>
			</ul>
		</div>
	</nav>
</template>

<style scoped>

</style>