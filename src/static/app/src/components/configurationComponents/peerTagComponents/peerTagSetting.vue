<script setup lang="ts">
import LocaleText from "@/components/text/localeText.vue";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js"
import {ref} from "vue";
const store = WireguardConfigurationsStore();
const props = defineProps(['group'])
const emits = defineEmits(['delete', 'iconPickerOpen', 'colorPickerOpen'])

const groupName = ref(props.group.GroupName)
</script>

<template>
<div class="border rounded-3 p-2">
	<div
		class="rounded-3 align-items-center overflow-scroll d-flex gap-2 position-relative">
		<div
			@click="emits('iconPickerOpen')"
			aria-label="Pick icon button"
			class="d-flex align-items-center p-2 btn btn-sm border rounded-2">
			<i class="bi" :class="'bi-' + group.Icon" :aria-label="group.Icon" v-if="group.Icon"></i>
			<span style="white-space: nowrap" v-else>
					<LocaleText t="No Icon"></LocaleText>
				</span>
		</div>
		<div
			aria-label="Pick color button"
			@click="emits('colorPickerOpen')"
			:style="{'background-color': group.BackgroundColor, 'color': store.colorText(group.BackgroundColor)}"
			class="d-flex align-items-center  p-2 btn btn-sm border rounded-2">
			<i class="bi bi-eyedropper"  ></i>
		</div>
		<input
			v-model="groupName"
			@change="group.GroupName = groupName"
			class="form-control form-control-sm p-2 rounded-2 w-100">
		<div
			aria-label="Pick color button" @click="emits('delete')"
			class="rounded-2 border p-2 btn btn-sm btn-outline-danger">
			<i class="bi bi-trash-fill" ></i>
		</div>
	</div>
</div>
</template>

<style scoped>

</style>