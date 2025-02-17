import{_ as m,D as _,z as c,j as b,a as n,c as r,b as e,d as a,t as h,m as d,x as l,n as f,$ as v,a5 as u,e as p}from"./index-CB1eX1Wm.js";import{L as g}from"./localeText-DIJr90Fd.js";const y={name:"peerSettings",components:{LocaleText:g},props:{selectedPeer:Object},data(){return{data:void 0,dataChanged:!1,showKey:!1,saving:!1}},setup(){return{dashboardConfigurationStore:_()}},methods:{reset(){this.selectedPeer&&(this.data=JSON.parse(JSON.stringify(this.selectedPeer)),this.dataChanged=!1)},savePeer(){this.saving=!0,c(`/api/updatePeerSettings/${this.$route.params.id}`,this.data,i=>{this.saving=!1,i.status?this.dashboardConfigurationStore.newMessage("Server","Peer saved","success"):this.dashboardConfigurationStore.newMessage("Server",i.message,"danger"),this.$emit("refresh")})},resetPeerData(i){this.saving=!0,c(`/api/resetPeerData/${this.$route.params.id}`,{id:this.data.id,type:i},t=>{this.saving=!1,t.status?this.dashboardConfigurationStore.newMessage("Server","Peer data usage reset successfully","success"):this.dashboardConfigurationStore.newMessage("Server",t.message,"danger"),this.$emit("refresh")})}},beforeMount(){this.reset()},mounted(){this.$el.querySelectorAll("input").forEach(i=>{i.addEventListener("change",()=>{this.dataChanged=!0})})}},x={class:"peerSettingContainer w-100 h-100 position-absolute top-0 start-0 overflow-y-scroll"},w={class:"container d-flex h-100 w-100"},S={class:"m-auto modal-dialog-centered dashboardModal"},k={class:"card rounded-3 shadow flex-grow-1"},C={class:"card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4 pb-2"},P={class:"mb-0"},$={key:0,class:"card-body px-4"},D={class:"d-flex flex-column gap-2 mb-4"},V={class:"d-flex align-items-center"},U={class:"text-muted"},N={class:"ms-auto"},K={for:"peer_name_textbox",class:"form-label"},M={class:"text-muted"},A=["disabled"],O={class:"d-flex position-relative"},R={for:"peer_private_key_textbox",class:"form-label"},T={class:"text-muted"},L=["type","disabled"],q={for:"peer_allowed_ip_textbox",class:"form-label"},E={class:"text-muted"},B=["disabled"],I={for:"peer_endpoint_allowed_ips",class:"form-label"},j={class:"text-muted"},z=["disabled"],J={for:"peer_DNS_textbox",class:"form-label"},Q={class:"text-muted"},F=["disabled"],G={class:"accordion my-3",id:"peerSettingsAccordion"},H={class:"accordion-item"},W={class:"accordion-header"},X={class:"accordion-button rounded-3 collapsed",type:"button","data-bs-toggle":"collapse","data-bs-target":"#peerSettingsAccordionOptional"},Y={id:"peerSettingsAccordionOptional",class:"accordion-collapse collapse","data-bs-parent":"#peerSettingsAccordion"},Z={class:"accordion-body d-flex flex-column gap-2 mb-2"},ee={for:"peer_preshared_key_textbox",class:"form-label"},te={class:"text-muted"},se=["disabled"],oe={for:"peer_mtu",class:"form-label"},ae={class:"text-muted"},de=["disabled"],ie={for:"peer_keep_alive",class:"form-label"},le={class:"text-muted"},ne=["disabled"],re={key:0},ce={for:"peer_advance_security",class:"form-label d-block"},ue={class:"text-muted"},pe={class:"btn-group",role:"group"},me={class:"btn btn-outline-primary btn-sm",for:"advanced_security_on"},_e={class:"btn btn-outline-primary btn-sm",for:"advanced_security_off"},be={class:"d-flex align-items-center gap-2"},he=["disabled"],fe=["disabled"],ve={class:"d-flex gap-2 align-items-center"},ge={class:"d-flex gap-2 ms-auto"};function ye(i,t,xe,we,Se,ke){const o=b("LocaleText");return n(),r("div",x,[e("div",w,[e("div",S,[e("div",k,[e("div",C,[e("h4",P,[a(o,{t:"Peer Settings"})]),e("button",{type:"button",class:"btn-close ms-auto",onClick:t[0]||(t[0]=s=>this.$emit("close"))})]),this.data?(n(),r("div",$,[e("div",D,[e("div",V,[e("small",U,[a(o,{t:"Public Key"})]),e("small",N,[e("samp",null,h(this.data.id),1)])]),e("div",null,[e("label",K,[e("small",M,[a(o,{t:"Name"})])]),d(e("input",{type:"text",class:"form-control form-control-sm rounded-3",disabled:this.saving,"onUpdate:modelValue":t[1]||(t[1]=s=>this.data.name=s),id:"peer_name_textbox",placeholder:""},null,8,A),[[l,this.data.name]])]),e("div",null,[e("div",O,[e("label",R,[e("small",T,[a(o,{t:"Private Key"}),e("code",null,[a(o,{t:"(Required for QR Code and Download)"})])])]),e("a",{role:"button",class:"ms-auto text-decoration-none toggleShowKey",onClick:t[2]||(t[2]=s=>this.showKey=!this.showKey)},[e("i",{class:f(["bi",[this.showKey?"bi-eye-slash-fill":"bi-eye-fill"]])},null,2)])]),d(e("input",{type:[this.showKey?"text":"password"],class:"form-control form-control-sm rounded-3",disabled:this.saving,"onUpdate:modelValue":t[3]||(t[3]=s=>this.data.private_key=s),id:"peer_private_key_textbox",style:{"padding-right":"40px"}},null,8,L),[[v,this.data.private_key]])]),e("div",null,[e("label",q,[e("small",E,[a(o,{t:"Allowed IPs"}),e("code",null,[a(o,{t:"(Required)"})])])]),d(e("input",{type:"text",class:"form-control form-control-sm rounded-3",disabled:this.saving,"onUpdate:modelValue":t[4]||(t[4]=s=>this.data.allowed_ip=s),id:"peer_allowed_ip_textbox"},null,8,B),[[l,this.data.allowed_ip]])]),e("div",null,[e("label",I,[e("small",j,[a(o,{t:"Endpoint Allowed IPs"}),e("code",null,[a(o,{t:"(Required)"})])])]),d(e("input",{type:"text",class:"form-control form-control-sm rounded-3",disabled:this.saving,"onUpdate:modelValue":t[5]||(t[5]=s=>this.data.endpoint_allowed_ip=s),id:"peer_endpoint_allowed_ips"},null,8,z),[[l,this.data.endpoint_allowed_ip]])]),e("div",null,[e("label",J,[e("small",Q,[a(o,{t:"DNS"})])]),d(e("input",{type:"text",class:"form-control form-control-sm rounded-3",disabled:this.saving,"onUpdate:modelValue":t[6]||(t[6]=s=>this.data.DNS=s),id:"peer_DNS_textbox"},null,8,F),[[l,this.data.DNS]])]),e("div",G,[e("div",H,[e("h2",W,[e("button",X,[a(o,{t:"Optional Settings"})])]),e("div",Y,[e("div",Z,[e("div",null,[e("label",ee,[e("small",te,[a(o,{t:"Pre-Shared Key"})])]),d(e("input",{type:"text",class:"form-control form-control-sm rounded-3",disabled:this.saving,"onUpdate:modelValue":t[7]||(t[7]=s=>this.data.preshared_key=s),id:"peer_preshared_key_textbox"},null,8,se),[[l,this.data.preshared_key]])]),e("div",null,[e("label",oe,[e("small",ae,[a(o,{t:"MTU"})])]),d(e("input",{type:"number",class:"form-control form-control-sm rounded-3",disabled:this.saving,"onUpdate:modelValue":t[8]||(t[8]=s=>this.data.mtu=s),id:"peer_mtu"},null,8,de),[[l,this.data.mtu]])]),e("div",null,[e("label",ie,[e("small",le,[a(o,{t:"Persistent Keepalive"})])]),d(e("input",{type:"number",class:"form-control form-control-sm rounded-3",disabled:this.saving,"onUpdate:modelValue":t[9]||(t[9]=s=>this.data.keepalive=s),id:"peer_keep_alive"},null,8,ne),[[l,this.data.keepalive]])]),this.data.advanced_security?(n(),r("div",re,[e("label",ce,[e("small",ue,[a(o,{t:"Advanced Security"})])]),e("div",pe,[d(e("input",{type:"radio",class:"btn-check","onUpdate:modelValue":t[10]||(t[10]=s=>this.data.advanced_security=s),value:"on",name:"advanced_security_radio",id:"advanced_security_on",autocomplete:"off"},null,512),[[u,this.data.advanced_security]]),e("label",me,[a(o,{t:"On"})]),d(e("input",{type:"radio","onUpdate:modelValue":t[11]||(t[11]=s=>this.data.advanced_security=s),value:"off",class:"btn-check",name:"advanced_security_radio",id:"advanced_security_off",autocomplete:"off"},null,512),[[u,this.data.advanced_security]]),e("label",_e,[a(o,{t:"Off"})])])])):p("",!0)])])])]),e("div",be,[e("button",{class:"btn bg-secondary-subtle border-secondary-subtle text-secondary-emphasis rounded-3 shadow ms-auto px-3 py-2",onClick:t[12]||(t[12]=s=>this.reset()),disabled:!this.dataChanged||this.saving},[t[17]||(t[17]=e("i",{class:"bi bi-arrow-clockwise me-2"},null,-1)),a(o,{t:"Reset"})],8,he),e("button",{class:"btn bg-primary-subtle border-primary-subtle text-primary-emphasis rounded-3 px-3 py-2 shadow",disabled:!this.dataChanged||this.saving,onClick:t[13]||(t[13]=s=>this.savePeer())},[t[18]||(t[18]=e("i",{class:"bi bi-save-fill me-2"},null,-1)),a(o,{t:"Save"})],8,fe)]),t[22]||(t[22]=e("hr",null,null,-1)),e("div",ve,[e("strong",null,[a(o,{t:"Reset Data Usage"})]),e("div",ge,[e("button",{class:"btn bg-primary-subtle text-primary-emphasis rounded-3 flex-grow-1 shadow-sm",onClick:t[14]||(t[14]=s=>this.resetPeerData("total"))},[t[19]||(t[19]=e("i",{class:"bi bi-arrow-down-up me-2"},null,-1)),a(o,{t:"Total"})]),e("button",{class:"btn bg-primary-subtle text-primary-emphasis rounded-3 flex-grow-1 shadow-sm",onClick:t[15]||(t[15]=s=>this.resetPeerData("receive"))},[t[20]||(t[20]=e("i",{class:"bi bi-arrow-down me-2"},null,-1)),a(o,{t:"Received"})]),e("button",{class:"btn bg-primary-subtle text-primary-emphasis rounded-3 flex-grow-1 shadow-sm",onClick:t[16]||(t[16]=s=>this.resetPeerData("sent"))},[t[21]||(t[21]=e("i",{class:"bi bi-arrow-up me-2"},null,-1)),a(o,{t:"Sent"})])])])])])):p("",!0)])])])])}const $e=m(y,[["render",ye],["__scopeId","data-v-2166fcf9"]]);export{$e as default};
