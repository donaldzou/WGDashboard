<script setup>
import {computed, onBeforeMount, onBeforeUnmount, onMounted, reactive, ref} from "vue";
import { v4 } from "uuid"
import dayjs from "dayjs";
import AgentMessage from "@/components/navbarComponents/agentMessage.vue";
import LocaleText from "@/components/text/localeText.vue";
import {GetLocale} from "@/utilities/locale.js";

const userPrompt = ref("")
const waitingMessage = ref(false)
const messages = reactive({})
const agentBaseUrl = "https://wgdashboard-bot-middleware-5xqq9.ondigitalocean.app";
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

const validMessages = computed(() => {
	return Object.values(messages).filter(x => x.content)
})

const pushPrompt = () => {
	if (userPrompt.value){
		newMessage('user', userPrompt.value)
		userPrompt.value = "";
		waitingMessage.value = true;
		let recvMsgId = newMessage('assistant', '')
		fetch(`${agentBaseUrl}/api/completion`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({
				"messages": validMessages.value
			})
		}).then(response => {
			if (response.ok){
				const stream = response.body;
				const reader = stream.getReader();
				const decoder = new TextDecoder();
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
									let d = JSON.parse(x);
									if (d.status){
										if (d.data !== "[DONE]"){
											d.data.choices.forEach(c => {
												if (c.delta.content){
													messages[recvMsgId].content += c.delta.content
													scrollMessageBody()
												}
											})
										}
									}else{
										throw new Error(d.message)
									}
								}
							})
							readChunk();
						})
						.catch((err) => {
							console.log(err)
							waitingMessage.value = false
							messages[recvMsgId].content = "Sorry, the bot is not responding."
						});
				};
				readChunk();
			}else{
				waitingMessage.value = false;
				throw new Error("Invalid response")
			}
		}).catch(() => {
			waitingMessage.value = false
			messages[recvMsgId].content = "Sorry, the bot is not responding."
		});

	}
}

const initAgent = async () => {
	checkingAgentHealth.value = true;
	await fetch(`${agentBaseUrl}/api/health`, {
		signal: AbortSignal.timeout(3000)
	}).then(res => res.json()).then(res => {
		agentHealth.value = res.status === 'ok'
		checkingAgentHealth.value = false;
	}).catch(() => {
		checkingAgentHealth.value = false;
		agentHealth.value = false;
	})
}

onBeforeMount(() => {
	newMessage('assistant', GetLocale('Hi! How can I help you today?'))
})
onMounted(async () => {
	await initAgent();
})
</script>

<template>
	<div class="flex-grow-1 d-flex flex-column">
		<div class="p-1 text-center shadow" 
		     :class="
		        {'text-bg-secondary': checkingAgentHealth, 'text-bg-success': !checkingAgentHealth && agentHealth}">
			<small>
				<LocaleText t="Connecting..." v-if="checkingAgentHealth"></LocaleText>
				<LocaleText :t="agentHealth ? 'Connected':'Not Connected'" v-else></LocaleText>
			</small>
		</div>
		<Transition name="agent-message">
			<div class="agentChatroomBody p-3 pb-5 d-flex flex-column gap-3 flex-grow-1"
			     v-if="agentHealth && !checkingAgentHealth"
			     key="body"
			>
				<TransitionGroup name="agent-message">
					<AgentMessage :message="msg" v-for="(msg, index) in validMessages" :key="msg.id" :ind="index"></AgentMessage>
				</TransitionGroup>
			</div>
		</Transition>
		<Transition name="agent-message">
			<div class="d-flex text-white align-items-center p-3 gap-3 rounded-bottom-3 mt-auto"
			     v-if="agentHealth && !checkingAgentHealth"
			     key="input"
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
		</Transition>
	</div>
</template>

<style scoped>

</style>