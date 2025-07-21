import {defineStore} from "pinia";
import {ref} from "vue";
import {fetchGet, fetchPost} from "@/utilities/fetch.js";

export const DashboardClientAssignmentStore = 
	defineStore('DashboardClientAssignmentStore', () => {
		const allConfigurationsPeers = ref({})
		const assignments = ref([])
		const clients = ref({})
		const clientsRaw = ref([])
		const unassigning = ref(false)
		const assigning = ref("")
		
		const getClients = async () => {
			await fetchGet('/api/clients/allClients', {},(res) => {
				clients.value = res.data;
			})
		}
		
		const getClientsRaw = async () => {
			await fetchGet('/api/clients/allClientsRaw', {},(res) => {
				clientsRaw.value = res.data;
				console.log(clientsRaw.value)
			})
		}
		
		const getClientById = (ClientID) => {
			return Object.values(clients.value).flat().find(x => x.ClientID === ClientID)
		}
		
		const getAssignedClients = async (ConfigurationName, Peer) => {
			await fetchGet('/api/clients/assignedClients', {
				ConfigurationName: ConfigurationName,
				Peer: Peer
			}, (res) => {
				assignments.value = res.data
			})
		}

		const assignClient = async (ConfigurationName, Peer, ClientID, get=true) => {
			assigning.value = ClientID;
			await fetchPost('/api/clients/assignClient', {
				ConfigurationName: ConfigurationName,
				Peer: Peer,
				ClientID: ClientID
			}, async (res) => {
				if (res.status){
					if (get) await getAssignedClients(ConfigurationName, Peer)
					assigning.value = "";
				}else{
					assigning.value = "";
				}
			})
		}

		const unassignClient = async (ConfigurationName, Peer, AssignmentID) => {
			unassigning.value = true;
			await fetchPost('/api/clients/unassignClient', {
				AssignmentID: AssignmentID
			}, async (res) => {
				if (res.status){
					if (ConfigurationName && Peer) await getAssignedClients(ConfigurationName, Peer)
				}
				unassigning.value = false;
			})
		}

		const getAllConfigurationsPeers = async () => {
			await fetchGet("/api/clients/allConfigurationsPeers", {}, (res) => {
				allConfigurationsPeers.value = res.data
			})
		}
		
		return {
			assignments, 
			getAssignedClients, 
			getClients,
			getClientsRaw,
			clients, 
			unassignClient, 
			assignClient, 
			getClientById,
			unassigning,
			assigning,
			clientsRaw,
			allConfigurationsPeers,
			getAllConfigurationsPeers
		}
})