// Vuetify
import "@/assets/styles/custom-vuetify.scss";
import "@mdi/font/css/materialdesignicons.css";
import { createVuetify, type ThemeDefinition } from "vuetify";

// To customize SASS variables, follow the guide here: https://vuetifyjs.com/en/features/sass-variables

const MainTheme: ThemeDefinition = {
  dark: false,
  colors: {
    // Add color overrides here
  },
  variables: {
    // Add CSS Variables here
    // https://github.com/vuetifyjs/vuetify/discussions/18883#discussioncomment-7868798
  }
};

export const vuetify = createVuetify({
  theme: {
    defaultTheme: "MainTheme",
    themes: {
      MainTheme
    }
  }
});
