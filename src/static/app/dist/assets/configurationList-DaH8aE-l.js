import{_ as N,D as I,g as K,a as n,c as a,d as i,w as x,b as t,n as k,t as d,f as S,i as h,e as f,m as M,v as G,u as U,j as _,r as O,p as D,T as R,q as v,o as V,s as W,F as C,h as $,W as q,G as L,x as F,k as j}from"./index-CGY_8-KO.js";import{L as b}from"./localeText-FmUupiXC.js";import{_ as z}from"./protocolBadge-CIAFrzfx.js";import{C as J}from"./storageMount.vue_vue_type_style_index_0_scoped_5d74c517_lang-kivbXqln.js";const T={name:"configurationCard",components:{ProtocolBadge:z,LocaleText:b},props:{c:{Name:String,Status:Boolean,PublicKey:String,PrivateKey:String},delay:String},data(){return{configurationToggling:!1}},setup(){return{dashboardConfigurationStore:I()}},methods:{toggle(){this.configurationToggling=!0,K("/api/toggleWireguardConfiguration/",{configurationName:this.c.Name},o=>{o.status?this.dashboardConfigurationStore.newMessage("Server",`${this.c.Name} ${o.data?"is on":"is off"}`):this.dashboardConfigurationStore.newMessage("Server",o.message,"danger"),this.c.Status=o.data,this.configurationToggling=!1})}}},P=()=>{U(o=>({"6ae61cbb":o.delay}))},B=T.setup;T.setup=B?(o,e)=>(P(),B(o,e)):P;const E={class:"card conf_card rounded-3 shadow text-decoration-none"},H={class:"mb-0"},Y={class:"card-title mb-0 d-flex align-items-center gap-2"},A={class:"card-footer d-flex gap-2 flex-column"},Q={class:"row"},X={class:"col-6 col-md-3"},Z={class:"text-primary-emphasis col-6 col-md-3"},tt={class:"text-success-emphasis col-6 col-md-3"},et={class:"text-md-end col-6 col-md-3"},st={class:"d-flex align-items-center gap-2"},ot={class:"text-muted"},nt={style:{"word-break":"keep-all"}},rt={class:"mb-0 d-block d-lg-inline-block"},at={style:{"line-break":"anywhere"}},it={class:"form-check form-switch ms-auto"},lt=["for"],ct={key:4,class:"spinner-border spinner-border-sm ms-2","aria-hidden":"true"},dt=["disabled","id"];function ut(o,e,s,g,r,m){const c=_("ProtocolBadge"),u=_("RouterLink"),l=_("LocaleText");return n(),a("div",E,[i(u,{to:"/configuration/"+s.c.Name+"/peers",class:"card-body d-flex align-items-center gap-3 flex-wrap text-decoration-none"},{default:x(()=>[t("h6",H,[t("span",{class:k(["dot",{active:s.c.Status}])},null,2)]),t("h6",Y,[t("samp",null,d(s.c.Name),1),t("small",null,[i(c,{protocol:s.c.Protocol,mini:!0},null,8,["protocol"])])]),e[2]||(e[2]=t("h6",{class:"mb-0 ms-auto"},[t("i",{class:"bi bi-chevron-right"})],-1))]),_:1},8,["to"]),t("div",A,[t("div",Q,[t("small",X,[e[3]||(e[3]=t("i",{class:"bi bi-arrow-down-up me-2"},null,-1)),S(d(s.c.DataUsage.Total>0?s.c.DataUsage.Total.toFixed(4):0)+" GB ",1)]),t("small",Z,[e[4]||(e[4]=t("i",{class:"bi bi-arrow-down me-2"},null,-1)),S(d(s.c.DataUsage.Receive>0?s.c.DataUsage.Receive.toFixed(4):0)+" GB ",1)]),t("small",tt,[e[5]||(e[5]=t("i",{class:"bi bi-arrow-up me-2"},null,-1)),S(d(s.c.DataUsage.Sent>0?s.c.DataUsage.Sent.toFixed(4):0)+" GB ",1)]),t("small",et,[t("span",{class:k(["dot me-2",{active:s.c.ConnectedPeers>0}])},null,2),S(" "+d(s.c.ConnectedPeers)+" / "+d(s.c.TotalPeers)+" ",1),i(l,{t:"Peers"})])]),t("div",st,[t("small",ot,[t("strong",nt,[i(l,{t:"Public Key"})])]),t("small",rt,[t("samp",at,d(s.c.PublicKey),1)]),t("div",it,[t("label",{class:"form-check-label",style:{cursor:"pointer"},for:"switch"+s.c.PrivateKey},[!s.c.Status&&this.configurationToggling?(n(),h(l,{key:0,t:"Turning Off..."})):s.c.Status&&this.configurationToggling?(n(),h(l,{key:1,t:"Turning On..."})):s.c.Status&&!this.configurationToggling?(n(),h(l,{key:2,t:"On"})):!s.c.Status&&!this.configurationToggling?(n(),h(l,{key:3,t:"Off"})):f("",!0),this.configurationToggling?(n(),a("span",ct)):f("",!0)],8,lt),M(t("input",{class:"form-check-input",style:{cursor:"pointer"},disabled:this.configurationToggling,type:"checkbox",role:"switch",id:"switch"+s.c.PrivateKey,onChange:e[0]||(e[0]=w=>this.toggle()),"onUpdate:modelValue":e[1]||(e[1]=w=>s.c.Status=w)},null,40,dt),[[G,s.c.Status]])])])])])}const mt=N(T,[["render",ut],["__scopeId","data-v-4806af36"]]),gt={class:"text-muted me-2"},ht={class:"fw-bold"},_t={__name:"storageMount",props:{mount:String,percentage:Number,align:Boolean,square:Boolean},setup(o){U(r=>({"703ec95e":g.value}));const e=o,s=O(!1),g=D(()=>e.square?"40px":"25px");return(r,m)=>(n(),a("div",{class:"flex-grow-1 square rounded-3 border position-relative",onMouseenter:m[0]||(m[0]=c=>s.value=!0),onMouseleave:m[1]||(m[1]=c=>s.value=!1),style:v({"background-color":`rgb(25 135 84 / ${o.percentage}%)`})},[i(R,{name:"zoomReversed"},{default:x(()=>[s.value?(n(),a("div",{key:0,style:{"white-space":"nowrap"},class:k(["floatingLabel z-3 border position-absolute d-block p-1 px-2 bg-body text-body rounded-3 border shadow d-flex",[o.align?"end-0":"start-0"]])},[t("small",gt,[t("samp",null,d(o.mount),1)]),t("small",ht,d(o.percentage)+"% ",1)],2)):f("",!0)]),_:1})],36))}},ft=N(_t,[["__scopeId","data-v-5d74c517"]]),pt={class:"row text-body g-3 mb-5"},bt={class:"col-md-6 col-sm-12 col-xl-3"},yt={class:"d-flex align-items-center"},St={class:"text-muted"},vt={class:"ms-auto"},xt={key:0},kt={key:1,class:"spinner-border spinner-border-sm"},wt={class:"progress",role:"progressbar",style:{height:"6px"}},Ct={class:"d-flex mt-2 gap-1"},$t={class:"col-md-6 col-sm-12 col-xl-3"},Nt={class:"d-flex align-items-center"},Lt={class:"text-muted"},Tt={class:"ms-auto"},Pt={key:0},Bt={key:1,class:"spinner-border spinner-border-sm"},It={class:"progress",role:"progressbar",style:{height:"6px"}},Kt={class:"d-flex mt-2 gap-1"},Mt={class:"col-md-6 col-sm-12 col-xl-3"},Ut={class:"d-flex align-items-center"},Dt={class:"text-muted"},Gt={class:"ms-auto"},Ot={key:0},Rt={key:1,class:"spinner-border spinner-border-sm"},Vt={class:"progress",role:"progressbar",style:{height:"6px"}},Wt={class:"col-md-6 col-sm-12 col-xl-3"},qt={class:"d-flex align-items-center"},Ft={class:"text-muted"},jt={class:"ms-auto"},zt={key:0},Jt={key:1,class:"spinner-border spinner-border-sm"},Et={class:"progress",role:"progressbar",style:{height:"6px"}},Ht={__name:"systemStatusWidget",setup(o){const e=I();let s=null;V(()=>{g(),s=setInterval(()=>{g()},5e3)}),W(()=>{clearInterval(s)});const g=()=>{K("/api/systemStatus",{},m=>{e.SystemStatus=m.data})},r=D(()=>e.SystemStatus);return(m,c)=>(n(),a("div",pt,[t("div",bt,[t("div",yt,[t("h6",St,[c[0]||(c[0]=t("i",{class:"bi bi-cpu-fill me-2"},null,-1)),i(b,{t:"CPU"})]),t("h6",vt,[r.value?(n(),a("span",xt,d(r.value.cpu.cpu_percent)+"% ",1)):(n(),a("span",kt))])]),t("div",wt,[t("div",{class:"progress-bar",style:v({width:`${r.value?.cpu.cpu_percent}%`})},null,4)]),t("div",Ct,[(n(!0),a(C,null,$(r.value?.cpu.cpu_percent_per_cpu,(u,l)=>(n(),h(J,{key:l,align:l+1>Math.round(r.value?.cpu.cpu_percent_per_cpu.length/2),core_number:l,percentage:u},null,8,["align","core_number","percentage"]))),128))])]),t("div",$t,[t("div",Nt,[t("h6",Lt,[c[1]||(c[1]=t("i",{class:"bi bi-device-ssd-fill me-2"},null,-1)),i(b,{t:"Storage"})]),t("h6",Tt,[r.value?(n(),a("span",Pt,d(r.value?.disk["/"].percent)+"% ",1)):(n(),a("span",Bt))])]),t("div",It,[t("div",{class:"progress-bar bg-success",style:v({width:`${r.value?.disk["/"].percent}%`})},null,4)]),t("div",Kt,[r.value?(n(!0),a(C,{key:0},$(Object.keys(r.value?.disk),(u,l)=>(n(),h(ft,{key:l,align:l+1>Math.round(Object.keys(r.value?.disk).length/2),mount:u,percentage:r.value?.disk[u].percent},null,8,["align","mount","percentage"]))),128)):f("",!0)])]),t("div",Mt,[t("div",Ut,[t("h6",Dt,[c[2]||(c[2]=t("i",{class:"bi bi-memory me-2"},null,-1)),i(b,{t:"Memory"})]),t("h6",Gt,[r.value?(n(),a("span",Ot,d(r.value?.memory.virtual_memory.percent)+"% ",1)):(n(),a("span",Rt))])]),t("div",Vt,[t("div",{class:"progress-bar bg-info",style:v({width:`${r.value?.memory.virtual_memory.percent}%`})},null,4)])]),t("div",Wt,[t("div",qt,[t("h6",Ft,[c[3]||(c[3]=t("i",{class:"bi bi-memory me-2"},null,-1)),i(b,{t:"Swap Memory"})]),t("h6",jt,[r.value?(n(),a("span",zt,d(r.value?.memory.swap_memory.percent)+"% ",1)):(n(),a("span",Jt))])]),t("div",Et,[t("div",{class:"progress-bar bg-warning",style:v({width:`${r.value?.memory.swap_memory.percent}%`})},null,4)])])]))}},Yt=N(Ht,[["__scopeId","data-v-435b92ba"]]),At={name:"configurationList",components:{SystemStatus:Yt,LocaleText:b,ConfigurationCard:mt},async setup(){return{wireguardConfigurationsStore:q()}},data(){return{configurationLoaded:!1,sort:{Name:L("Name"),Status:L("Status"),"DataUsage.Total":L("Total Usage")},currentSort:{key:"Name",order:"asc"},searchKey:""}},async mounted(){window.localStorage.getItem("ConfigurationListSort")?this.currentSort=JSON.parse(window.localStorage.getItem("ConfigurationListSort")):window.localStorage.setItem("ConfigurationListSort",JSON.stringify(this.currentSort)),await this.wireguardConfigurationsStore.getConfigurations(),this.configurationLoaded=!0,this.wireguardConfigurationsStore.ConfigurationListInterval=setInterval(()=>{this.wireguardConfigurationsStore.getConfigurations()},1e4)},beforeUnmount(){clearInterval(this.wireguardConfigurationsStore.ConfigurationListInterval)},computed:{configurations(){return[...this.wireguardConfigurationsStore.Configurations].filter(o=>o.Name.includes(this.searchKey)||o.PublicKey.includes(this.searchKey)||!this.searchKey).sort((o,e)=>this.currentSort.order==="desc"?this.dotNotation(o,this.currentSort.key)<this.dotNotation(e,this.currentSort.key)?1:this.dotNotation(o,this.currentSort.key)>this.dotNotation(e,this.currentSort.key)?-1:0:this.dotNotation(o,this.currentSort.key)>this.dotNotation(e,this.currentSort.key)?1:this.dotNotation(o,this.currentSort.key)<this.dotNotation(e,this.currentSort.key)?-1:0)}},methods:{dotNotation(o,e){return e.split(".").reduce((s,g)=>s&&s[g],o)},updateSort(o){this.currentSort.key===o?this.currentSort.order==="asc"?this.currentSort.order="desc":this.currentSort.order="asc":this.currentSort.key=o,window.localStorage.setItem("ConfigurationListSort",JSON.stringify(this.currentSort))}}},Qt={class:"mt-md-5 mt-3"},Xt={class:"container-md"},Zt={class:"d-flex mb-4 configurationListTitle align-items-md-center gap-3 flex-column flex-md-row"},te={class:"text-body d-flex mb-0"},ee={key:0,class:"text-body filter mb-3 d-flex gap-2 flex-column flex-md-row"},se={class:"d-flex align-items-center gap-3 align-items-center mb-3 mb-md-0"},oe={class:"text-muted"},ne={class:"d-flex ms-auto ms-lg-0"},re=["onClick"],ae={class:"d-flex align-items-center ms-md-auto"},ie={class:"text-muted",key:"noConfiguration"};function le(o,e,s,g,r,m){const c=_("SystemStatus"),u=_("LocaleText"),l=_("RouterLink"),w=_("ConfigurationCard");return n(),a("div",Qt,[t("div",Xt,[i(c),t("div",Zt,[t("h2",te,[i(u,{t:"WireGuard Configurations"})]),i(l,{to:"/new_configuration",class:"ms-md-auto py-2 text-decoration-none btn text-primary-emphasis bg-primary-subtle rounded-3 border-1 border-primary-subtle"},{default:x(()=>[e[1]||(e[1]=t("i",{class:"bi bi-plus-circle me-2"},null,-1)),i(u,{t:"Configuration"})]),_:1}),i(l,{to:"/restore_configuration",class:"py-2 text-decoration-none btn text-primary-emphasis bg-primary-subtle rounded-3 border-1 border-primary-subtle"},{default:x(()=>[e[2]||(e[2]=t("i",{class:"bi bi-clock-history me-2"},null,-1)),i(u,{t:"Restore"})]),_:1})]),this.configurationLoaded?(n(),a("div",ee,[t("div",se,[t("small",oe,[i(u,{t:"Sort By"})]),t("div",ne,[(n(!0),a(C,null,$(this.sort,(p,y)=>(n(),a("a",{role:"button",onClick:ce=>m.updateSort(y),class:k([{"bg-primary-subtle text-primary-emphasis":this.currentSort.key===y},"px-2 py-1 rounded-3"])},[t("small",null,[this.currentSort.key===y?(n(),a("i",{key:0,class:k(["bi me-2",[this.currentSort.order==="asc"?"bi-sort-up":"bi-sort-down"]])},null,2)):f("",!0),S(d(p),1)])],10,re))),256))])]),t("div",ae,[e[3]||(e[3]=t("label",{for:"configurationSearch",class:"text-muted"},[t("i",{class:"bi bi-search me-2"})],-1)),M(t("input",{class:"form-control form-control-sm rounded-3","onUpdate:modelValue":e[0]||(e[0]=p=>this.searchKey=p),id:"configurationSearch"},null,512),[[F,this.searchKey]])])])):f("",!0),i(j,{name:"fade",tag:"div",class:"d-flex flex-column gap-3 mb-4"},{default:x(()=>[this.configurationLoaded&&this.wireguardConfigurationsStore.Configurations.length===0?(n(),a("p",ie,[i(u,{t:"You don't have any WireGuard configurations yet. Please check the configuration folder or change it in Settings. By default the folder is /etc/wireguard."})])):this.configurationLoaded?(n(!0),a(C,{key:1},$(m.configurations,(p,y)=>(n(),h(w,{delay:y*.05+"s",key:p.Name,c:p},null,8,["delay","c"]))),128)):f("",!0)]),_:1})])])}const he=N(At,[["render",le],["__scopeId","data-v-8300994b"]]);export{he as default};
