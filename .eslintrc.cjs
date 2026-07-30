/* eslint-env node */
require("@rushstack/eslint-patch/modern-module-resolution");

module.exports = {
  root: true,
  ignorePatterns: ["mobile/", "dist/", "coverage/", "auto-imports.d.ts", "components.d.ts"],
  extends: [
    "plugin:vue/vue3-recommended",
    "eslint:recommended",
    "@vue/eslint-config-typescript",
    "@vue/eslint-config-prettier/skip-formatting"
  ],
  parserOptions: {
    ecmaVersion: "latest"
  },
  rules: {
    "prettier/prettier": "warn",
    "vue/multi-word-component-names": "off",
    // Optional props in Vue 3 + TS (esp. shadcn-vue) do not need defaults.
    "vue/require-default-prop": "off"
  }
};
