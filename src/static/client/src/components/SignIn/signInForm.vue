<script setup>
import {computed, reactive, ref} from "vue";
import {clientStore} from "@/stores/clientStore.js";
import axios from "axios";
import {requestURl} from "@/utilities/request.js";
import {useRoute, useRouter} from "vue-router";
const loading = ref(false)
const formData = reactive({
	Email: "",
	Password: ""
});
const emits = defineEmits(['totpToken'])

const totpToken = ref("")
const store = clientStore()
const signIn = async (e) => {
	e.preventDefault();
	if (!formFilled){
		store.newNotification("Please fill in all fields", "warning")
		return;
	}
	loading.value = true;
	await axios.post(requestURl("/api/signin"), formData).then(res => {
		let data = res.data;
		if (!data.status){
			store.newNotification(data.message, "danger")
			loading.value = false;
		}else{
			emits("totpToken", data.message)
		}
	})
}

const formFilled = computed(() => {
	return Object.values(formData).find(x => !x) === undefined
})

// const router = useRouter()
const route = useRoute()
if (route.query.Email){
	formData.Email = route.query.Email
}
</script>

<template>
	<div>
		<h1>Sign In</h1>
		<p>to your WGDashboard Client account</p>
		<form class="mt-4 d-flex flex-column gap-3" @submit="e => signIn(e)">
			<div class="form-floating">
				<input type="text"
				       required
				       :disabled="loading"
				       v-model="formData.Email"
				       name="email"
				       autocomplete="email"
				       autofocus
				       class="form-control rounded-3" id="email" placeholder="email">
				<label for="email" class="d-flex">
					<i class="bi bi-person-circle me-2"></i>
					Email
				</label>
			</div>
			<div class="form-floating">
				<input type="password"
				       required
				       :disabled="loading"
				       v-model="formData.Password"
				       name="password"
				       autocomplete="current-password"
				       class="form-control rounded-3" id="password" placeholder="Password">
				<label for="password" class="d-flex">
					<i class="bi bi-key me-2"></i>
					Password
				</label>
			</div>
			<div>
				<a href="#" class="text-body text-decoration-none ms-0">
					Forgot Password?
				</a>
			</div>
			<button
				:disabled="!formFilled || loading"
				class="btn btn-primary rounded-3 btn-brand px-3 py-2">
				<Transition name="slide-right" mode="out-in">
					<span v-if="!loading" class="d-block">
						Continue <i class="ms-2 bi bi-arrow-right"></i>
					</span>
					<span v-else class="d-block">
						Loading...
						<i class="spinner-border spinner-border-sm"></i>
					</span>
				</Transition>
			</button>
		</form>
		<div>
			<hr class="my-4">
			<div class="d-flex align-items-center">
					<span class="text-muted">
						Don't have an account yet?
					</span>
				<RouterLink  to="/signup" class="text-body text-decoration-none ms-auto fw-bold">
					Sign Up
				</RouterLink>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>