<script>
export default {
	name: "peer",
	props: {
		Peer: Object
	}
}
</script>

<template>
	<div class="card shadow-sm rounded-3">
		<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0">
			<div class="dot ms-0" :class="{active: Peer.status === 'running'}"></div>
			<div style="font-size: 0.8rem" class="ms-auto d-flex gap-2">
				<span class="text-primary">
					<i class="bi bi-arrow-down"></i><strong>
					{{(Peer.cumu_receive + Peer.total_receive).toFixed(4)}}</strong> GB
				</span>
				<span class="text-success">
					<i class="bi bi-arrow-up"></i><strong>
					{{(Peer.cumu_sent + Peer.total_sent).toFixed(4)}}</strong> GB
				</span>
				<span class="text-secondary" v-if="Peer.latest_handshake !== 'No Handshake'">
					<i class="bi bi-arrows-angle-contract"></i>
					{{Peer.latest_handshake}} ago
				</span>
			</div>
		</div>
		<div class="card-body pt-1" style="font-size: 0.9rem">
			<h5>
				{{Peer.name ? Peer.name : 'Untitled Peer'}}
			</h5>
			<div class="mb-2">
				<small class="text-muted">Public Key</small>
				<p class="mb-0"><samp>{{Peer.id}}</samp></p>
			</div>
			<div>
				<small class="text-muted">Allowed IP</small>
				<p class="mb-0"><samp>{{Peer.allowed_ip}}</samp></p>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>