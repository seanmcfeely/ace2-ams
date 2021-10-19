// create instance
import axios, { AxiosRequestConfig } from "axios";

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

  async function (error) {
    // Reject the promise if it was not a 401 error
    if (error.response.status !== 401) {
      return Promise.reject(error);
    }

    const originalRequest = error.config;
    console.debug("error accessing: " + originalRequest.url);

    // Redirect to the login page if the 401 came from one of the auth URLs
    if (originalRequest.url.includes("/auth")) {
      return Promise.reject(error);
    }

    // Try to refresh the tokens and replay the original request
    console.debug("trying to refresh tokens");
    return axiosRefresh()
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
        return Promise.reject(error);
      });
  },
);

export async function axiosRefresh(): Promise<void> {
  const config: AxiosRequestConfig = {
    url: "/auth/refresh",
    method: "GET",
    withCredentials: true,
  };

  await instance.request(config).catch((error) => {
    console.debug("need to authenticate");
    sessionStorage.removeItem("authenticated");
    throw error;
  });

  console.debug("successfully refreshed tokens");
  sessionStorage.setItem("authenticated", "yes");
}

export default instance;
