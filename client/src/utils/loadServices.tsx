import axios from "axios";

/*
Operations to load services from config 
before execution of other API calls
*/

export let services = {};
let servicesInitialized = false;
const servicesPromiseResolvers = [];

export function setServices(servicesConfig) {
  services = servicesConfig;
  servicesInitialized = true;
  servicesPromiseResolvers.forEach((resolve) => resolve());
  servicesPromiseResolvers.length = 0;
}

export function servicesWait() {
  return new Promise((resolve) => {
    if (servicesInitialized) {
      resolve();
    } else {
      servicesPromiseResolvers.push(resolve);
    }
  });
}

export function getConfig() {
  const host = "localhost";

  return axios
    .get(`http://${host}:5001/config/services`)
    .then((response) => response.data)
    .catch((error) => {
      throw error;
    });
}
