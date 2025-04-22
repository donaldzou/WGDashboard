<script>
import LocaleText from "@/components/text/localeText.vue";
import {GetLocale} from "@/utilities/locale.js";
import {useRoute} from "vue-router";
import {fetchGet} from "@/utilities/fetch.js";

export default {
	name: "bulkAdd",
	components: {LocaleText},
	props: {
		saving: Boolean,
		data: Object,
		availableIp: undefined
	},
	data(){
		return {
			numberOfAvailableIPs: null
		}	
	},
	computed:{
		bulkAddGetLocale(){
			return GetLocale("How many peers you want to add?")
		},
		getNumberOfAvailableIPs(){
			if (!this.numberOfAvailableIPs){
				return '...'
			}else{
				return Object.values(this.numberOfAvailableIPs).reduce((x, y) => {
					return x + y
				})
			}
		}
	},
	watch: {
		'data.bulkAdd': {
			immediate: true,
			handler(newVal){
				if (newVal){
					fetchGet("/api/getNumberOfAvailableIPs/" + this.$route.params.id, {}, (res) => {
						if (res.status){
							this.numberOfAvailableIPs = res.data
						}
					})
				}
			}
		}
	}
}
</script>

<template>
	<div>
		<div class="form-check form-switch ">
			<input class="form-check-input"
			       type="checkbox" role="switch"
			       :disabled="!this.availableIp"
			       id="bulk_add" v-model="this.data.bulkAdd">
			<label class="form-check-label me-2" for="bulk_add">
				<small><strong>
					<LocaleText t="Bulk Add"></LocaleText>
				</strong></small>
			</label>
		</div>
		<p :class="{'mb-0': !this.data.bulkAdd}"><small class="text-muted d-block">
			<LocaleText t="By adding peers by bulk, each peer's name will be auto generated, and Allowed IP will be assign to the next available IP."></LocaleText>
		</small></p>

		<div class="form-group" v-if="this.data.bulkAdd">
			<input class="form-control form-control-sm rounded-3 mb-1" type="number" min="1"
			       id="bulk_add_count"
			       :max="this.availableIp.length"
			       v-model="this.data.bulkAddAmount"
			       :placeholder="this.bulkAddGetLocale">
			<small class="text-muted">
				<LocaleText :t="`You can add up to ` + 
				    getNumberOfAvailableIPs
				 + ' peers'"></LocaleText> 
			</small>
		</div>
	</div>
</template>

<style scoped>

</style>