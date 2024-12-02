<script setup>
import {GetLocale} from "@/utilities/locale.js";
import {computed, onMounted, ref, useTemplateRef} from "vue";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import LocaleText from "@/components/text/localeText.vue";

const searchBarPlaceholder = computed(() => {
	return GetLocale("Search Peers...")
})
let searchStringTimeout = undefined
const searchString = ref("")
const wireguardConfigurationStore = WireguardConfigurationsStore()

const debounce = () => {
	if (!searchStringTimeout){
		searchStringTimeout = setTimeout(() => {
			wireguardConfigurationStore.searchString = searchString.value;
		}, 300)
	}else{
		clearTimeout(searchStringTimeout)
		searchStringTimeout = setTimeout(() => {
			wireguardConfigurationStore.searchString = searchString.value;
		}, 300)
	}
}

const emits = defineEmits(['close'])
const input = useTemplateRef('searchBar')

onMounted(() => {
	input.value.focus();
})

</script>

<template>
	<div class="fixed-bottom w-100 bottom-0 z-2" style="z-index: 1;">
		<div class="container-fluid">
			<div class="row g-0">
				<div class="col-md-3 col-lg-2"></div>
				<div class="col-md-9 col-lg-10 d-flex justify-content-center py-2">
					<div class="rounded-3 p-2 border shadow searchPeersContainer bg-body-tertiary">
						<div class="d-flex gap-1 align-items-center px-2">
							<h6 class="mb-0 me-2">
								<label for="searchPeers">
									<i class="bi bi-search"></i>
								</label>
							</h6>
							<input 
								ref="searchBar"
								class="form-control rounded-3 bg-secondary-subtle border-1 border-secondary-subtle "
							       :placeholder="searchBarPlaceholder"
							       id="searchPeers"
							       @keyup="debounce()"
							       v-model="searchString">
							<button 
								@click="emits('close')"
								class="btn btn-secondary rounded-3 d-flex align-items-center">
								<i class="bi bi-x-circle-fill me-2"></i><LocaleText t="Hide"></LocaleText>
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
.searchPeersContainer{
	width: 100%;
}



</style>