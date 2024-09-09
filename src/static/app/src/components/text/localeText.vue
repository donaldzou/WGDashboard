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
	{{ this.getLocaleText }}
</template>

<style scoped>

</style>