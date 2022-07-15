import { describe, it, beforeEach, expect, vi } from "vitest";
import { useUserStore } from "@/stores/user";
import { createCustomPinia } from "@tests/unitHelpers";
import { User } from "@/services/api/user";

import { userReadFactory } from "@mocks/user";

createCustomPinia();
const store = useUserStore();
const spy = vi.spyOn(User, "readAll");
const mock = userReadFactory();

describe("user store", () => {
  beforeEach(() => {
    store.$reset();
  });

  it("will return state.items on the allItems getter", () => {
    expect(store.allItems).toEqual([]);
    store.items = [mock];
    expect(store.allItems).toEqual([mock]);
  });

  it("will call User.readAll on readAll action and set items with the result", async () => {
    spy.mockImplementationOnce(async () => [mock]);
    await store.readAll();
    expect(spy).toHaveBeenCalledTimes(1);
    expect(store.items).toEqual([mock]);
  });
});
