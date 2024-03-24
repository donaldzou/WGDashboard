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
import Configuration from "@/views/configuration.vue";
import PeerSettings from "@/components/configurationComponents/peerSettings.vue";
import PeerList from "@/components/configurationComponents/peerList.vue";

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
        requiresAuth: true,
        
      },
      children: [
        {
          name: "Configuration List",
          path: '',
          component: ConfigurationList,
          meta: {
            title: "WireGuard Configurations"
          }
        },
        {
          name: "Settings",
          path: '/settings',
          component: Settings,
          meta: {
            title: "Settings"
          }
        },
        {
          name: "New Configuration",
          path: '/new_configuration',
          component: NewConfiguration,
          meta: {
            title: "New Configuration"
          }
        },
        {
          name: "Configuration",
          path: '/configuration/:id',
          component: Configuration,
          meta: {
            title: "Configuration"
          },
          children: [
            {
              name: "Peers List",
              path: '',
              component: PeerList
            }
          ]
        },
        
      ]
    },
    {
      path: '/signin', component: Signin,
      meta: {
        title: "Sign In"
      }
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
  
  if (to.meta.title){
    if (to.params.id){
      document.title = to.params.id + " | WGDashboard";
    }else{
      document.title = to.meta.title + " | WGDashboard";
    }
  }else{
    document.title = "WGDashboard"
  }
  
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
