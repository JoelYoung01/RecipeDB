/* Global Jest setup for the Junket mobile app. */

// Silence the Animated "useNativeDriver is not supported" warning in tests.
jest.mock("react-native/src/private/animated/NativeAnimatedHelper");

// Official mock: components relying on useSafeAreaInsets render with zero
// insets instead of requiring a SafeAreaProvider in every test.
jest.mock("react-native-safe-area-context", () => {
  // Jest mock factories cannot use ESM import; require is required here.
  // eslint-disable-next-line @typescript-eslint/no-require-imports -- jest mock factory
  return require("react-native-safe-area-context/jest/mock").default;
});
