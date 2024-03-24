<script>
export default {
	name: "peerSettingsDropdown",
	props: {
		Peer: Object
	}
}
</script>

<template>
	<ul class="dropdown-menu mt-2 shadow-lg d-block rounded-3" style="max-width: 200px">
		<template v-if="!this.Peer.private_key">
			<li>
				<small class="w-100 dropdown-item text-muted"
				       style="white-space: break-spaces; font-size: 0.7rem"
				>Download & QR Code is not available due to no <code>private key</code>
					set for this peer
				</small>
			</li>
			<li><hr class="dropdown-divider"></li>
		</template>
		
		<li>
			<a class="dropdown-item d-flex" role="button"
				@click="this.$emit('setting')"
			>
				<i class="me-auto bi bi-pen"></i> Edit
			</a>
		</li>
		<template v-if="this.Peer.private_key">
			<li>
				<a class="dropdown-item d-flex" role="button">
					<i class="me-auto bi bi-download"></i> Download
				</a>
			</li>
			<li>
				<a class="dropdown-item d-flex" role="button">
					<i class="me-auto bi bi-qr-code"></i> QR Code
				</a>
			</li>
		</template>
		
		<li><hr class="dropdown-divider"></li>
		<li>
			<a class="dropdown-item d-flex text-warning" 
			   
			   role="button">
				<i class="me-auto bi bi-lock"></i> Lock
			</a>
		</li>
		<li>
			<a class="dropdown-item d-flex fw-bold text-danger" 
			   
			   role="button">
				<i class="me-auto bi bi-trash"></i> Delete
			</a>
		</li>
	</ul>
</template>

<style scoped>
.dropdown-menu{
	right: 1rem;
}
</style>