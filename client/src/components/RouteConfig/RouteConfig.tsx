'use client';
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import { LatLngExpression } from 'leaflet';
import useToken from '../contexts/TokenContext';
import { generateRoute } from '@/app/Api';

export default function RouteConfig() {
  const [isErrorDisplayed, setIsErrorDisplayed] = useState(false);
  const [distance, setDistance] = useState(2);
  const [isAvoidGreen, setIsAvoidGreen] = useState(false);
  const [isPreferGreen, setIsPreferGreen] = useState(false);
  const [isIncludeWeather, setIsIncludeWeather] = useState(false);
  const [startPosition, setStartPosition] = useState<[number, number]>([50.06143, 19.93658]); // Kraków

  const [routeName, setRouteName] = useState('');
  const [favoriteRoutes, setFavoriteRoutes] = useState<
    { name: string; distance: number; isAvoidGreen: boolean; isPreferGreen: boolean; position: [number, number] }[]
  >([]);

  const token = useToken();

  useEffect(() => {
    if (isErrorDisplayed) {
      setTimeout(() => {
        setIsErrorDisplayed(value => !value)
      }, 5000);
    }
  }, [isErrorDisplayed, setIsErrorDisplayed])

  const handleGenerateRoute = () => {
    console.log({ distance, isAvoidGreen, isPreferGreen, startPosition });
    generateRoute(
      token,
      startPosition[0],
      startPosition[1],
      distance * 1000,
      isPreferGreen,
      isAvoidGreen,
      isIncludeWeather).then((response) => {
        if (response === false) {
          setIsErrorDisplayed(true);
        }
      });
  };

  const handleSave = () => {
    if (routeName.trim() === '') return;

    const newRoute = {
      name: routeName,
      distance,
      isAvoidGreen,
      isPreferGreen,
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
      {/* Configuration panel */}
      <div className="bg-white dark:bg-gray-800 text-black dark:text-white rounded-xl shadow-md p-6 w-full md:w-1/3">
        <h2 className="text-xl font-bold mb-4">Dostosuj trasę spaceru</h2>

        <label className="block mb-2">Długość trasy: {distance} km</label>
        <input
          type="range"
          min="0.5"
          max="5"
          step="0.5"
          value={distance}
          onChange={(e) => setDistance(parseFloat(e.target.value))}
          className="w-full mb-4"
        />

        <label className="block mb-2">
          <input type="checkbox" checked={isPreferGreen} onChange={() => setIsPreferGreen(!isPreferGreen)} />
          <span className="ml-2">Preferuję parki</span>
        </label>

        <label className="block mb-4">
          <input type="checkbox" checked={isAvoidGreen} onChange={() => setIsAvoidGreen(!isAvoidGreen)} />
          <span className="ml-2">Preferuję chodniki</span>
        </label>

        <button
          onClick={handleGenerateRoute}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Pokaż trasę
        </button>

        <div>
          {!!isErrorDisplayed &&
            <p>
              Service with routes is temporary unavailable. Please try again later.
            </p>
          }
        </div>

        {/* Save route */}
        <div className="mt-6">
          <input
            type="text"
            value={routeName}
            onChange={(e) => setRouteName(e.target.value)}
            placeholder="Nazwa trasy"
            className="w-full px-3 py-2 rounded border dark:bg-gray-700 mb-2"
          />
          <button
            onClick={handleSave}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          >
            Zapisz trasę
          </button>

          {/* Favourite routes list */}
          {favoriteRoutes.length > 0 && (
            <div className="mt-4">
              <h3 className="text-lg font-semibold mb-2">Ulubione trasy</h3>
              <ul className="list-disc list-inside space-y-1">
                {favoriteRoutes.map((route, index) => (
                  <li key={index}>
                    <span className="font-medium">{route.name}</span> – {route.distance} km
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Map */}
      <div className="w-full md:w-2/3 h-[500px] rounded-xl overflow-hidden shadow-md">
        <MapContainer center={startPosition as LatLngExpression} zoom={13} className="w-full h-full">
          <TileLayer
            attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <LocationMarker />
        </MapContainer>
      </div>
    </div>
  );
}
