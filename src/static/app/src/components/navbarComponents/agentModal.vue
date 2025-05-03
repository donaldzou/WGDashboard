<script setup>
import LocaleText from "@/components/text/localeText.vue";
import AgentContainer from "@/components/navbarComponents/agentContainer.vue";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

const emits = defineEmits(['close'])
const store = DashboardConfigurationStore()
</script>

<template>
<div class="agentContainer m-2 rounded-3 d-flex flex-column text-body" 
     :class="{'enabled': store.HelpAgent.Enable}">
	<TransitionGroup name="agent-message">
		<div key="header" class="shadow">
			<div class="p-3 d-flex gap-2 flex-column ">
				<div class="d-flex text-body" >
					<div class="d-flex flex-column align-items-start gap-1">
						<h5 class="mb-0">
							<LocaleText t="Help"></LocaleText>
						</h5>
					</div>
					<a role="button" class="ms-auto text-body" @click="emits('close')">
						<h5 class="mb-0">
							<i class="bi bi-x-lg"></i>
						</h5>
					</a>
				</div>
				<p class="mb-0">
					<LocaleText t="You can visit our: "></LocaleText>
				</p>
				<div class="list-group">
					<a href="https://donaldzou.github.io/WGDashboard-Documentation/"
					   target="_blank" class="list-group-item list-group-item-action d-flex align-items-center">
						<i class="bi bi-book-fill"></i>
						<LocaleText class="ms-auto" t="Official Documentation"></LocaleText>
					</a>
					<a target="_blank" role="button" href="https://discord.gg/72TwzjeuWm"
					   class="list-group-item list-group-item-action d-flex align-items-center">
						<i class="bi bi-discord"></i>
						<LocaleText class="ms-auto" t="Discord Server"></LocaleText>
					</a>
				</div>
			</div>
<!--			<div class="d-flex flex-column p-3 gap-2">-->
<!--				<div class="d-flex w-100">-->
<!--					<h5 class="mb-0">-->
<!--						<LocaleText t="WGDashboard Help Bot"></LocaleText>-->
<!--					</h5>-->
<!--					<div class="form-check form-switch ms-auto mb-0">-->
<!--						<input class="form-check-input"-->
<!--						       v-model="store.HelpAgent.Enable"-->
<!--						       type="checkbox" role="switch" id="enableHelpAgent">-->
<!--						<label class="form-check-label fw-bold" for="enableHelpAgent">-->
<!--							<LocaleText :t="store.HelpAgent.Enable ? 'Enabled':'Disabled'"></LocaleText>-->
<!--						</label>-->
<!--					</div>-->
<!--				</div>-->
<!--				<small class="text-muted" v-if="!store.HelpAgent.Enable">-->
<!--					By using this service, you're agreed to send your messages to a Large Language Model (LLM) hosted on DigitalOcean. Your messages will not store on the server in any type of form, you can verify it on <a href="https://github.com/donaldzou/WGDashboard-Bot-Middleware" target="_blank">here</a>. For more information, please contact me through GitHub or email.-->
<!--				</small>-->
<!--			</div>-->
		</div>
<!--		<AgentContainer key="agentContainer" v-if="store.HelpAgent.Enable"></AgentContainer>-->
	</TransitionGroup>
</div>
</template>

<style scoped>
.agentContainer{
	--agentHeight: 100vh;
	position: absolute;
	z-index: 9999;
	top: 0;
	left: 100%;
	width: 450px;
	box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.3);
	backdrop-filter: blur(8px);
	background: linear-gradient(var(--degree), #009dff52 var(--distance2), #F9464752 100%);
}

.agentContainer.enabled{
	height: calc(var(--agentHeight) - 1rem);
}

@media screen and (max-width: 768px) {
	.agentContainer{
		--agentHeight: 100vh !important;
		top: 0;
		left: 0;
		max-height: calc(var(--agentHeight) - 58px - 1rem);
		width: calc( 100% - 1rem);
	}
}

.agentChatroomBody{
	flex: 1 1 auto;
	overflow-y: auto;
	max-height: calc(var(--agentHeight) - 70px - 244px);
}
</style>