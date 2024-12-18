<script>
import {GetLocale} from "@/utilities/locale.js";

export default {
	name: "localeText",
	props: {
		t: ""
	},
	computed: {
		getLocaleText(){
			return GetLocale(this.t)
		}
	}
}
</script>

<template>
	<span>
		{{ this.getLocaleText }}
	</span>
</template>

<style scoped>

</style>