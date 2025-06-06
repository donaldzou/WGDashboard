<script setup>
import './assets/main.css'
import NotificationList from "@/components/Notification/notificationList.vue";
</script>

<template>
	<div data-bs-theme="dark" class="text-body bg-body w-100 h-100">
		<div class="d-flex vh-100 vw-100 p-4 overflow-y-scroll">
			<div class="mx-auto my-sm-auto bg-body-tertiary rounded-4 shadow-lg border position-relative"
			     style="width: 700px">
				<Suspense>
					<RouterView v-slot="{ Component }">
						<Transition name="app" type="transition" mode="out-in">
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
