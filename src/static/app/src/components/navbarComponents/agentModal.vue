<script setup>
import {onBeforeMount, onBeforeUnmount, onMounted, reactive, ref} from "vue";
import { v4 } from "uuid"
import dayjs from "dayjs";
import AgentMessage from "@/components/navbarComponents/agentMessage.vue";
import {fetchGet} from "@/utilities/fetch.js";
import LocaleText from "@/components/text/localeText.vue";
import {GetLocale} from "@/utilities/locale.js";

const userPrompt = ref("")
const waitingMessage = ref(false)
const messages = reactive({})
const agentBaseUrl = "https://agent-aee6a811e474080613b1-ie5yg.ondigitalocean.app";
const agentChatbotId = "JrYZtArj_C5FGRts06op58QUHPFCgUzo";
const agentId = "1150ab95-025b-11f0-bf8f-4e013e2ddde4"
let refreshTokenInterval = undefined;
let agentToken = ref(undefined);
const agentHealth = ref(false);
const checkingAgentHealth = ref(false);
const scrollMessageBody = () => {
	document.querySelector(".agentChatroomBody").scrollTop = document.querySelector(".agentChatroomBody").scrollHeight
}
const newMessage = (role, content) => {
	let sentMsgId = v4().toString();
	messages[sentMsgId] = {
		id: sentMsgId,
		role: role,
		content: content,
		time: dayjs().format("YYYY-MM-DD HH:mm:ss")
	}
	return sentMsgId
}

const pushPrompt = () => {
	if (userPrompt.value){
		newMessage('user', userPrompt.value)
		userPrompt.value = "";
		waitingMessage.value = true;
		fetch(`${agentBaseUrl}/api/v1/chat/completions`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"Authorization": `Bearer ${agentToken.value.access_token}`
			},
			body: JSON.stringify({
				"include_functions_info": false,
				"include_retrieval_info": false,
				"include_guardrails_info": false,
				"stream": true,
				"messages": Object.values(messages)
			})
		}).then(response => {
			if (response.ok){
				const stream = response.body;
				const reader = stream.getReader();
				const decoder = new TextDecoder();
				let recvMsgId = newMessage('assistant', '')
				const readChunk = () => {
					reader.read()
						.then(({value, done}) => {
							if (done) {
								waitingMessage.value = false
								return
							}
							let chunkString = decoder.decode(value, {stream: true}).trim();
							chunkString = chunkString.split("\n")
							chunkString.forEach(x => {
								if (x){
									x = x.replace(/^data:\s*/, "")
									if (x !== "[DONE]"){
										let d = JSON.parse(x);
										d.choices.forEach(c => {
											if (c.delta.content){
												messages[recvMsgId].content += c.delta.content
												scrollMessageBody()
											}
										})
									}
								}
							})
							readChunk();
						})
						.catch(error => {
							waitingMessage.value = false
							messages[recvMsgId].content = "Sorry, the bot is not responding."
						});
				};
				readChunk();
			}else{
				waitingMessage.value = false;
				throw new Error("Invalid response")
			}
		});
		
	}
}

const initAgent = async () => {
	checkingAgentHealth.value = true;
	await fetch(`${agentBaseUrl}/health`, {
		signal: AbortSignal.timeout(3000)
	}).then(res => res.json()).then(res => {
		agentHealth.value = res.status === 'ok'
	}).catch(() => {
		checkingAgentHealth.value = false;
		agentHealth.value = false;
	})
	if (agentHealth.value){
		await fetch(`https://cloud.digitalocean.com/gen-ai/auth/agents/${agentId}/token`, {
			headers: {
				'Content-Type': 'application/json',
				'X-Api-Key': agentChatbotId
			},
			method: "POST",
			body: JSON.stringify({})
		}).then(res => {
			if (!res.ok){
				throw new Error('Access token not available')
			}else{
				return res.json()
			}
		}).then(res => {
			agentToken.value = res;
			checkingAgentHealth.value = false;
		}).catch(() => {
			checkingAgentHealth.value = false;
			agentHealth.value = false;
		})
	}
}

