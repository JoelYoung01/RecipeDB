import { createRouter, createWebHistory } from "vue-router";
import HomeView from "@/views/HomeView.vue";
import NotFound from "@/views/NotFound.vue";
import LoginView from "@/views/LoginView.vue";
import { useSessionStore } from "@/stores/session";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "Home",
      component: HomeView,
      meta: {
        noAuthReq: true
      }
    },
    {
      path: "/login",
      name: "Login",
      component: LoginView,
      meta: {
        noAuthReq: true
      }
    },
    {
      path: "/app-definition",
      children: [
        {
          path: "list",
          name: "AppDefinitionList",
          component: () => import("@/views/AppDefinitions/ListView.vue")
        },
        {
          path: "create",
          name: "AppDefinitionCreate",
          meta: {
            useShadedBackground: true
          },
          component: () => import("@/views/AppDefinitions/UpdateView.vue")
        },
        {
          path: ":app_definition_id(\\d+)",
          children: [
            {
              name: "AppDefinitionDetail",
              path: "detail",
              meta: {
                useShadedBackground: true
              },
              component: () => import("@/views/AppDefinitions/DetailView.vue")
            },
            {
              path: "update",
              name: "AppDefinitionUpdate",
              meta: {
                useShadedBackground: true
              },
              component: () => import("@/views/AppDefinitions/UpdateView.vue")
            }
          ]
        }
      ]
    },
    {
      path: "/:pathMatch(.*)*",
      name: "notFound",
      component: NotFound
    }
  ]
});

// Verify user is logged in before routing
router.beforeEach((to) => {
  const sessionStore = useSessionStore();

  if (!sessionStore.currentUser && !to.meta.noAuthReq) {
    return `/login?redirectUrl=${to.fullPath}`;
  }
});

export default router;
