// create instance
import axios from "axios";

import auth, { authUrl, refreshUrl, validateUrl } from "@/services/api/auth";
import router from "@/router";

const instance = axios.create({
  baseURL: `${process.env.VUE_APP_BACKEND_URL}`,
  headers: {
    "Content-Type": "application/json",
  },
  // By default, axios has no timeout!
  timeout: 10000, // 10 seconds
});

// Set an interceptor that will refresh the tokens if a request gets a 401 response
instance.interceptors.response.use(
  // Don't do anything if the response was successful
  function (response) {
    return response;
  },

  // Check to see if the response was a 401 and try to refresh the tokens
  async function (error) {
    const originalRequest = error.config;
    console.debug("error accessing: " + originalRequest.url);

    // Redirect to the login page if the 401 came from one of the auth URLs
    if ([authUrl, refreshUrl, validateUrl].includes(originalRequest.url)) {
      console.debug("redirecting to login page");
      sessionStorage.removeItem("authenticated");
      router.replace({ name: "Login" });
      return Promise.reject(error);
    }

    // If the error was a 401, try to refresh the auth tokens
    if (error.response.status === 401) {
      console.debug("trying to refresh tokens");
      await auth.refresh().catch(() => {
        console.debug("refresh token not present or expired");
        router.replace({ name: "Login" });
        return Promise.reject(error);
      });
      console.debug("successfully refreshed tokens");
      return await instance(originalRequest);
    }

    return Promise.reject(error);
  },
);

export default instance;