const refreshAgentToken = async () => {
	if (agentToken.value){
		await fetch(
			`https://cloud.digitalocean.com/gen-ai/auth/agents/${agentId}/token?refresh_token=${agentToken.value.refresh_token}`, {
				headers: {
					'Content-Type': 'application/json',
					'X-Api-Key': agentChatbotId
				},
				method: "PUT",
				body: JSON.stringify({})
			}).then(res => res.json()).then(res => {
				agentHealth.value = true;
				agentToken.value = res;
		}).catch(err => {
			agentHealth.value = false;
			console.log(err)
		})
	}
}

onBeforeMount(() => {
	newMessage('assistant', GetLocale('Hi! How can I help you today?'))
})

onMounted(async () => {
	await initAgent();
	refreshTokenInterval = setInterval(async () => {
		await refreshAgentToken()
	}, 60000)
})

onBeforeUnmount(() => {
	clearInterval(refreshTokenInterval);
})

const emits = defineEmits(['close'])
</script>

<template>
<div class="agentContainer m-2 rounded-3 d-flex flex-column text-body" :class="{'connected': agentHealth && !checkingAgentHealth}">
	<TransitionGroup name="agent-message">
		<div key="header" class=" shadow ">
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
			<div class="d-flex align-items-center p-3">
				<h5 class="mb-0"><LocaleText t="WGDashboard Help Bot"></LocaleText></h5>
				<h6 class="mb-0 ms-auto">
						<span class="mb-0 text-muted d-flex gap-2 align-items-center" v-if="checkingAgentHealth">
							<span class="spinner-border spinner-border-sm"></span>
							<small>
								<LocaleText t="Connecting..."></LocaleText>
							</small>
						</span>
					<span class="mb-0 d-flex gap-2 align-items-center badge"
					      :class="[agentHealth ? 'text-bg-success':'text-bg-danger']"
					      v-else>
							{{ agentHealth ? 'Connected':'Not Connected'}}
						</span>
				</h6>
			</div>
		</div>
		<div class="agentChatroomBody p-3 pb-5 d-flex flex-column gap-3 flex-grow-1"
		     key="body"
		     v-if="agentHealth && !checkingAgentHealth">
			<TransitionGroup name="agent-message">
				<AgentMessage :message="msg" v-for="(msg, index) in Object.values(messages)" :key="msg.id" :ind="index"></AgentMessage>
			</TransitionGroup>
		</div>
		<div class="d-flex text-white align-items-center p-3 gap-3 rounded-bottom-3 mt-auto"
		     key="input"
		     v-if="agentHealth && !checkingAgentHealth"
		     style="box-shadow: 1px -1rem 3rem 0 rgba(0, 0, 0, 0.175) !important">
			<input type="text" class="form-control rounded-3 bg-transparent border-0"
			       :placeholder="GetLocale('What do you want to ask?')"
			       @keyup.enter="pushPrompt"
			       v-model="userPrompt" :disabled="waitingMessage">
			<a role="button" class="agentChatroomSendButton text-body" @click="pushPrompt">
				<i class="bi bi-send-fill" v-if="!waitingMessage"></i>
				<span class="spinner-border spinner-border-sm" v-else></span>
			</a>
		</div>
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
	background: linear-gradient(var(--degree), #009dff52 var(--distance2), #ff4a0052 100%);
}

.agentContainer.connected{
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

.agent-message-move, /* apply transition to moving elements */
.agent-message-enter-active,
.agent-message-leave-active {
	transition: all 0.5s cubic-bezier(0.82, 0.58, 0.17, 1);
}
.agent-message-enter-from,
.agent-message-leave-to {
	opacity: 0;
	filter: blur(8px);
	transform: translateY(30px);
}
.agent-message-leave-active {
	position: absolute;
}
</style>