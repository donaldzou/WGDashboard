import{S as _}from"./schedulePeerJob-C5YbygAh.js";import{_ as g,W as v,j as c,a as t,c as r,b as e,d as l,F as p,h as b,t as m,e as f,i as y}from"./index-CGY_8-KO.js";import{L as x}from"./localeText-FmUupiXC.js";import"./vue-datepicker-BIlY3Ss2.js";import"./dayjs.min-BZb_e7nw.js";const J={name:"peerJobsAllModal",setup(){return{store:v()}},components:{LocaleText:x,SchedulePeerJob:_},props:{configurationPeers:Array[Object]},computed:{getAllJobs(){return this.configurationPeers.filter(a=>a.jobs.length>0)}}},w={class:"peerSettingContainer w-100 h-100 position-absolute top-0 start-0 overflow-y-scroll"},$={class:"container d-flex h-100 w-100"},k={class:"m-auto modal-dialog-centered dashboardModal"},A={class:"card rounded-3 shadow",style:{width:"900px"}},L={class:"card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4 pb-2"},S={class:"mb-0 fw-normal"},j={class:"card-body px-4 pb-4 pt-2"},C={key:0,class:"accordion",id:"peerJobsLogsModalAccordion"},P={class:"accordion-header"},M=["data-bs-target"],B={key:0},N={class:"text-muted"},D=["id"],T={class:"accordion-body"},V={key:1,class:"card shadow-sm",style:{height:"153px"}},F={class:"card-body text-muted text-center d-flex"},O={class:"m-auto"};function W(a,o,E,I,R,q){const n=c("LocaleText"),u=c("SchedulePeerJob");return t(),r("div",w,[e("div",$,[e("div",k,[e("div",A,[e("div",L,[e("h4",S,[l(n,{t:"All Active Jobs"})]),e("button",{type:"button",class:"btn-close ms-auto",onClick:o[0]||(o[0]=s=>this.$emit("close"))})]),e("div",j,[e("button",{class:"btn bg-primary-subtle border-1 border-primary-subtle text-primary-emphasis rounded-3 shadow mb-2",onClick:o[1]||(o[1]=s=>this.$emit("allLogs"))},[o[4]||(o[4]=e("i",{class:"bi bi-clock me-2"},null,-1)),l(n,{t:"Logs"})]),this.getAllJobs.length>0?(t(),r("div",C,[(t(!0),r(p,null,b(this.getAllJobs,(s,d)=>(t(),r("div",{class:"accordion-item",key:s.id},[e("h2",P,[e("button",{class:"accordion-button collapsed",type:"button","data-bs-toggle":"collapse","data-bs-target":"#collapse_"+d},[e("small",null,[e("strong",null,[s.name?(t(),r("span",B,m(s.name)+" • ",1)):f("",!0),e("samp",N,m(s.id),1)])])],8,M)]),e("div",{id:"collapse_"+d,class:"accordion-collapse collapse","data-bs-parent":"#peerJobsLogsModalAccordion"},[e("div",T,[(t(!0),r(p,null,b(s.jobs,i=>(t(),y(u,{onDelete:o[2]||(o[2]=h=>this.$emit("refresh")),onRefresh:o[3]||(o[3]=h=>this.$emit("refresh")),dropdowns:this.store.PeerScheduleJobs.dropdowns,viewOnly:!0,key:i.JobID,pjob:i},null,8,["dropdowns","pjob"]))),128))])],8,D)]))),128))])):(t(),r("div",V,[e("div",F,[e("span",O,[l(n,{t:"No active job at the moment."})])])]))])])])])])}const U=g(J,[["render",W]]);export{U as default};
