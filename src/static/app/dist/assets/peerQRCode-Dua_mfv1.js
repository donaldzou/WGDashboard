import{b as r}from"./browser-CjSdxGTc.js";import{L as i}from"./localeText-DIJr90Fd.js";import{_ as c,D as l,g as p,j as _,a,c as n,b as e,d as m,n as h,e as u}from"./index-CB1eX1Wm.js";const f={name:"peerQRCode",components:{LocaleText:i},props:{selectedPeer:Object},setup(){return{dashboardStore:l()}},data(){return{loading:!0}},mounted(){p("/api/downloadPeer/"+this.$route.params.id,{id:this.selectedPeer.id},t=>{this.loading=!1,t.status?r.toCanvas(document.querySelector("#qrcode"),t.data.file,s=>{s&&console.error(s)}):this.dashboardStore.newMessage("Server",t.message,"danger")})}},b={class:"peerSettingContainer w-100 h-100 position-absolute top-0 start-0"},g={class:"container d-flex h-100 w-100"},v={class:"m-auto modal-dialog-centered dashboardModal justify-content-center"},x={class:"card rounded-3 shadow"},C={class:"card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4 pb-0"},w={class:"mb-0"},y={class:"card-body p-4"},S={style:{width:"292px",height:"292px"},class:"d-flex"},L={key:0,class:"spinner-border m-auto",role:"status"};function $(t,s,k,j,o,q){const d=_("LocaleText");return a(),n("div",b,[e("div",g,[e("div",v,[e("div",x,[e("div",C,[e("h4",w,[m(d,{t:"QR Code"})]),e("button",{type:"button",class:"btn-close ms-auto",onClick:s[0]||(s[0]=B=>this.$emit("close"))})]),e("div",y,[e("div",S,[e("canvas",{id:"qrcode",class:h(["rounded-3 shadow animate__animated animate__fadeIn animate__faster",{"d-none":o.loading}])},null,2),o.loading?(a(),n("div",L,s[1]||(s[1]=[e("span",{class:"visually-hidden"},"Loading...",-1)]))):u("",!0)])])])])])])}const R=c(f,[["render",$]]);export{R as default};
