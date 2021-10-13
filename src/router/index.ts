import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import ManageAlerts from "../pages/Alerts/ManageAlerts.vue";
import TheLogin from "../pages/User/TheLogin.vue";
import store from "@/store";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/manage_alerts",
    name: "Manage Alerts",
    component: ManageAlerts,
  },
  {
    path: "/login",
    name: "Login",
    component: TheLogin,
  },
  {
    path: "/",
    redirect: "/login",
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

router.beforeEach(function (to, _, next) {
  const isLoggedIn: boolean = store.getters["auth/isLoggedIn"];

  if (!isLoggedIn) {
    // Redirect the user to the login page if they are not logged in and try to access something
    if (to.path !== "/login") {
      next("/login");
    }
    // Otherwise allow the user's request to the login page go through
    else {
      next();
    }
  } else {
    // Redirect the user to the manage alerts page if they are logged in and try to access the login page
    if (to.path == "/login" && isLoggedIn) {
      next("/manage_alerts");
    }
    // Otherwise allow the user's request to go through
    else {
      next();
    }
  }
});

export default router;
