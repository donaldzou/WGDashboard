<script>
import {DomainStore} from "@/stores/DomainStore.js";
import LocaleText from "@/components/text/localeText.vue";

export default {
        name: "domainList",
        components: {LocaleText},
        setup(){
                const store = DomainStore();
                return {store};
        },
        data(){
                return {
                        newDomain: ""
                }
        },
        mounted() {
                this.store.load();
        },
        methods:{
                async add(){
                        if(this.newDomain.length === 0) return;
                        await this.store.add(this.newDomain);
                        this.newDomain = "";
                }
        }
}
</script>

<template>
        <div class="card rounded-3">
                <div class="card-header">
                        <h6 class="my-2">
                                <LocaleText t="Domains"></LocaleText>
                        </h6>
                </div>
                <div class="card-body d-flex flex-column gap-2">
                        <div class="input-group">
                                <input type="text" class="form-control" v-model="newDomain">
                                <button class="btn btn-primary" @click="add">
                                        <LocaleText t="Add"></LocaleText>
                                </button>
                        </div>
                        <ul class="list-group">
                                <li class="list-group-item" v-for="d in store.domains" :key="d">{{d}}</li>
                        </ul>
                </div>
        </div>
</template>

<style scoped>
</style>
