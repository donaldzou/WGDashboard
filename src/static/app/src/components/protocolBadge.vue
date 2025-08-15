<script setup>
import LocaleText from "@/components/text/localeText.vue";
import {onMounted, ref} from "vue";

const props = defineProps({
	protocol: String,
	mini: false
})

const blur = ref(undefined)

onMounted(() => {
	setTimeout(() => {
		blur.value = !props.mini
	}, 500)
})
</script>

<template>
<div class="position-relative">
	<span class="badge wireguardBg rounded-3 shadow z-1"
		  :class="{blur: blur === true}"
		  v-if="protocol === 'wg'">
		WireGuard <LocaleText t="Configuration" v-if="!mini"></LocaleText>
	</span>
	<span class="badge amneziawgBg rounded-3 shadow"
		  :class="{blur: blur === true}"
		  v-else-if="protocol === 'awg'">
		AmneziaWG <LocaleText t="Configuration" v-if="!mini"></LocaleText>
	</span>

</div>
</template>

<style scoped>
.wireguardBg.blur{
	box-shadow: rgba(255, 56, 56, 1) 3rem 1rem 8rem 10px !important;
	transition: box-shadow 1s ease-in-out;
}
.amneziawgBg.blur{
	box-shadow: rgb(227, 142, 65) 3rem 1rem 8rem 10px !important;
	transition: box-shadow 1s ease-in-out;
}
</style>