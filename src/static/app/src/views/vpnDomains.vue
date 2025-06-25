<script>
import {fetchGet, fetchPost} from "@/utilities/fetch.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import LocaleText from "@/components/text/localeText.vue";

export default {
        name: "vpnDomains",
        components: {LocaleText},
        setup(){
                const store = DashboardConfigurationStore();
                return {store};
        },
        data(){
                return {
                        domains: [],
                        newDomain: "",
                        saving: false,
                        loading: true,
                        editIndex: null
                }
        },
        mounted(){
                this.load();
        },
        methods:{
                load(){
                        fetchGet("/api/vpnDomains", {}, (res)=>{
                                if(res.status){
                                        this.domains = res.data;
                                }else{
                                        this.store.newMessage("Server", res.message, "danger");
                                }
                                this.loading = false;
                        })
                },
                add(){
                        if(this.newDomain.trim().length){
                                this.domains.push({domain:this.newDomain.trim(), ip:""});
                                this.newDomain = "";
                        }
                },
                save(){
                        this.saving = true;
                        fetchPost("/api/vpnDomains", {domains:this.domains}, (res)=>{
                                if(res.status){
                                        this.store.newMessage("Server", "Save", "success");
                                }else{
                                        this.store.newMessage("Server", res.message, "danger");
                                }
                                this.saving = false;
                        })
                },
                deleteDomain(i){
                        this.domains.splice(i,1);
                }
        }
}
</script>

<template>
        <div class="mt-md-5 mt-3 text-body mb-3">
                <div class="container">
                        <h3 class="mb-3"><LocaleText t="VPN Domains"></LocaleText></h3>
                        <div class="input-group mb-3">
                                <input class="form-control" type="text" v-model="newDomain"/>
                                <button class="btn btn-success" @click="add">
                                        <i class="bi bi-plus-circle-fill me-2"></i>
                                        <LocaleText t="Add"></LocaleText>
                                </button>
                                <button class="btn btn-primary" @click="save" :disabled="saving">
                                        <span v-if="!saving">
                                                <i class="bi bi-save-fill me-2"></i>
                                                <LocaleText t="Save"></LocaleText>
                                        </span>
                                        <span v-else class="spinner-border spinner-border-sm" role="status"></span>
                                </button>
                        </div>
                        <ul class="list-group" v-if="!loading">
                                <li class="list-group-item d-flex justify-content-between align-items-center" v-for="(d,i) in domains" :key="i">
                                        <span>{{d.domain}} - {{d.ip}}</span>
                                        <div class="d-flex gap-2">
                                                <a role="button" class="text-danger" @click="deleteDomain(i)"><i class="bi bi-trash-fill"></i></a>
                                        </div>
                                </li>
                        </ul>
                </div>
        </div>
</template>

<style scoped>
</style>
