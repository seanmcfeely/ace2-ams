import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import AnalyzeAlert from "@/pages/Alerts/AnalyzeAlert.vue";
import ViewAlert from "@/pages/Alerts/ViewAlert.vue";
import ViewAnalysis from "@/pages/Alerts/ViewAnalysis.vue";
import ManageAlerts from "@/pages/Alerts/ManageAlerts.vue";
import TheLogin from "@/pages/User/TheLogin.vue";
import { useAuthStore } from "@/stores/auth";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/login",
    name: "Login",
    component: TheLogin,
  },
  {
    path: "/manage_alerts",
    name: "Manage Alerts",
    component: ManageAlerts,
  },
  {
    path: "/analyze",
    name: "Analyze",
    component: AnalyzeAlert,
  },
  {
    path: "/alert/:alertID",
    name: "View Alert",
    component: ViewAlert,
  },
  {
    path: "/alert/:alertID/:analysisID",
    name: "View Analysis",
    component: ViewAnalysis,
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
  const authStore = useAuthStore();

  if (!authStore.isAuthenticated) {
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
    if (to.path == "/login" && authStore.isAuthenticated) {
      next("/manage_alerts");
    }
    // Otherwise allow the user's request to go through
    else {
      next();
    }
  }
});

export default router;
