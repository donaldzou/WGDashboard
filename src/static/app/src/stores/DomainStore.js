import {defineStore} from "pinia";
import {fetchGet, fetchPost} from "@/utilities/fetch.js";

export const DomainStore = defineStore('DomainStore', {
    state: () => ({
        domains: []
    }),
    actions: {
        async load(){
            await fetchGet('/api/getDomains', {}, (res) => {
                if(res.status) this.domains = res.data
            })
        },
        async add(domain){
            await fetchPost('/api/addDomain', {domain}, (res) => {
                if(res.status) this.domains = res.data
            })
        }
    }
});
