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

function isAuthUrl(url: string): boolean {
  return [authUrl, refreshUrl, validateUrl].includes(url);
}

// Set an interceptor that will refresh the tokens if a request gets a 401 response
instance.interceptors.response.use(
  // Don't do anything if the response was successful
  function (response) {
    return response;
  },

  async function (error) {
    // Reject the promise if it was not a 401 error
    if (error.response.status !== 401) {
      return Promise.reject(error);
    }

    const originalRequest = error.config;
    console.debug("error accessing: " + originalRequest.url);

    // Redirect to the login page if the 401 came from one of the auth URLs
    if (isAuthUrl(originalRequest.url)) {
      console.debug("redirecting to login page");
      router.replace({ name: "Login" });
      return Promise.reject(error);
    }

    // Try to refresh the tokens and replay the original request
    console.debug("trying to refresh tokens");
    return auth
      .refresh()
      .then(() => {
        return new Promise((resolve, reject) => {
          instance(originalRequest)
            .then((response) => {
              resolve(response);
            })
            .catch((error) => {
              reject(error);
            });
        });
      })
      .catch(() => {
        console.debug("refresh token not present or expired");
        router.replace({ name: "Login" });
        return Promise.reject(error);
      });
  },
);

export default instance;
