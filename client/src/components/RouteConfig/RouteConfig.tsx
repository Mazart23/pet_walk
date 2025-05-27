'use client';
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, GeoJSON } from 'react-leaflet';
import { LatLngExpression } from 'leaflet';
import useToken from '../contexts/TokenContext';
import { generateRoute } from '@/app/Api';
import { toast } from 'react-toastify';
import Breadcrumb from '../Common/Breadcrumb';

export default function RouteConfig() {
  const [isErrorDisplayed, setIsErrorDisplayed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [distance, setDistance] = useState(2);
  const [preference, setPreference] = useState("default");
  const [startPosition, setStartPosition] = useState<[number, number]>([50.06143, 19.93658]);

  const [routeName, setRouteName] = useState('');
  const [favoriteRoutes, setFavoriteRoutes] = useState<
    { name: string; distance: number; preference: string; position: [number, number] }[]
  >([]);
  const [currentRoute, setCurrentRoute] = useState({});

  const { token } = useToken();

  useEffect(() => {
    if (isErrorDisplayed) {
      setTimeout(() => {
        setIsErrorDisplayed(value => !value)
      }, 5000);
    }
  }, [isErrorDisplayed, setIsErrorDisplayed])

  const handleGenerateRoute = () => {
    setCurrentRoute({});
    setIsLoading(true);
    generateRoute(
      token,
      startPosition[0],
      startPosition[1],
      distance * 1000,
      preference === "prefer",
      preference === "avoid",
      preference === "base on weather").then((response) => {
        if (response === false) {
          toast.error("Service with routes is temporarily unavailable. Please try again later.");
        } else {
          setCurrentRoute(response);
          toast.success("Route generated successfully!");

        }
        setIsLoading(false);
      });
  };

  const handleSave = () => {
    if (routeName.trim() === '') return;
    const newRoute = {
      name: routeName,
      distance,
      preference,
      position: startPosition,
    };
    setFavoriteRoutes((prev) => [...prev, newRoute]);
    setRouteName('');
  };

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
      {/* Configuration Panel */}
      {/* <div className="bg-white dark:bg-gray-800 text-black dark:text-white rounded-xl shadow-md p-6 w-full md:w-1/3"> */}
      <div className="relative w-full md:w-1/3">
        <div className={`bg-white dark:bg-gray-800 text-black dark:text-white rounded-xl shadow-md p-6 h-full transition-opacity duration-300 ${isLoading ? 'opacity-30 pointer-events-none' : 'opacity-100'}`}>        
          <h2 className="text-xl font-bold mb-4">Customize your walk route</h2>

          {/* Distance */}
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

          {/* Preference (Radio Buttons) */}
          <fieldset className="mb-4">
            <legend className="mb-2 font-medium">Green area preference:</legend>
            {["prefer", "default", "avoid", "base on weather"].map((opt) => (
              <label key={opt} className="block mb-1">
                <input
                  type="radio"
                  name="preference"
                  value={opt}
                  checked={preference === opt}
                  onChange={() => setPreference(opt)}
                />
                <span className="ml-2 capitalize">{opt} green</span>
              </label>
            ))}
          </fieldset>

          <button
            onClick={handleGenerateRoute}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Show route
          </button>
      


        </div>
        {isLoading && (
          <div className="absolute inset-0 z-20 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 rounded-xl">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
          </div>
        )}
      </div>

      {/* Map */}
      <div className="w-full md:w-2/3 h-[500px] rounded-xl overflow-hidden shadow-md">
        <MapContainer center={startPosition as LatLngExpression} zoom={13} className="w-full h-full">
          <TileLayer
            attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {currentRoute?.route && <GeoJSON data={currentRoute.route} />}
          <LocationMarker />
        </MapContainer>
      </div>
    </div>
    
  );
}
