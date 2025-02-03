// Vuetify
import "vuetify/styles";
import "@mdi/font/css/materialdesignicons.css";
import { createVuetify, type ThemeDefinition } from "vuetify";

// To customize SASS variables, follow the guide here: https://vuetifyjs.com/en/features/sass-variables

const MainTheme: ThemeDefinition = {
  dark: false,
  colors: {
    // Add color overrides here
  },
  variables: {
    // Add variable overrides here
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
