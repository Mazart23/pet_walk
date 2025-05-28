// "use client";
// import { useParams } from "next/navigation";
// import { useEffect, useState } from 'react';
// import { fetchRoutes, deleteRoute } from '@/app/Api';
// import useToken from '@/components/contexts/TokenContext';
// import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
// import { Feature } from 'geojson';
// import Breadcrumb from "@/components/Common/Breadcrumb";


// export default function UserProfilePage() {
//   const params = useParams();
//   const username = params.username;

//   const [routes, setRoutes] = useState([]);
//   const [expandedRouteId, setExpandedRouteId] = useState<number | null>(null);
//   const { token } = useToken();

//   useEffect(() => {
//     if (token) {
//       fetchRoutes(token).then(res => {
//         if (res?.routes) {
//           setRoutes(res.routes);
//         }
//       });
//     }
//   }, [token]);

//   const handleDelete = async (routeId: number) => {
//     if (!token) return;
//     const ok = await deleteRoute(token, routeId);
//     if (ok) {
//       setRoutes(routes.filter(r => r.id !== routeId));
//     }
//   };

//   return (
//     <>
//      <Breadcrumb />

//     <div className="p-6 text-white">      
//       {routes.length > 0 ? (
//          <ul className="space-y-4">
//          {routes.map((route) => (
//            <li
//              key={route.id}
//              className="bg-gray-100 dark:bg-gray-800 text-black dark:text-white p-4 rounded shadow"
//            >
//              <div className="flex justify-between items-center">
//                <div>
//                  <p><strong>Distance:</strong> {(route.real_distance / 1000).toFixed(2)} km</p>
//                  <p>
//                    <strong>Preferences:</strong>{" "}
//                    {route.declared_parameters.is_prefer_green
//                      ? "prefer green"
//                      : route.declared_parameters.is_avoid_green
//                      ? "avoid green"
//                      : "default"}
//                  </p>
//                  <p><strong>Data:</strong> {new Date(route.timestamp).toLocaleString()}</p>
//                </div>
//                <div className="flex flex-col items-end gap-2">
//                  <button
//                    onClick={() =>
//                      setExpandedRouteId((prev) =>
//                        prev === route.id ? null : route.id
//                      )
//                    }
//                    className="text-sm bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded"
//                  >
//                    {expandedRouteId === route.id ? "Ukryj trasę" : "Pokaż trasę"}
//                  </button>
//                  <button
//                    onClick={() => handleDelete(route.id)}
//                    className="text-sm bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded"
//                  >
//                    🗑 Usuń
//                  </button>
//                </div>
//              </div>

//              {expandedRouteId === route.id && (
//                <div className="mt-4">
//                  <MapContainer
//                    center={[
//                      route.declared_parameters.point.latitude,
//                      route.declared_parameters.point.longitude,
//                    ]}
//                    zoom={13}
//                    className="w-full h-[300px] rounded"
//                  >
//                    <TileLayer
//                      attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
//                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
//                    />
//                    <GeoJSON
//                     data={route.route}
//                     />
//                  </MapContainer>
//                </div>
//              )}
//            </li>
//          ))}
//        </ul>
//      ) : (
//        <p>Brak zapisanych tras.</p>
//      )}
//    </div>
//  </>
// );
// }

"use client"

import { useParams } from "next/navigation"
import { useEffect, useState } from "react"
import { fetchRoutes, deleteRoute } from "@/app/Api"
import useToken from "@/components/contexts/TokenContext"
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet"
import Breadcrumb from "@/components/Common/Breadcrumb"
import {
  MapPin,
  Route,
  Calendar,
  Trash2,
  Eye,
  EyeOff,
  Clock,
  ArrowUpDown,
  Search,
  Trees,
  X,
  Minus,
  CloudSun,
  Loader2,
} from "lucide-react"
import { motion } from "framer-motion"

type RoutePreference = "prefer green" | "avoid green" | "default" | "base on weather"

interface RouteData {
  id: number
  real_distance: number
  timestamp: string
  route: any
  declared_parameters: {
    is_prefer_green: boolean
    is_avoid_green: boolean
    is_weather_based: boolean
    point: {
      latitude: number
      longitude: number
    }
    distance: number
  }
}

