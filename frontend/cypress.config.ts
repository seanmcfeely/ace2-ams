/* eslint-disable @typescript-eslint/no-var-requires */
import { defineConfig } from "cypress";

export default defineConfig({
  fixturesFolder: "cypress/fixtures",
  screenshotsFolder: "cypress/screenshots",
  videosFolder: "cypress/videos",
  viewportWidth: 1280,
  viewportHeight: 720,
  e2e: {
    specPattern: "tests/e2e/specs/**/*.spec.js",
    supportFile: "tests/e2e/support/index-e2e.js",
    baseUrl: "http://ace2-ams:8080",
    execTimeout: 90000,
    pageLoadTimeout: 90000,
    requestTimeout: 10000,
    responseTimeout: 90000,
    taskTimeout: 90000,
  },
  component: {
    specPattern: "tests/component/src/**/*.spec.ts",
    supportFile: "tests/e2e/support/index-ct.js",
    devServer: {
      framework: "vue",
      bundler: "vite",
    },
    setupNodeEvents(on, config) {
      require("@cypress/code-coverage/task")(on, config);
      return config;
    },
  },
});
