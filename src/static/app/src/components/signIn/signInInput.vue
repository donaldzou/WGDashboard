<script>
import {GetLocale} from "@/utilities/locale.js";

export default {
	name: "signInInput",
	methods: {GetLocale},
	props: {
		id: "",
		data: "",
		type: "",
		placeholder: ""
	},
	computed: {
		getLocaleText(){
			return GetLocale(this.placeholder)
		}
	}
}
</script>

<template>
	<input :type="type" v-model="this.data[this.id]" class="form-control" 
	       :id="this.id" :name="this.id"
	       autocomplete="on"
	       :placeholder="this.getLocaleText" required>
</template>

<style scoped>

</style>