export default function UserProfilePage() {
  const params = useParams()
  const username = params.username

  const [routes, setRoutes] = useState<RouteData[]>([])
  const [expandedRouteId, setExpandedRouteId] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [sortBy, setSortBy] = useState<"date" | "distance">("date")
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc")
  const [searchTerm, setSearchTerm] = useState("")
  const [filterPreference, setFilterPreference] = useState<RoutePreference | "all">("all")
  const { token } = useToken()

  useEffect(() => {
    if (token) {
      setIsLoading(true)
      fetchRoutes(token)
        .then((res) => {
          if (res?.routes) {
            setRoutes(res.routes)
          }
        })
        .finally(() => {
          setIsLoading(false)
        })
    }
  }, [token])

  const handleDelete = async (routeId: number) => {
    if (!token) return

    if (!window.confirm("Are you sure you want to delete this route?")) {
      return
    }

    const ok = await deleteRoute(token, routeId)
    if (ok) {
      setRoutes(routes.filter((r) => r.id !== routeId))
    }
  }

  const getRoutePreference = (route: RouteData): RoutePreference => {
    if (route.declared_parameters.is_prefer_green) return "prefer green"
    if (route.declared_parameters.is_avoid_green) return "avoid green"
    if (route.declared_parameters.is_weather_based) return "base on weather"
    return "default"
  }

  const getPreferenceIcon = (preference: RoutePreference) => {
    switch (preference) {
      case "prefer green":
        return <Trees className="w-4 h-4 text-sky-500" />
      case "avoid green":
        return <X className="w-4 h-4 text-sky-500" />
      case "default":
        return <Minus className="w-4 h-4 text-sky-500" />
      case "base on weather":
        return <CloudSun className="w-4 h-4 text-sky-500" />
    }
  }

  const getPreferenceColor = (preference: RoutePreference) => {
    switch (preference) {
      case "prefer green":
        return "bg-sky-100 text-sky-800 dark:bg-sky-900/30 dark:text-sky-300"
      case "avoid green":
        return "bg-sky-100 text-sky-800 dark:bg-sky-900/30 dark:text-sky-300"
      case "default":
        return "bg-sky-100 text-sky-800 dark:bg-sky-900/30 dark:text-sky-300"
      case "base on weather":
        return "bg-sky-100 text-sky-800 dark:bg-sky-900/30 dark:text-sky-300"
    }
  }

  const sortedAndFilteredRoutes = routes
    .filter((route) => {
      // Apply preference filter
      if (filterPreference !== "all") {
        const routePreference = getRoutePreference(route)
        if (routePreference !== filterPreference) return false
      }

      // Apply search filter (could be expanded to search more fields)
      if (searchTerm) {
        const date = new Date(route.timestamp).toLocaleDateString()
        const distance = (route.real_distance / 1000).toFixed(2)
        return date.includes(searchTerm) || distance.includes(searchTerm)
      }

      return true
    })
    .sort((a, b) => {
      if (sortBy === "date") {
        const dateA = new Date(a.timestamp).getTime()
        const dateB = new Date(b.timestamp).getTime()
        return sortOrder === "asc" ? dateA - dateB : dateB - dateA
      } else {
        return sortOrder === "asc" ? a.real_distance - b.real_distance : b.real_distance - a.real_distance
      }
    })

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-12">
      
      <div className="container mx-auto px-4 py-6">
      <div className="flex items-center gap-2 mt-4">
      <div className="p-2 bg-sky rounded-lg">
              <h1 className="text-3xl opacity-0 font-bold flex items-center gap-2">
                <Route className="w-6 h-6" />
                My Routes
              </h1>
              <p className="opacity-0 mt-1">
                {routes.length} saved {routes.length === 1 ? "route" : "routes"} • Total distance:{" "}
                {(routes.reduce((sum, route) => sum + route.real_distance, 0) / 1000).toFixed(2)} km
              </p>
            </div>
          </div>
        </div>
      

      <div className="container mx-auto px-4 -mt-6">
      <div className="p-2 bg-sky rounded-lg">
              <h1 className="text-3xl font-bold flex items-center gap-2">
                <Route className="w-6 h-6" />
                My Routes
              </h1>
              <p className="font-light mt-1">
                {routes.length} saved {routes.length === 1 ? "route" : "routes"} • Total distance:{" "}
                {(routes.reduce((sum, route) => sum + route.real_distance, 0) / 1000).toFixed(2)} km
              </p>
            </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6">
          {/* Filters and Search */}
          <div className="flex flex-col lg:flex-row gap-4 mb-6">
            <div className="relative flex-grow">
              {/* <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div> */}
              {/* <input
                type="text"
                placeholder="Search routes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 py-2 px-4 text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-sky-500"
              /> */}
            </div>

            <div className="flex flex-wrap gap-2">
              <select
                value={filterPreference}
                onChange={(e) => setFilterPreference(e.target.value as RoutePreference | "all")}
                className="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 py-2 px-4 text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-sky-500"
              >
                <option value="all">All preferences</option>
                <option value="prefer green">Prefer green</option>
                <option value="avoid green">Avoid green</option>
                <option value="default">Default</option>
                <option value="base on weather">Weather based</option>
              </select>

              <button
                onClick={() => {
                  if (sortBy === "date") {
                    setSortOrder(sortOrder === "asc" ? "desc" : "asc")
                  } else {
                    setSortBy("date")
                    setSortOrder("desc")
                  }
                }}
                className={`flex items-center gap-1 rounded-lg border py-2 px-4 ${
                  sortBy === "date"
                    ? "border-sky-500 bg-sky-50 dark:bg-sky-900/20 text-sky-700 dark:text-sky-300"
                    : "border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200"
                }`}
              >
                <Calendar className="w-4 h-4" />
                Date
                {sortBy === "date" && <ArrowUpDown className={`w-3 h-3 ${sortOrder === "asc" ? "rotate-180" : ""}`} />}
              </button>

              <button
                onClick={() => {
                  if (sortBy === "distance") {
                    setSortOrder(sortOrder === "asc" ? "desc" : "asc")
                  } else {
                    setSortBy("distance")
                    setSortOrder("desc")
                  }
                }}
                className={`flex items-center gap-1 rounded-lg border py-2 px-4 ${
                  sortBy === "distance"
                    ? "border-sky-500 bg-sky-50 dark:bg-sky-900/20 text-sky-700 dark:text-sky-300"
                    : "border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200"
                }`}
              >
                <MapPin className="w-4 h-4" />
                Distance
                {sortBy === "distance" && (
                  <ArrowUpDown className={`w-3 h-3 ${sortOrder === "asc" ? "rotate-180" : ""}`} />
                )}
              </button>
            </div>
          </div>

          {/* Routes List */}
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="w-12 h-12 text-sky-500 animate-spin mb-4" />
              <p className="text-gray-500 dark:text-gray-400">Loading your routes...</p>
            </div>
          ) : sortedAndFilteredRoutes.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {sortedAndFilteredRoutes.map((route) => {
                const routePreference = getRoutePreference(route)
                return (
                  <motion.div
                    key={route.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden shadow-md hover:shadow-lg transition-shadow"
                  >
                    <div className="p-5">
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center gap-2">
                          <div className="p-2 rounded-full bg-sky-100 dark:bg-sky-900/30">
                            <Route className="w-5 h-5 text-sky-600 dark:text-sky-400" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-lg text-gray-800 dark:text-gray-200">
                              {(route.real_distance / 1000).toFixed(2)} km Route
                            </h3>
                            <div className="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400">
                              <Clock className="w-3 h-3" />
                              {new Date(route.timestamp).toLocaleDateString(undefined, {
                                year: "numeric",
                                month: "short",
                                day: "numeric",
                              })}
                            </div>
                          </div>
                        </div>
                        <div
                          className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getPreferenceColor(
                            routePreference,
                          )}`}
                        >
                          {getPreferenceIcon(routePreference)}
                          <span className="capitalize">{routePreference}</span>
                        </div>
                      </div>

                      <div className="flex justify-between mt-4">
                        <button
                          onClick={() => setExpandedRouteId((prev) => (prev === route.id ? null : route.id))}
                          className="flex items-center gap-1 text-sm font-medium text-sky-600 hover:text-sky-700 dark:text-sky-400 dark:hover:text-sky-300 transition-colors"
                        >
                          {expandedRouteId === route.id ? (
                            <>
                              <EyeOff className="w-4 h-4" /> Hide Map
                            </>
                          ) : (
                            <>
                              <Eye className="w-4 h-4" /> View Map
                            </>
                          )}
                        </button>
                        <button
                          onClick={() => handleDelete(route.id)}
                          className="flex items-center gap-1 text-sm font-medium text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" /> Delete
                        </button>
                      </div>
                    </div>

                    {expandedRouteId === route.id && (
                      <div className="h-[300px] w-full border-t border-gray-200 dark:border-gray-700">
                        <MapContainer
                          center={[route.declared_parameters.point.latitude, route.declared_parameters.point.longitude]}
                          zoom={13}
                          className="w-full h-full"
                        >
                          <TileLayer
                            attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                          />
                          <GeoJSON
                            data={route.route}
                            style={() => ({
                              color:
                                routePreference === "prefer green"
                                  ? "#22c55e"
                                  : routePreference === "avoid green"
                                    ? "#ef4444"
                                    : routePreference === "base on weather"
                                      ? "#eab308"
                                      : "#3b82f6",
                              weight: 5,
                              opacity: 0.8,
                            })}
                          />
                        </MapContainer>
                      </div>
                    )}
                  </motion.div>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-12 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-700 mb-4">
                <Route className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No routes found</h3>
              <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
                {searchTerm || filterPreference !== "all"
                  ? "Try changing your search or filter criteria"
                  : "You haven't created any routes yet. Generate a new route to get started."}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
