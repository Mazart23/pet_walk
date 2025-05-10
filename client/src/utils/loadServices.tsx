import axios from "axios";

/*
Operations to load services from config 
before execution of other API calls
*/

export let services = {};
let servicesInitialized = false;
let servicesPromiseResolve = null;

export function setServices(servicesConfig) {
  services = servicesConfig;
  servicesInitialized = true;
  if (servicesPromiseResolve) {
    servicesPromiseResolve();
  }
}

export function servicesWait() {
  return new Promise((resolve) => {
    if (servicesInitialized) {
      resolve();
    } else {
      servicesPromiseResolve = resolve;
    }
  });
}

export function getConfig() {
  const host =
    typeof window !== "undefined" ? "localhost" : "controller";

  return axios
    .get(`http://${host}:5001/config/services`)
    .then((response) => response.data)
    .catch((error) => {
      throw error;
    });
}
