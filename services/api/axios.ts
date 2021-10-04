// create instance
import axios from "axios";

const instance = axios.create({
  baseURL: `${process.env.VUE_APP_BACKEND_URL}`,
  headers: {
    "Content-Type": "application/json",
    Authorization: null,
  },
  // By default, axios has no timeout!
  timeout: 10000, // 10 seconds
});

// Add authorization here
// instance.defaults.headers.common['Authorization'] = null;

export default instance;
