import{_,r,D as p,g as u,c as m,b as t,d as c,$ as h,a as f,j as b}from"./index-BPNEscAR.js";import{b as v}from"./browser-CjSdxGTc.js";import{L as y}from"./localeText-DX813vQA.js";const g={name:"share",components:{LocaleText:y},async setup(){const o=h(),e=r(!1),i=p(),n=r(""),s=r(void 0),l=r(new Blob);await u("/api/getDashboardTheme",{},d=>{n.value=d.data});const a=o.query.ShareID;return a===void 0||a.length===0?(s.value=void 0,e.value=!0):await u("/api/sharePeer/get",{ShareID:a},d=>{d.status?(s.value=d.data,l.value=new Blob([s.value.file],{type:"text/plain"})):s.value=void 0,e.value=!0}),{store:i,theme:n,peerConfiguration:s,blob:l}},mounted(){this.peerConfiguration&&v.toCanvas(document.querySelector("#qrcode"),this.peerConfiguration.file,o=>{o&&console.error(o)})},methods:{download(){const o=new Blob([this.peerConfiguration.file],{type:"text/plain"}),e=URL.createObjectURL(o),i=`${this.peerConfiguration.fileName}.conf`,n=document.createElement("a");n.href=e,n.download=i,n.click()}},computed:{getBlob(){return URL.createObjectURL(this.blob)}}},w=["data-bs-theme"],x={class:"m-auto text-body",style:{width:"500px"}},C={key:0,class:"text-center position-relative",style:{}},U={class:"position-absolute w-100 h-100 top-0 start-0 d-flex animate__animated animate__fadeInUp",style:{"animation-delay":"0.1s"}},I={class:"m-auto"},L={key:1,class:"d-flex align-items-center flex-column gap-3"},B={class:"h1 dashboardLogo text-center animate__animated animate__fadeInUp"},k={id:"qrcode",class:"rounded-3 shadow animate__animated animate__fadeInUp mb-3",ref:"qrcode"},D={class:"text-muted animate__animated animate__fadeInUp mb-1",style:{"animation-delay":"0.2s"}},R=["download","href"];function j(o,e,i,n,s,l){const a=b("LocaleText");return f(),m("div",{class:"container-fluid login-container-fluid d-flex main pt-5 overflow-scroll","data-bs-theme":this.theme},[t("div",x,[this.peerConfiguration?(f(),m("div",L,[t("div",B,[e[1]||(e[1]=t("h6",null,"WGDashboard",-1)),c(a,{t:"Scan QR Code with the WireGuard App to add peer"})]),t("canvas",k,null,512),t("p",D,[c(a,{t:"or click the button below to download the "}),e[2]||(e[2]=t("samp",null,".conf",-1)),c(a,{t:" file"})]),t("a",{download:this.peerConfiguration.fileName+".conf",href:l.getBlob,class:"btn btn-lg bg-primary-subtle text-primary-emphasis border-1 border-primary-subtle animate__animated animate__fadeInUp shadow-sm",style:{"animation-delay":"0.25s"}},e[3]||(e[3]=[t("i",{class:"bi bi-download"},null,-1)]),8,R)])):(f(),m("div",C,[e[0]||(e[0]=t("div",{class:"animate__animated animate__fadeInUp"},[t("h1",{style:{"font-size":"20rem",filter:"blur(1rem)","animation-duration":"7s"},class:"animate__animated animate__flash animate__infinite"},[t("i",{class:"bi bi-file-binary"})])],-1)),t("div",U,[t("h3",I,[c(a,{t:"Oh no... This link is either expired or invalid."})])])]))])],8,w)}const $=_(g,[["render",j],["__scopeId","data-v-1b44aacd"]]);export{$ as default};
