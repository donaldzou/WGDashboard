<script setup>
import LocaleText from "@/components/text/localeText.vue";

const props = defineProps({
	protocol: String,
	mini: false
})
</script>

<template>
<span class="badge wireguardBg rounded-3 shadow" v-if="protocol === 'wg'">
	WireGuard <LocaleText t="Configuration" v-if="!mini"></LocaleText>
</span>
<span class="badge amneziawgBg rounded-3 shadow" v-else-if="protocol === 'awg'">
	AmneziaWG <LocaleText t="Configuration" v-if="!mini"></LocaleText>
</span>
</template>

<style scoped>

</style>