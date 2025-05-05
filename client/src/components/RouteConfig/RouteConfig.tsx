"use client";

import React, { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  GeoJSON,
  useMapEvents,
} from "react-leaflet";
import type { LatLngExpression } from "leaflet";

import useToken from "../contexts/TokenContext";
import {
  generateRoute,
  getRoutes,
  saveRoute,
  removeRoute,
  BackendRoute,
  SavedRoute,
} from "@/app/Api";

export default function RouteConfig() {
  const [distance, setDistance] = useState(2);
  const [preference, setPreference] = useState<"prefer" | "avoid" | "default" | "weather">("default");
  const [startPosition, setStartPosition] = useState<[number, number]>([50.06143, 19.93658]);

  const [savedRoutes, setSavedRoutes] = useState<SavedRoute[]>([]);
  const [previewRoute, setPreviewRoute] = useState<SavedRoute | null>(null);

  const { token } = useToken();

  // --- Pobieranie tras po zalogowaniu ---
  useEffect(() => {
    if (!token) {
      setSavedRoutes([]);
      return;
    }

    (async () => {
      const routes = await getRoutes(token);
      setSavedRoutes(routes);
    })();
  }, [token]);

  // --- Generowanie i zapis trasy ---
  const handleGenerateRoute = async () => {
    if (!token) {
      alert("Zaloguj się, aby zapisać trasy.");
      return;
    }

    if (savedRoutes.length >= 5) {
      alert("Limit 5 zapisanych tras. Usuń jedną, aby dodać kolejną.");
      return;
    }

    const backendRoute: BackendRoute = await generateRoute(
      token,
      startPosition[0],
      startPosition[1],
      distance * 1000,
      preference === "prefer",
      preference === "avoid",
      preference === "weather"
    );

    const saved = await saveRoute(token, backendRoute);
    setSavedRoutes((prev) => [...prev, saved]);
    setPreviewRoute(saved);
  };

  // --- Usuwanie trasy ---
  const handleDeleteRoute = async (id: number) => {
    if (!token) return;
    await removeRoute(token, id);
    setSavedRoutes((prev) => prev.filter((r) => r.id !== id));
    if (previewRoute?.id === id) setPreviewRoute(null);
  };

  // --- Kliknięcie na mapie: ustawienie punktu startowego ---
  function LocationMarker() {
    useMapEvents({
      click(e) {
        setStartPosition([e.latlng.lat, e.latlng.lng]);
      },
    });
    return <Marker position={startPosition as LatLngExpression} />;
  }

  return (
    <div className="flex flex-col md:flex-row gap-6 p-4 w-full max-w-[1400px] mx-auto">
      {/* Panel konfiguracji */}
      <div className="bg-white dark:bg-gray-800 text-black dark:text-white rounded-xl shadow-md p-6 w-full md:w-1/3">
        <h2 className="text-xl font-bold mb-4">Customize your walk route</h2>

        <label className="block mb-2">Distance: {distance} km</label>
        <select
          value={distance}
          onChange={(e) => setDistance(parseFloat(e.target.value))}
          className="w-full mb-4 p-2 rounded border dark:bg-gray-700"
        >
          {[...Array(10)].map((_, i) => {
            const val = (i + 1) * 0.5;
            return (
              <option key={val} value={val}>
                {val} km
              </option>
            );
          })}
        </select>

        <fieldset className="mb-4">
          <legend className="mb-2 font-medium">Green area preference:</legend>
          {["prefer", "default", "avoid", "weather"].map((opt) => (
            <label key={opt} className="block mb-1 capitalize">
              <input
                type="radio"
                name="preference"
                value={opt}
                checked={preference === opt}
                onChange={() => setPreference(opt as any)}
              />
              <span className="ml-2">
                {opt === "weather" ? "base on weather" : `${opt} green`}
              </span>
            </label>
          ))}
        </fieldset>

        <button
          onClick={handleGenerateRoute}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 w-full"
        >
          Generate & save
        </button>

        {savedRoutes.length > 0 && (
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-2">Your routes</h3>
            <ul className="space-y-2">
              {savedRoutes.map((route) => (
                <li
                  key={route.id}
                  className="flex items-center justify-between bg-gray-100 dark:bg-gray-700 p-2 rounded"
                >
                  <button
                    onClick={() => setPreviewRoute(route)}
                    className="text-sm font-medium hover:underline"
                  >
                    Route #{route.id} ({route.decl_distance / 1000} km)
                  </button>
                  <button
                    onClick={() => handleDeleteRoute(route.id)}
                    className="text-red-600 text-xs"
                  >
                    delete
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Mapa */}
      <div className="w-full md:w-2/3 h-[500px] rounded-xl overflow-hidden shadow-md">
        <MapContainer
          center={startPosition as LatLngExpression}
          zoom={13}
          className="w-full h-full"
        >
          <TileLayer
            attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <LocationMarker />
          {previewRoute?.geojson && (
            <GeoJSON data={previewRoute.geojson} pathOptions={{ color: "blue" }} />
          )}
        </MapContainer>
      </div>
    </div>
  );
}


