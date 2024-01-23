import { createRouter, createWebHashHistory } from 'vue-router'
import {cookie} from "../utilities/cookie.js";
import Index from "@/views/index.vue"
import Signin from "@/views/signin.vue";
import ConfigurationList from "@/components/configurationList.vue";
import {fetchGet} from "@/utilities/fetch.js";
import {wgdashboardStore} from "@/stores/wgdashboardStore.js";
import Settings from "@/views/settings.vue";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import Setup from "@/views/setup.vue";
import NewConfiguration from "@/views/newConfiguration.vue";

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
        },
        {
          name: "New Configuration",
          path: '/new_configuration',
          component: NewConfiguration
        }
      ]
    },
    {
      path: '/signin', component: Signin
    },
    {
      path: '/welcome', component: Setup,
      meta: {
        requiresAuth: true
      },
    }
  ]
});

router.beforeEach(async (to, from, next) => {
  const wireguardConfigurationsStore = WireguardConfigurationsStore();
  const dashboardConfigurationStore = DashboardConfigurationStore();
  
  
  if (to.meta.requiresAuth){
    if (cookie.getCookie("authToken") && await checkAuth()){
      await dashboardConfigurationStore.getConfiguration()
      if (!wireguardConfigurationsStore.Configurations && to.name !== "Configuration List"){
        await wireguardConfigurationsStore.getConfigurations();
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
