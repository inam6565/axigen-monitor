import axios from "axios";

const api = axios.create({
  baseURL: "/api", // FastAPI backend URL
});

export default api;
