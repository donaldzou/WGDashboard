<script>
import "@/utilities/wireguard.js"
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import LocaleText from "@/components/text/localeText.vue";
export default {
	name: "privatePublicKeyInput",
	components: {LocaleText},
	props: {
		data: Object,
		saving: Boolean,
		bulk: Boolean
	},
	setup(){
		const dashboardStore = DashboardConfigurationStore();
		return {dashboardStore}
	},
	data(){
		return {
			keypair: {
				publicKey: "",
				privateKey: "",
				presharedKey: ""
			},
			editKey: false,
			error: false
		}
	},
	methods: {
		genKeyPair(){
			this.editKey = false;
			this.keypair = window.wireguard.generateKeypair();
			this.data.private_key = this.keypair.privateKey;
			this.data.public_key = this.keypair.publicKey;
		},
		testKey(key){
			const reg = /^[A-Za-z0-9+/]{43}=?=?$/;
			return reg.test(key)
		},
		checkMatching(){
			try{
				if(this.keypair.privateKey){
					if(this.testKey(this.keypair.privateKey)){
						this.keypair.publicKey = window.wireguard.generatePublicKey(this.keypair.privateKey)
						if (window.wireguard.generatePublicKey(this.keypair.privateKey)
							!== this.keypair.publicKey){
							this.error = true;
							this.dashboardStore.newMessage("WGDashboard", "Private Key and Public Key does not match.", "danger");
						}else{
							this.data.private_key = this.keypair.privateKey
							this.data.public_key = this.keypair.publicKey
						}
					}
				}
			}catch (e){
				this.error = true;
				this.data.private_key = "";
				this.data.public_key = "";
			}
		}
	},
	mounted() {
		this.genKeyPair();
	},
	watch: {
		keypair: {
			deep: true,
			handler(){
				this.error = false;
				this.checkMatching();
			}
		}
	}
}
</script>

<template>
	<div class="d-flex gap-2 flex-column" :class="{inactiveField: this.bulk}">
		<div>
			<label for="peer_private_key_textbox" class="form-label">
				<small class="text-muted">
					<LocaleText t="Private Key"></LocaleText>
					<code>
						<LocaleText t="(Required for QR Code and Download)"></LocaleText>
					</code></small>
			</label>
			<div class="input-group">
				<input type="text" class="form-control form-control-sm rounded-start-3"
				       v-model="this.keypair.privateKey"
				       :disabled="!this.editKey || this.bulk"
				       :class="{'is-invalid': this.error}"
				       @blur="this.checkMatching()"
				       id="peer_private_key_textbox">
				<button class="btn btn-outline-info btn-sm rounded-end-3"
				        @click="this.genKeyPair()"
				        :disabled="this.bulk"
				        type="button" id="button-addon2">
					<i class="bi bi-arrow-repeat"></i> </button>
			</div>
		</div>
		<div>
			<div class="d-flex">
				<label for="public_key" class="form-label">
					<small class="text-muted">
						<LocaleText t="Public Key"></LocaleText>
						<code>
							<LocaleText t="(Required)"></LocaleText>
						</code></small>
				</label>
				<div class="form-check form-switch ms-auto">
					<input class="form-check-input" type="checkbox" role="switch"
					       :disabled="this.bulk"
					       id="enablePublicKeyEdit" v-model="this.editKey">
					<label class="form-check-label" for="enablePublicKeyEdit">
						<small>
							<LocaleText t="Use your own Private and Public Key"></LocaleText>
						</small>
					</label>
				</div>
			</div>
			<input class="form-control-sm form-control rounded-3"
			       :class="{'is-invalid': this.error}"
			       v-model="this.keypair.publicKey"
			       @blur="this.checkMatching()" 
			       :disabled="!this.editKey || this.bulk"
			       type="text" id="public_key">
		</div>
	</div>
</template>

<style scoped>

</style>