'use client';
import React, { useState } from 'react';

export default function RouteConfig() {
  const [distance, setDistance] = useState(2);
  const [park, setPark] = useState(true);
  const [sidewalk, setSidewalk] = useState(false);

  const handleSubmit = () => {
    // TODO: wyślij dane na backend
    console.log({ distance, park, sidewalk });
  };

  return (
    <div className="bg-white dark:bg-gray-800 text-black dark:text-white rounded-xl shadow-md p-6 max-w-md">

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
        <input
          type="checkbox"
          checked={park}
          onChange={() => setPark(!park)}
        />
        <span className="ml-2">Preferuję parki</span>
      </label>

      <label className="block mb-4">
        <input
          type="checkbox"
          checked={sidewalk}
          onChange={() => setSidewalk(!sidewalk)}
        />
        <span className="ml-2">Preferuję chodniki</span>
      </label>

      <button
        onClick={handleSubmit}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Pokaż trasę
      </button>
    </div>
  );
}
