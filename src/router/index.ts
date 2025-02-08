import { createRouter, createWebHistory } from "vue-router";
import UserHome from "@/views/UserViews/UserHome.vue";
import NotFound from "@/views/NotFound.vue";
import LoginView from "@/views/LoginView.vue";
import { useSessionStore } from "@/stores/session";
import UserView from "@/views/UserView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "UserView",
      component: UserView,
      redirect: "/home",
      children: [
        {
          path: "home",
          component: UserHome,
          name: "Home"
        },
        {
          path: "discover",
          component: () => import("@/views/UserViews/ExploreRecipes.vue"),
          name: "Explore"
        },
        {
          path: "my-recipes",
          component: () => import("@/views/UserViews/MyRecipes.vue"),
          name: "MyRecipes"
        },
        {
          path: "add-recipe",
          component: () => import("@/views/UserViews/AddRecipe.vue"),
          name: "AddRecipe"
        },
        {
          path: "my-account",
          component: () => import("@/views/UserViews/MyAccount.vue"),
          name: "MyAccount"
        }
      ]
    },
    {
      path: "/test",
      name: "Testing",
      component: () => import("@/views/TestApi.vue"),
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
