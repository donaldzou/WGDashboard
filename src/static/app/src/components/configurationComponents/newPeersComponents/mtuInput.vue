<script>
import LocaleText from "@/components/text/localeText.vue";

export default {
	name: "mtuInput",
	components: {LocaleText},
	props: {
		data: Object,
		saving: Boolean
	}
}
</script>

<template>
	<div>
		<label for="peer_mtu" class="form-label"><small class="text-muted">
			<LocaleText t="MTU"></LocaleText>
		</small></label>
		<input type="number" class="form-control form-control-sm rounded-3"
		       :disabled="this.saving"
		       v-model="this.data.mtu"
		       min="0"
		       id="peer_mtu">
	</div>
</template>

<style scoped>

</style>