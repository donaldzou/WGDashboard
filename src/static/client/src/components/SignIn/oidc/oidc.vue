<script setup async>

import {axiosGet} from "@/utilities/request.js";
import {ref} from "vue";
import OidcBtn from "@/components/SignIn/oidc/oidcBtn.vue";

const providerExist = ref(false)
const providers = ref(undefined)
const getProviders = await axiosGet("/api/signin/oidc/providers")
if (getProviders){
	providerExist.value = true;
	providers.value = getProviders.data
	console.log(providers.value)
}

</script>

<template>
	<div class="d-flex gap-2" v-if="providers">
		<suspense>
			<OidcBtn :provider="provider" :name="name" v-for="(provider, name) in providers"></OidcBtn>
		</suspense>
	</div>
</template>

<style scoped>

</style>