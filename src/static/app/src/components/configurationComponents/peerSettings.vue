<script>
export default {
	name: "peerSettings"
}
</script>

<template>
	<div class="peerSettingContainer w-100 h-100 position-absolute top-0 start-0">
		<div class="container d-flex h-100 w-100">
			<div class="card m-auto rounded-3 w-100">
				<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4">
					<h4 class="mb-0">Peer Settings</h4>
					<router-link to="./" class="ms-auto btn">
						<i class="bi bi-x-lg"></i>
					</router-link>
				</div>
				
				<div class="card-body p-4">
					
				</div>
			</div>
		</div>
		
	</div>
</template>

<style scoped>
.peerSettingContainer{
	background-color: #00000060;
	z-index: 1000;
}
</style>