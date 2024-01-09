import { createRouter, createWebHashHistory } from 'vue-router'
import {cookie} from "../utilities/cookie.js";
import Index from "@/views/index.vue"
import Signin from "@/views/signin.vue";
import ConfigurationList from "@/views/configurationList.vue";

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

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth){
    if (cookie.getCookie("authToken")){
      next()
    }else{
      next("/signin")
    }
  }else {
    next();
  }
});
export default router
