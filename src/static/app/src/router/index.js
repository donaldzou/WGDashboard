import { createRouter, createWebHashHistory } from 'vue-router'
import {cookie} from "../utilities/cookie.js";
import Index from "@/views/index.vue"
import Signin from "@/views/signin.vue";
import ConfigurationList from "@/views/configurationList.vue";
import {fetchGet} from "@/utilities/fetch.js";

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
      path: '/',
      component: Index,
      meta: {
        requiresAuth: true
      },
      children: [
        {
          path: '',
          component: ConfigurationList
        }
      ]
    },
    {
      path: '/signin', component: Signin
    }
  ]
});

router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth){
    if (cookie.getCookie("authToken") && await checkAuth()){
      next()
    }else{
      next("/signin")
    }
  }else {
    next();
  }
});
export default router
