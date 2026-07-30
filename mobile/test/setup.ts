/* Global Jest setup for the RecipeDB mobile app. */

// Silence the Animated "useNativeDriver is not supported" warning in tests.
jest.mock("react-native/src/private/animated/NativeAnimatedHelper");

// Official mock: components relying on useSafeAreaInsets render with zero
// insets instead of requiring a SafeAreaProvider in every test.
jest.mock(
  "react-native-safe-area-context",
  () => require("react-native-safe-area-context/jest/mock").default
);
