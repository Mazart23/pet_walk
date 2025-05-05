import axios from "axios";

/* ------------------------------------------------------------------ */
/* 1. Struktury typów                                                 */
/* ------------------------------------------------------------------ */
export interface ServiceRecord {
  url: string;
}

interface RawService {
  name: string;          // np. "controller"
  ip_host: string;       // np. "127.0.0.1"
  port: number;          // np. 8000
  http: "http" | "https";
}

/* ------------------------------------------------------------------ */
/* 2. Globalny obiekt services + synchronizacja                       */
/* ------------------------------------------------------------------ */
export let services: Record<string, ServiceRecord> = {};

let servicesInitialized = false;
let servicesPromiseResolve: (() => void) | null = null;

/** Ustawia (lub nadpisuje) mapę usług i sygnalizuje gotowość */
export function setServices(cfg: Record<string, ServiceRecord>) {
  services = cfg;
  servicesInitialized = true;
  if (servicesPromiseResolve) servicesPromiseResolve();
}

/** Zwraca Promise, który rozwiązuje się, gdy services są gotowe */
export function servicesWait(): Promise<void> {
  return new Promise((resolve) => {
    if (servicesInitialized) resolve();
    else servicesPromiseResolve = resolve;
  });
}

/* ------------------------------------------------------------------ */
/* 3. Funkcja pobierająca config z serwera                             */
/* ------------------------------------------------------------------ */
export async function loadServices() {
  const { data } = await axios.get<{ services: RawService[] }>(
    "http://controller:5001/config/services"
  );

  const responseConfig: Record<string, ServiceRecord> = {};

  /*  Mapujemy każdą usługę na obiekt { url }.
      Backend wysyła np.:
      { name: "controller", ip_host: "172.23.0.3", port: 8000, http: "http" }
  */
  data.services.forEach((service) => {
    responseConfig[service.name] = {
      url: `${service.http}://${service.ip_host}:${service.port}`,
    };
  });

  // <- najważniejsze: "controller" MUSI być kluczem, bo Api.tsx go używa
  if (!responseConfig.controller) {
    console.error("⚠️  Brak usługi 'controller' w odpowiedzi config-serwera!");
  }

  setServices(responseConfig);
}

/* ------------------------------------------------------------------ */
/* 4. Automatyczne ładowanie przy starcie aplikacji frontendowej      */
/* ------------------------------------------------------------------ */
loadServices().catch((err) => {
  console.error("❌ Nie udało się pobrać konfiguracji usług:", err);
});

export const getConfig = loadServices;   // alias dla starej nazwy
