<script>
import Navbar from "@/components/navbar.vue";

export default {
	name: "index",
	components: {Navbar}
}
</script>

<template>
	<div class="container-fluid flex-grow-1">
		<div class="row h-100">
			<Navbar></Navbar>
			<main class="col-md-9 ml-sm-auto col-lg-10 px-md-4 mb-4">
				<RouterView></RouterView>
			</main>
		</div>
	</div>
</template>

<style scoped>

</style>