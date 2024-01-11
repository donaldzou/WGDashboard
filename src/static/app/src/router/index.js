import { createRouter, createWebHashHistory } from 'vue-router'
import {cookie} from "../utilities/cookie.js";
import Index from "@/views/index.vue"
import Signin from "@/views/signin.vue";
import ConfigurationList from "@/components/configurationList.vue";
import {fetchGet} from "@/utilities/fetch.js";
import {wgdashboardStore} from "@/stores/wgdashboardStore.js";
import Settings from "@/views/settings.vue";

const checkAuth = async () => {
  let result = false
  await fetchGet("/api/validateAuthentication", {}, (res) => {
    result = res.status
  });
  return result;
}

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      name: "Index",
      path: '/',
      component: Index,
      meta: {
        requiresAuth: true
      },
      children: [
        {
          name: "Configuration List",
          path: '',
          component: ConfigurationList
        },
        {
          name: "Settings",
          path: '/settings',
          component: Settings
        }
      ]
    },
    {
      path: '/signin', component: Signin
    }
  ]
});

router.beforeEach(async (to, from, next) => {
  const store = wgdashboardStore();
  
  if (to.meta.requiresAuth){
    if (cookie.getCookie("authToken") && await checkAuth()){
      
      console.log(to.name)
      if (!store.DashboardConfiguration){
        await store.getDashboardConfiguration()
      }
      if (!store.WireguardConfigurations && to.name !== "Configuration List"){
        await store.getWireguardConfigurations()
      }
      next()
    }else{
      next("/signin")
    }
  }else {
    next();
  }
});
export default router
