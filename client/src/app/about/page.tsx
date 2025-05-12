"use client";

import Breadcrumb from "@/components/Common/Breadcrumb";
import SectionTitle from "@/components/Common/SectionTitle";
import { useState } from "react";

export default function AboutPage() {
    const [activeTooltip, setActiveTooltip] = useState<number | null>(null);

    const items = [
        {
          icon: "🧠",
          title: "Intelligent Routing",
          desc: "Suggests optimal walking paths based on distance, terrain, and live weather.",
          tooltipPosition: "top-[-100px] left-[-10px]",
        },
        {
          icon: "🌦️",
          title: "Weather Aware",
          desc: "Avoid rainy, muddy or unsafe routes thanks to real-time weather data.",
          tooltipPosition: "top-[-120px] left-[0px]",
        },
        {
          icon: "⚙️",
          title: "Custom Preferences",
          desc: "Choose route length, terrain type and surface preference.",
          tooltipPosition: "top-[-100px] left-[10px]",
        },
        {
          icon: "🐾",
          title: "For Dog Lovers",
          desc: "Tailored experience made specifically for dog owners in the city.",
          tooltipPosition: "top-[-130px] right-[-10px]",
        },
      ];

  return (
    <>
      <Breadcrumb />

      <section className="relative z-10 pb-16 pt-12 md:pb-20 lg:pb-28 lg:pt-[60px] text-center">
        <div className="container mx-auto px-4">
          <SectionTitle
             title="Smart Dog Walking Assistant"
            
              paragraph="PetWalk helps you plan the perfect walk with your dog by giving you route suggestions based on distance,
              surface type, and real-time weather conditions. Designed especially for dog lovers, our app ensures each
              walk is enjoyable — rain or shine."

              center={true}
           />
          
          <div className="flex justify-center flex-wrap gap-6 max-w-4xl mx-auto overflow-visible mt-10">
            {items.map(({ icon, title, desc, tooltipPosition }, i) => (
              <div
                key={i}
                onClick={() => setActiveTooltip(i === activeTooltip ? null : i)}
                className="relative w-28 h-28 rounded-full bg-white/10 hover:bg-white/20 text-white flex flex-col items-center justify-center cursor-pointer transition duration-300"
              >
                <div className="text-3xl mb-1">{icon}</div>
                <p className="text-xs font-semibold">{title}</p>

                {activeTooltip === i && (
                  <div
                    className={`absolute z-10 w-52 p-3 bg-gray-800 text-sm text-white rounded shadow-lg ${tooltipPosition}`}
                  >
                    {desc}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
