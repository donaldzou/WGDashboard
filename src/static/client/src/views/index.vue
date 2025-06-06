<script setup async>
import {computed, onMounted, ref} from "vue";
import {axiosGet} from "@/utilities/request.js";
import {clientStore} from "@/stores/clientStore.js";
import Configuration from "@/components/Configuration/configuration.vue";
const store = clientStore()
const loading = ref(true)

const loadConfigurations = async () => {

	await store.getConfigurations()

}

const configurations = computed(() => {
	return store.configurations
});

onMounted(async () => {
	// loading.value = true;
	await loadConfigurations();
	loading.value = false;

})
</script>

<template>
<div class="">
	<ul class="nav  gap-0 border-bottom">
		<li class="nav-item">
			<a class="nav-link text-body border-start-0" aria-current="page" href="#">
				<strong>WGDashboard Client</strong>
			</a>
		</li>
		<li class="nav-item ms-auto">
			<a class="nav-link text-body" aria-current="page" href="#">
				<i class="bi bi-gear-fill me-sm-2"></i>
				<span>Settings</span>
			</a>
		</li>
		<li class="nav-item">
			<RouterLink to="/signout" class="nav-link text-danger" aria-current="page">
				<i class="bi bi-box-arrow-left me-sm-2"></i>
				<span>Sign Out</span>
			</RouterLink>
		</li>
	</ul>
	<Transition name="app" mode="out-in">
		<div class="d-flex flex-column gap-3" v-if="!loading">
			<div class="px-3 border-bottom py-4">
				<h6>Hi donaldzou@live.hk!</h6>
				<h5 class="mb-0">You have <strong>
					{{ configurations.length }}
				</strong> configuration{{ configurations.length > 1 ? 's':''}} available</h5>
			</div>
			<div class="px-3">
				<Configuration v-for="config in configurations" :config="config"></Configuration>
			</div>
			<div></div>
		</div>
		<div v-else class="d-flex py-4">
			<div class="spinner-border m-auto"></div>
		</div>
	</Transition>
</div>
</template>

<style scoped>
.nav-link{
	padding: 1rem 1rem;
	border-left: 1px solid var(--bs-border-color)
}

@media screen and (max-width: 576px) {
	.nav-link span{
		display: none;
	}
}
</style>