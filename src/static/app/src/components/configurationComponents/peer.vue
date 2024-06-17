<script>
import { ref } from 'vue'
import { onClickOutside } from '@vueuse/core'
import "animate.css"
import PeerSettingsDropdown from "@/components/configurationComponents/peerSettingsDropdown.vue";
export default {
	name: "peer",
	components: {PeerSettingsDropdown},
	props: {
		Peer: Object
	},
	data(){
		return {
		
		}
	},
	setup(){
		const target = ref(null);
		const subMenuOpened = ref(false)
		onClickOutside(target, event => {
			subMenuOpened.value = false;
		});
		return {target, subMenuOpened}
	},
	computed: {
		getLatestHandshake(){
			if (this.Peer.latest_handshake.includes(",")){
				return this.Peer.latest_handshake.split(",")[0]
			}
			return this.Peer.latest_handshake;
		}
	}
}
</script>

<template>
	<div class="card shadow-sm rounded-3"
		:class="{'border-warning': Peer.restricted}"
	>
		<div>
			<div v-if="!Peer.restricted" class="card-header bg-transparent d-flex align-items-center gap-2 border-0">
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
						{{getLatestHandshake}} ago
					</span>
				</div>
			</div>
			<div v-else class="border-0 card-header bg-transparent text-warning fw-bold" 
			     style="font-size: 0.8rem">
				<i class="bi-lock-fill me-2"></i>
				Access Restricted
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
			<div class="d-flex align-items-end">
				<div>
					<small class="text-muted">Allowed IP</small>
					<p class="mb-0"><samp>{{Peer.allowed_ip}}</samp></p>
				</div>
				<div class="ms-auto px-2 rounded-3 subMenuBtn"
				     :class="{active: this.subMenuOpened}"
				>
					<a role="button" class="text-body" 
					   
					   @click="this.subMenuOpened = true">
						<h5 class="mb-0"><i class="bi bi-three-dots"></i></h5>
					</a>
					<Transition name="slide-fade">
						<PeerSettingsDropdown 
							@qrcode="(file) => this.$emit('qrcode', file)"
							@setting="this.$emit('setting')"
							@jobs="this.$emit('jobs')"
							@refresh="this.$emit('refresh')"
							:Peer="Peer"
							v-if="this.subMenuOpened"
							ref="target"
						></PeerSettingsDropdown>
					</Transition>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

.slide-fade-leave-active, .slide-fade-enter-active {
	transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
	transform: translateY(20px);
	opacity: 0;
}

.subMenuBtn.active{
	background-color: #ffffff20;
}
</style>