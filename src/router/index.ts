import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import AnalyzeAlert from "../pages/Alerts/AnalyzeAlert.vue";
import ManageAlerts from "../pages/Alerts/ManageAlerts.vue";
import TheLogin from "../pages/User/TheLogin.vue";

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
    path: "/",
    redirect: "/login",
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
