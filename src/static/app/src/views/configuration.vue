<script>
export default {
	name: "configuration",
}
</script>

<template>
	<div class="mt-5 text-body">
		<RouterView v-slot="{ Component, route }">
			<Transition name="fade2" mode="out-in">
				<Suspense>
					<Component :is="Component" :key="route.path"></Component>
				</Suspense>
			</Transition>
		</RouterView>
	</div>
</template>

<style scoped>
	
</style>