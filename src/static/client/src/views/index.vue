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
	await loadConfigurations();
	loading.value = false;
})
</script>

<template>
<div class="p-sm-3">
	<div class="w-100 d-flex align-items-center">
		<a class="nav-link text-body border-start-0" aria-current="page" href="#">
			<strong>WGDashboard Client</strong>
		</a>
		<div class="ms-auto px-3 d-flex gap-2 nav-links">
			<a class=" text-body btn btn-body rounded-3 ms-auto btn-sm" aria-current="page" href="#">
				<i class="bi bi-gear-fill me-sm-2"></i>
				<span>Settings</span>
			</a>
			<RouterLink to="/signout" class="btn btn-danger rounded-3  btn-sm" aria-current="page">
				<i class="bi bi-box-arrow-left me-sm-2"></i>
				<span>Sign Out</span>
			</RouterLink>
		</div>
	</div>

	<Transition name="app" mode="out-in">
		<div class="d-flex flex-column gap-3" v-if="!loading">
			<div class="p-3 d-flex flex-column gap-3">
				<Configuration v-for="config in configurations" :config="config"></Configuration>
<!--				<h6 class="mb-0 text-center text-muted">-->
<!--					<small>-->
<!--						<strong>-->
<!--							{{ configurations.length }}-->
<!--						</strong> configuration{{ configurations.length > 1 ? 's':''}}-->
<!--					</small>-->
<!--				</h6>-->
			</div>
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
}

@media screen and (max-width: 576px) {
	.nav-links a span{
		display: none;
	}
}
</style>