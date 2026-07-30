import { secureStorage } from "@/lib/secure-storage";
import { resetAppLockBootstrapForTests, useAppLockStore } from "../app-lock";

jest.mock("@/lib/secure-storage", () => ({
  secureStorage: {
    get: jest.fn(),
    set: jest.fn(),
    remove: jest.fn()
  }
}));

const mockedStorage = secureStorage as jest.Mocked<typeof secureStorage>;

beforeEach(() => {
  jest.clearAllMocks();
  resetAppLockBootstrapForTests();
  useAppLockStore.setState({ ready: false, enabled: false, locked: false });
});

describe("app lock store", () => {
  it("bootstraps locked when the preference is persisted", async () => {
    mockedStorage.get.mockResolvedValue("1");
    await useAppLockStore.getState().bootstrap();
    expect(useAppLockStore.getState()).toMatchObject({
      ready: true,
      enabled: true,
      locked: true
    });
  });

  it("bootstraps unlocked when the preference is absent", async () => {
    mockedStorage.get.mockResolvedValue(null);
    await useAppLockStore.getState().bootstrap();
    expect(useAppLockStore.getState()).toMatchObject({
      ready: true,
      enabled: false,
      locked: false
    });
  });

  it("only bootstraps once", async () => {
    mockedStorage.get.mockResolvedValue(null);
    await useAppLockStore.getState().bootstrap();
    await useAppLockStore.getState().bootstrap();
    expect(mockedStorage.get).toHaveBeenCalledTimes(1);
  });

  it("persists the preference when enabling, without locking the current session", async () => {
    await useAppLockStore.getState().setEnabled(true);
    expect(mockedStorage.set).toHaveBeenCalledWith("junket.app_lock", "1");
    expect(useAppLockStore.getState()).toMatchObject({ enabled: true, locked: false });
  });

  it("removes the preference when disabling", async () => {
    await useAppLockStore.getState().setEnabled(true);
    await useAppLockStore.getState().setEnabled(false);
    expect(mockedStorage.remove).toHaveBeenCalledWith("junket.app_lock");
    expect(useAppLockStore.getState()).toMatchObject({ enabled: false, locked: false });
  });

  it("lock() engages only while enabled", async () => {
    useAppLockStore.getState().lock();
    expect(useAppLockStore.getState().locked).toBe(false);

    await useAppLockStore.getState().setEnabled(true);
    useAppLockStore.getState().lock();
    expect(useAppLockStore.getState().locked).toBe(true);

    useAppLockStore.getState().unlock();
    expect(useAppLockStore.getState().locked).toBe(false);
  });
});
