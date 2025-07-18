import {defineStore} from "pinia";
import {ref} from "vue";
import {fetchGet, fetchPost} from "@/utilities/fetch.js";

export const DashboardClientAssignmentStore = 
	defineStore('DashboardClientAssignmentStore', () => {
		const assignments = ref([])
		const clients = ref({})
		const unassigning = ref(false)
		const assigning = ref("")
		
		const getClients = async () => {
			await fetchGet('/api/clients/allClients', {},(res) => {
				clients.value = res.data;
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

		const assignClient = async (ConfigurationName, Peer, ClientID) => {
			assigning.value = ClientID;
			await fetchPost('/api/clients/assignClient', {
				ConfigurationName: ConfigurationName,
				Peer: Peer,
				ClientID: ClientID
			}, async (res) => {
				if (res.status){
					await getAssignedClients(ConfigurationName, Peer)
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
					await getAssignedClients(ConfigurationName, Peer)
				}
				unassigning.value = false;
			})
		}
		
		return {
			assignments, 
			getAssignedClients, 
			getClients, 
			clients, 
			unassignClient, 
			assignClient, 
			getClientById,
			unassigning,
			assigning
		}
})