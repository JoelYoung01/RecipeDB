import "./assets/index.css";

import { createPinia } from "pinia";
import { createApp } from "vue";

import App from "./App.vue";
import { googleAuth } from "./plugins";
import router from "./router";

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(googleAuth);

app.mount("#app");
