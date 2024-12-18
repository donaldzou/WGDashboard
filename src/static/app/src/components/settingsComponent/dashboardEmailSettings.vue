<script setup>
import LocaleText from "@/components/text/localeText.vue";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {preventDefault} from "ol/events/Event.js";
import {onMounted} from "vue";
import {fetchPost} from "@/utilities/fetch.js";
const store = DashboardConfigurationStore()

onMounted(() => {
	document.querySelectorAll("#emailAccount input").forEach(x => {
		x.addEventListener("blur", async () => {
			let id = x.attributes.getNamedItem('id').value;
			await fetchPost("/api/updateDashboardConfigurationItem", {
				section: "Email",
				key: id,
				value: x.value
			}, (res) => {
				if (res.status){
					x.classList.remove('is-invalid')
					x.classList.add('is-valid')
				}else{
					x.classList.remove('is-valid')
					x.classList.add('is-invalid')
				}
			})
		})
	})
})

</script>

<template>
	<div class="card" id="emailAccount">
		<div class="card-header">
			<h6 class="my-2">
				<LocaleText t="Email Account"></LocaleText>
			</h6>
		</div>
		<div class="card-body">
			<form @submit="(e) => preventDefault(e)">
				<div class="row gx-2 gy-2">
					<div class="col-12 col-lg-4">
						<div class="form-group">
							<label for="server" class="text-muted mb-1">
								<strong><small>
									<LocaleText t="Server"></LocaleText>
								</small></strong>
							</label>
							<input id="server" 
							       v-model="store.Configuration.Email.server"
							       type="text" class="form-control">
						</div>
					</div>
					<div class="col-12 col-lg-4">
						<div class="form-group">
							<label for="port" class="text-muted mb-1">
								<strong><small>
									<LocaleText t="Port"></LocaleText>
								</small></strong>
							</label>
							<input id="port"
							       v-model="store.Configuration.Email.port"
							       type="text" class="form-control">
						</div>
					</div>
					<div class="col-12 col-lg-4">
						<div class="form-group">
							<label for="encryption" class="text-muted mb-1">
								<strong><small>
									<LocaleText t="Encryption"></LocaleText>
								</small></strong>
							</label>
							<input id="encryption"
							       v-model="store.Configuration.Email.encryption"
							       type="text" class="form-control">
						</div>
					</div>
					<div class="col-12 col-lg-6">
						<div class="form-group">
							<label for="username" class="text-muted mb-1">
								<strong><small>
									<LocaleText t="Username"></LocaleText>
								</small></strong>
							</label>
							<input id="username"
							       v-model="store.Configuration.Email.username"
							       type="text" class="form-control">
						</div>
					</div>
					<div class="col-12 col-lg-6">
						<div class="form-group">
							<label for="email_password" class="text-muted mb-1">
								<strong><small>
									<LocaleText t="Password"></LocaleText>
								</small></strong>
							</label>
							<input id="email_password"
							       v-model="store.Configuration.Email.email_password"
							       type="password" class="form-control">
						</div>
					</div>
				</div>
			</form>
		</div>
	</div>
</template>

<style scoped>

</style>