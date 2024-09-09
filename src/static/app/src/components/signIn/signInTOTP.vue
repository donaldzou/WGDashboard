<script>
import {GetLocale} from "@/utilities/locale.js";

export default {
	name: "signInTOTP",
	methods: {GetLocale},
	props: {
		data: "",
	},
	computed: {
		getLocaleText(){
			return GetLocale(this.placeholder)
		}
	}
}
</script>

<template>
	<input class="form-control totp"
	       required
	       id="totp" maxlength="6" type="text" inputmode="numeric" autocomplete="one-time-code"
	       :placeholder="this.getLocaleText('OTP from your authenticator')"
	       v-model="this.data.totp"
	>
</template>

<style scoped>

</style>