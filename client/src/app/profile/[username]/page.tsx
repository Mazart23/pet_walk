"use client";
import { useParams } from "next/navigation";
import { useEffect, useState } from 'react';
import { fetchRoutes, deleteRoute } from '@/app/Api';
import useToken from '@/components/contexts/TokenContext';
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import { Feature } from 'geojson';



export default function UserProfilePage() {
  const params = useParams();
  const username = params.username;

  const [routes, setRoutes] = useState([]);
  const [expandedRouteId, setExpandedRouteId] = useState<number | null>(null);
  const { token } = useToken();

  useEffect(() => {
    if (token) {
      fetchRoutes(token).then(res => {
        if (res?.routes) {
          setRoutes(res.routes);
        }
      });
    }
  }, [token]);

  const handleDelete = async (routeId: number) => {
    if (!token) return;
    const ok = await deleteRoute(token, routeId);
    if (ok) {
      setRoutes(routes.filter(r => r.id !== routeId));
    }
  };

  return (
    <>
    <section className="min-h-[60vh] flex items-center justify-center text-center">
    <div>
    <h1 className="text-4xl font-bold mb-4"> </h1>

    <p className="text-lg opacity-0">costam</p>
    <p className="text-lg opacity-0">costam</p>
    <p className="text-lg opacity-0">costam</p>

    </div>
    </section>

    <div className="p-6 text-white">
      <h1 className="text-3xl font-bold">Profil użytkownika: {username}</h1>
      <p>Tu będzie więcej szczegółów o użytkowniku!</p>
      {routes.length > 0 ? (
         <ul className="space-y-4">
         {routes.map((route) => (
           <li
             key={route.id}
             className="bg-gray-100 dark:bg-gray-800 text-black dark:text-white p-4 rounded shadow"
           >
             <div className="flex justify-between items-center">
               <div>
                 <p><strong>Dystans:</strong> {(route.real_distance / 1000).toFixed(2)} km</p>
                 <p>
                   <strong>Preferencje:</strong>{" "}
                   {route.declared_parameters.is_prefer_green
                     ? "prefer zielone"
                     : route.declared_parameters.is_avoid_green
                     ? "unikaj zielonych"
                     : "domyślne"}
                 </p>
                 <p><strong>Data:</strong> {new Date(route.timestamp).toLocaleString()}</p>
               </div>
               <div className="flex flex-col items-end gap-2">
                 <button
                   onClick={() =>
                     setExpandedRouteId((prev) =>
                       prev === route.id ? null : route.id
                     )
                   }
                   className="text-sm bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded"
                 >
                   {expandedRouteId === route.id ? "Ukryj trasę" : "Pokaż trasę"}
                 </button>
                 <button
                   onClick={() => handleDelete(route.id)}
                   className="text-sm bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded"
                 >
                   🗑 Usuń
                 </button>
               </div>
             </div>

             {expandedRouteId === route.id && (
               <div className="mt-4">
                 <MapContainer
                   center={[
                     route.declared_parameters.point.latitude,
                     route.declared_parameters.point.longitude,
                   ]}
                   zoom={13}
                   className="w-full h-[300px] rounded"
                 >
                   <TileLayer
                     attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
                     url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                   />
                   <GeoJSON
                    data={{
                        type: "Feature",
                        geometry: route.route,
                        properties: {},
                    } as Feature}
                    />
                 </MapContainer>
               </div>
             )}
           </li>
         ))}
       </ul>
     ) : (
       <p>Brak zapisanych tras.</p>
     )}
   </div>
 </>
);
}