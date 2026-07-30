const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");

const config = getDefaultConfig(__dirname);

// inlineRem 16 keeps rem-based Tailwind spacing identical to the web app.
module.exports = withNativeWind(config, { input: "./src/global.css", inlineRem: 16 });
