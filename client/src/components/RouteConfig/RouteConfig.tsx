'use client';
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, GeoJSON, Popup } from 'react-leaflet';
import { LatLngExpression } from 'leaflet';
import useToken from '../contexts/TokenContext';
import { generateRoute } from '@/app/Api';
import { toast } from 'react-toastify';
import { Trees, Minus, X, CloudSun, Route, Loader2, MapPin, IceCream } from "lucide-react"
import L from "leaflet"


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

  const [showGoodLoodSpots, setShowGoodLoodSpots] = useState(false)

  // Mock GoodLood ice cream shop locations (you can replace with real data)
  const goodLoodLocations = [
    { id: 1, name: "GoodLood Centrum", lat: 50.0614, lng: 19.9365, address: "Rynek Główny 1" },
    { id: 2, name: "GoodLood Kazimierz", lat: 50.052, lng: 19.945, address: "ul. Szeroka 15" },
    { id: 3, name: "GoodLood Podgórze", lat: 50.047, lng: 19.952, address: "ul. Kalwaryjska 26" },
    { id: 4, name: "GoodLood Nowa Huta", lat: 50.077, lng: 19.969, address: "os. Centrum E 1" },
    { id: 5, name: "GoodLood Bronowice", lat: 50.085, lng: 19.918, address: "ul. Bronowicka 23" },
  ]

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

  function LocationMarker() {
    useMapEvents({
      click(e) {
        setStartPosition([e.latlng.lat, e.latlng.lng]);
      },
    });
    return <Marker position={startPosition as LatLngExpression} />;
  }

  function GoodLoodMarkers() {
    if (!showGoodLoodSpots) return null

    return (
      <>
        {goodLoodLocations.map((location) => (
          <Marker
            key={location.id}
            position={[location.lat, location.lng]}
            icon={L.divIcon({
              html: `
                <div style="
                  background: linear-gradient(135deg, #ec4899, #f472b6);
                  border: 3px solid white;
                  border-radius: 50%;
                  width: 40px;
                  height: 40px;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  box-shadow: 0 4px 12px rgba(236, 72, 153, 0.4);
                  color: white;
                  font-size: 18px;
                ">
                  🍦
                </div>
              `,
              className: "goodlood-marker",
              iconSize: [40, 40],
              iconAnchor: [20, 20],
            })}
          >
            <Popup>
              <div className="text-center p-2">
                <h3 className="font-bold text-pink-600 mb-1">{location.name}</h3>
                <p className="text-sm text-gray-600">{location.address}</p>
                <a
                  href="https://www.goodlood.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block mt-2 px-3 py-1 bg-pink-500 text-white text-xs rounded-full hover:bg-pink-600 transition-colors"
                >
                  Visit GoodLood
                </a>
              </div>
            </Popup>
          </Marker>
        ))}
      </>
    )
  }

  return (
    
    <div className="flex flex-col md:flex-row gap-6 p-6 w-full max-w-[1400px] mx-auto">
     
      <div className="relative w-full lg:w-1/3">
            <div
              className={`bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 
                            border border-gray-200 dark:border-gray-700 rounded-2xl shadow-xl 
                            backdrop-blur-sm transition-all duration-300 overflow-hidden
                            ${isLoading ? "opacity-60 pointer-events-none" : "opacity-100"}`}
            >
              <div className="bg-gradient-to-r from-sky-500 to-sky-600 p-6 text-white">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-white/20 rounded-lg">
                    <Route className="w-5 h-5" />
                  </div>
                  <h2 className="text-xl font-bold">Route Planner</h2>
                </div>
                <p className="text-sky-100 text-sm">Customize your perfect walk</p>
              </div>
          
          <div className="p-6 space-y-6">
              {/* Distance Section */}
              <div className="space-y-3">
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-gray-800 dark:text-gray-200" />
                <label className="font-semibold text-gray-800 dark:text-gray-200">Distance</label>
              </div>

              <div className="relative">
                <select
                  value={distance}
                  onChange={(e) => setDistance(Number.parseFloat(e.target.value))}
                  className="w-full p-3 pr-10 rounded-xl border-2 border-gray-200 dark:border-gray-600 
                           bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200
                           focus:border-sky-500 dark:focus:border-sky-400 focus:ring-2 focus:ring-sky-200 
                           dark:focus:ring-sky-800 transition-all duration-200 appearance-none cursor-pointer
                           hover:border-gray-300 dark:hover:border-gray-500"
                >
                  {[...Array(10)].map((_, i) => {
                    const val = (i + 1) * 0.5
                    return (
                      <option key={val} value={val}>
                        {val} km
                      </option>
                    )
                  })}
                </select>
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
              <div className="text-center">
                <span
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium 
                               bg-sky-100 dark:bg-sky-900/30 text-sky-800 dark:text-sky-300"
                >
                  {distance} km selected
                </span>
              </div>
            </div>
              {/* Preference (Icon Buttons) */}
              <div className="space-y-4">
              <div className="flex items-center gap-2">
                        <Trees className="w-4 h-4 text-gray-800 dark:text-gray-200" />
                        <label className="font-semibold text-gray-800 dark:text-gray-200">Green Area Preference</label>
                      </div>       
                      <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setPreference("prefer")}
                    className={`flex flex-col items-center p-3 rounded-lg border-2 transition-all ${
                      preference === "prefer"
                        ? "border-sky-500 bg-sky-50 dark:bg-sky-900/20 text-sky-700 dark:text-sky-300"
                        : "border-gray-200 dark:border-gray-600 hover:border-sky-300 dark:hover:border-sky-500"
                    }`}
                  >
                    <Trees className={`w-5 h-5 mb-1 ${preference === "prefer" ? "fill-current" : ""}`} />
                    <span className="text-xs font-medium">Prefer</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setPreference("default")}
                    className={`flex flex-col items-center p-3 rounded-lg border-2 transition-all ${
                      preference === "default"
                        ? "border-sky-500 bg-sky-50 dark:bg-sky-900/20 text-sky-700 dark:text-sky-300"
                        : "border-gray-200 dark:border-gray-600 hover:border-sky-300 dark:hover:border-sky-500"
                    }`}
                  >
                    <Minus className="w-5 h-5 mb-1" />
                    <span className="text-xs font-medium">Default</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setPreference("avoid")}
                    className={`flex flex-col items-center p-3 rounded-lg border-2 transition-all ${
                      preference === "avoid"
                        ? "border-sky-500 bg-sky-50 dark:bg-sky-900/20 text-sky-700 dark:text-sky-300"
                        : "border-gray-200 dark:border-gray-600 hover:border-sky-300 dark:hover:border-sky-500"
                    }`}
                  >
                    <X className="w-5 h-5 mb-1" />
                    <span className="text-xs font-medium">Avoid</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setPreference("base on weather")}
                    className={`flex flex-col items-center p-3 rounded-lg border-2 transition-all ${
                      preference === "base on weather"
                        ? "border-sky-500 bg-sky-50 dark:bg-sky-900/20 text-sky-700 dark:text-sky-300"
                        : "border-gray-200 dark:border-gray-600 hover:border-sky-300 dark:hover:border-sky-500"
                    }`}
                  >
                    <CloudSun className="w-5 h-5 mb-1" />
                    <span className="text-xs font-medium">Weather</span>
                  </button>
                </div>
              </div>
          
           <button
              onClick={handleGenerateRoute}
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-sky-500 to-sky-600 hover:from-sky-600 hover:to-sky-700 
                       text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 
                       hover:shadow-lg hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed 
                       disabled:hover:scale-100 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating Route...
                </>
              ) : (
                <>
                  <Route className="w-5 h-5" />
                  Generate Route
                </>
              )}
            </button>

             {/* GoodLood Sponsor Section */}
             <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
              <div className="text-center space-y-3">
                <div className="flex items-center justify-center gap-2 mb-3">
                  <IceCream className="w-4 h-4 text-pink-500" />
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Sponsored by</span>
                </div>

                <button
                  onClick={() => setShowGoodLoodSpots(!showGoodLoodSpots)}
                  className={`w-full flex items-center justify-center gap-3 p-4 rounded-xl border-2 transition-all duration-200 
                            hover:scale-105 hover:shadow-lg ${
                              showGoodLoodSpots
                                ? "border-pink-500 bg-pink-50 dark:bg-pink-900/30 text-pink-700 dark:text-pink-300 shadow-lg"
                                : "border-pink-200 dark:border-pink-700 hover:border-pink-400 dark:hover:border-pink-500 bg-white dark:bg-gray-800"
                            }`}
                >
                  <div
                    className={`p-2 rounded-lg transition-colors ${
                      showGoodLoodSpots ? "bg-pink-100 dark:bg-pink-800" : "bg-pink-50 dark:bg-pink-900/50"
                    }`}
                  >
                    <IceCream className="w-6 h-6" />
                  </div>
                  <div className="text-left">
                    <div className="font-bold text-lg">GoodLood</div>
                    <div className="text-sm opacity-75">
                      {showGoodLoodSpots ? "Hide ice cream spots" : "Show ice cream spots"}
                    </div>
                  </div>
                </button>

                {showGoodLoodSpots && (
                  <div className="bg-pink-50 dark:bg-pink-900/20 rounded-lg p-3 text-sm">
                    <p className="text-pink-700 dark:text-pink-300 font-medium mb-1">
                      🍦 {goodLoodLocations.length} GoodLood locations found!
                    </p>
                    <p className="text-pink-600 dark:text-pink-400 text-xs">
                      Treat yourself to delicious ice cream during your walk
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

         {/* Enhanced Loading Overlay */}
         {isLoading && (
          <div
            className="absolute inset-0 z-20 flex items-center justify-center bg-white/90 dark:bg-gray-900/90 
                        rounded-2xl backdrop-blur-sm"
          >
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-sky-500 border-t-transparent mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400 font-medium">Creating your perfect route...</p>
            </div>
          </div>
        )}


      </div>

      {/* Map */}
      <div className="w-full lg:w-2/3 h-[600px] rounded-2xl overflow-hidden shadow-xl border border-gray-200 dark:border-gray-700">       
       <MapContainer center={startPosition as LatLngExpression} zoom={13} className="w-full h-full">
          <TileLayer
            attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {currentRoute?.route && <GeoJSON data={currentRoute.route} />}
          <LocationMarker />
          <GoodLoodMarkers />
        </MapContainer>
      </div>
    </div>
  );
}
