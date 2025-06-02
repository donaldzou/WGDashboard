<script setup>
import './assets/main.css'
import NotificationList from "@/components/notification/notificationList.vue";
</script>

<template>
	<div data-bs-theme="dark" class="text-body bg-body w-100 h-100">
		<div class="d-flex vh-100 vw-100 p-4 overflow-y-scroll">
			<div class="m-auto p-5 bg-body-tertiary rounded-4 shadow-lg border" style="width: 700px">
				<Suspense>
					<RouterView v-slot="{ Component }">
						<Transition name="app" mode="out-in" type="transition" appear>
							<Component :is="Component"></Component>
						</Transition>
					</RouterView>
				</Suspense>
			</div>
		</div>
		<NotificationList></NotificationList>
	</div>
</template>

<style scoped>

</style>
