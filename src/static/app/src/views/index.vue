<script>
import Navbar from "@/components/navbar.vue";
import {wgdashboardStore} from "@/stores/wgdashboardStore.js";
import {WireguardConfigurations} from "@/models/WireguardConfigurations.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import Message from "@/components/messageCentreComponent/message.vue";

export default {
	name: "index",
	components: {Message, Navbar},
	async setup(){
		const dashboardConfigurationStore = DashboardConfigurationStore()
		return {dashboardConfigurationStore}
	},
	computed: {
		getMessages(){
			return this.dashboardConfigurationStore.Messages.filter(x => x.show)
		}
	}
}
</script>

<template>
	<div class="container-fluid flex-grow-1 main" :data-bs-theme="this.dashboardConfigurationStore.Configuration.Server.dashboard_theme">
		<div class="row h-100">
			<Navbar></Navbar>
			<main class="col-md-9 ml-sm-auto col-lg-10 px-md-4 overflow-y-scroll mb-0">
				<Suspense>
					<RouterView v-slot="{Component}">
						<Transition name="fade2" mode="out-in" appear>
							<Component :is="Component"></Component>
						</Transition>
					</RouterView>
				</Suspense>
				<div class="messageCentre text-body position-fixed d-flex">
					<TransitionGroup name="message" tag="div" 
					                 class="position-relative flex-sm-grow-0 flex-grow-1 d-flex align-items-end ms-sm-auto flex-column gap-2">
						<Message v-for="m in getMessages.slice().reverse()"
						         :message="m" :key="m.id"></Message>
					</TransitionGroup>
				</div>
			</main>
		</div>
	</div>
</template>

<style scoped>
	.messageCentre{
		top: 1rem;
		right: 1rem;
		width: calc(100% - 2rem);
	}
	main{
		height: 100vh;
	}
	
	@supports (height: 100dvh) {
		@media screen and (max-width: 768px) {
			main{
				height: calc(100dvh - 50px);
			}
		}
	}
	
	
</style>