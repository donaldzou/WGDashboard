<script setup lang="ts">
import LocaleText from "@/components/text/localeText.vue";
import { fetchGet } from "@/utilities/fetch.js"
import {onMounted, ref} from "vue";
import AddWebHook from "@/components/settingsComponent/dashboardWebHooksComponents/addWebHook.vue";
import WebHookSessions from "@/components/settingsComponent/dashboardWebHooksComponents/webHookSessions.vue";
const webHooks = ref([])
const webHooksLoaded = ref(false)

onMounted(async () => {
	await getWebHooks()
	webHooksLoaded.value = true
})
const getWebHooks = async () => {
	await fetchGet("/api/webHooks/getWebHooks", {}, (res) => {
		webHooks.value = res.data
	})
}

const addWebHook = ref(false)
const selectedWebHook = ref(undefined)

const view = ref("edit")
</script>

<template>
	<div class="text-body w-100 h-100 pb-2 position-relative">
		<div class="w-100 h-100 card rounded-3">
			<div class="border-bottom z-0">
				<div class="d-flex text-body align-items-center sticky-top p-3 bg-body-tertiary rounded-top-3" style="border-top-right-radius: 0 !important;">
					<h6 class="my-2">
						<i class="bi bi-plug-fill me-2"></i>
						<LocaleText t="Webhooks"></LocaleText>
					</h6>
					<button class="btn btn-sm bg-primary-subtle text-primary-emphasis border-1 border-primary-subtle rounded-3 shadow-sm ms-auto"
							@click="addWebHook = true; selectedWebHook = undefined"
							v-if="!addWebHook"
					>
						<i class="bi bi-plus-circle-fill me-2"></i>
						<LocaleText t="Webhook"></LocaleText>
					</button>
					<button class="btn btn-sm bg-secondary-subtle text-secondary-emphasis border-1 border-secondary-subtle rounded-3 shadow-sm ms-auto"
							@click="addWebHook = false"
							v-else
					>
						<i class="bi bi-chevron-left me-2"></i>
						<LocaleText t="Back"></LocaleText>
					</button>
				</div>
			</div>
			<div class="row h-100 g-0" v-if="!addWebHook">
				<div class="col-sm-4 border-end d-flex flex-column clientListContainer">
					<div class="d-flex flex-column overflow-y-scroll" style="flex: 1 0 0">
						<div class="list-group d-flex flex-column d-flex h-100">
							<a role="button"
							   @click="selectedWebHook = webHook"
							   :class="{active: selectedWebHook?.WebHookID === webHook.WebHookID}"
							   v-if="webHooks.length > 0"
							   v-for="webHook in webHooks"
							   class="list-group-item list-group-item-action " aria-current="true">
								<p class="mb-0 fw-bold text-body url" >
									{{ webHook.PayloadURL }}
								</p>
								<p class="url mb-0">
									<LocaleText t="Subscribed Actions"></LocaleText>:
									{{ webHook.SubscribedActions.join(", ")}}
								</p>
							</a>
							<div class="flex-grow-1 d-flex text-muted" v-else>
								<LocaleText t="No Webhooks" class="m-auto"></LocaleText>
							</div>
						</div>
					</div>
				</div>
				<div
					v-if="selectedWebHook"
					class="col-sm-8 clientViewerContainer  d-flex flex-column " >
					<div class="overflow-scroll"  style="flex: 1 0 0">
						<nav class="navbar navbar-expand-lg bg-body-tertiary sticky-top">
							<div class="container-fluid">
								<div>
									<ul class="navbar-nav gap-2">
										<li class="nav-item">
											<a
												@click="view = 'edit'"
												:class="{active: view === 'edit'}"
												class="nav-link  rounded-3" role="button">Edit</a>
										</li>
										<li class="nav-item">
											<a
												:class="{active: view === 'sessions'}"
												@click="view = 'sessions'"
												class="nav-link rounded-3" role="button">Sessions</a>
										</li>
									</ul>
								</div>
							</div>
						</nav>
						<AddWebHook
							v-if="view === 'edit'"
							:key="selectedWebHook"
							@delete="getWebHooks(); selectedWebHook = undefined;"
							:webHook="selectedWebHook" @refresh="getWebHooks()" ></AddWebHook>
						<Suspense v-else-if="view === 'sessions'">
							<WebHookSessions
								:key="selectedWebHook"
								:webHook="selectedWebHook"></WebHookSessions>
							<template #fallback>
								<div class="p-3">
									<LocaleText t="Loading..."></LocaleText>
								</div>
							</template>
						</Suspense>
					</div>
				</div>
			</div>
			<suspense v-else>
				<AddWebHook @refresh="selectedWebHook = undefined; addWebHook = false;  getWebHooks(); "></AddWebHook>
			</suspense>
		</div>
	</div>
</template>

<style scoped>
.list-group-item{
	border-radius: 0 !important;
	border-left: 0 !important;
	border-right: 0 !important;
}

.list-group-item:first-child{
	border-top: 0 !important;
}
.url{
	text-overflow: ellipsis;
	overflow: hidden;
	white-space: nowrap;
	font-size: 0.9rem;
}

</style>