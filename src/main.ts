import "./assets/styles/main.css";

import { createApp } from "vue";
import { createPinia } from "pinia";
import { vuetify, googleAuth } from "./plugins";

import App from "./App.vue";
import router from "./router";

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(vuetify);
app.use(googleAuth);

app.mount("#app");
