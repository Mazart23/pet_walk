"use client"

import Breadcrumb from "@/components/Common/Breadcrumb"
import SectionTitle from "@/components/Common/SectionTitle"
import { useState } from "react"

export default function AboutPage() {
  const [activeFeature, setActiveFeature] = useState<number | null>(null)

  const items = [
    {
      icon: "🧠",
      title: "Intelligent Routing",
      desc: "Suggests optimal walking paths based on distance, terrain, and live weather.",
      color: "from-sky-500 to-cyan-500",
      bgColor: "bg-sky-500/10",
    },
    {
      icon: "🌦️",
      title: "Weather Aware",
      desc: "Avoid rainy, muddy or unsafe routes thanks to real-time weather data.",
      color: "from-sky-500 to-cyan-500",
      bgColor: "bg-sky-500/10",
    },
    {
      icon: "⚙️",
      title: "Custom Preferences",
      desc: "Choose route length, terrain type and surface preference.",
      color: "from-sky-500 to-cyan-500",
      bgColor: "bg-sky-500/10",
    },
    {
      icon: "🐾",
      title: "For Dog Lovers",
      desc: "Tailored experience made specifically for dog owners in the city.",
      color: "from-sky-500 to-cyan-500",
      bgColor: "bg-sky-500/10",
    },
  ]

  return (
    <>
       <Breadcrumb />

      <section className="pt-24 md:pt-28 z-10 pb-16 md:pb-20 lg:pb-28 lg:pt-[60px] text-center">
        <div className="container mx-auto px-4">
          <SectionTitle
            title="Smart Dog Walking Assistant"
            paragraph="PetWalk helps you plan the perfect walk with your dog by giving you route suggestions based on distance,
              surface type, and real-time weather conditions. Designed especially for dog lovers, our app ensures each
              walk is enjoyable — rain or shine."
            center={true}
          />

          <div className="flex justify-center flex-wrap gap-6 max-w-4xl mx-auto mt-10">
            {items.map(({ icon, title, desc, color, bgColor }, i) => (
              <div
                key={i}
                onClick={() => setActiveFeature(i === activeFeature ? null : i)}
                className={`
                  relative w-32 h-32 
                  rounded-2xl 
                  ${bgColor} 
                  hover:scale-105 
                  text-white 
                  flex flex-col items-center justify-center 
                  cursor-pointer 
                  transition-all duration-300 
                  border border-white/20 
                  hover:border-white/40
                  ${activeFeature === i ? "ring-2 ring-white/50 scale-105" : ""}
                `}
              >
                <div
                  className={`text-4xl mb-2 transition-transform duration-300 ${
                    activeFeature === i ? "scale-125 rotate-12" : ""
                  }`}
                >
                  {icon}
                </div>
                <p className="text-sm font-semibold text-center px-2">{title}</p>

                {activeFeature === i && (
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/20 to-white/5 border border-white/30" />
                )}
              </div>
            ))}
          </div>

          {/* Enhanced Feature Description Display */}
          {activeFeature !== null && (
            <div className="mt-12 max-w-2xl mx-auto">
              <div
                className={`relative p-8 rounded-3xl bg-gradient-to-br ${items[activeFeature].color} shadow-2xl backdrop-blur-sm transform transition-all duration-500 ease-out`}
              >
                <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 w-12 h-12 bg-white rounded-full flex items-center justify-center text-2xl shadow-lg">
                  {items[activeFeature].icon}
                </div>

                <h3 className="text-2xl font-bold text-white mb-4 pt-4">{items[activeFeature].title}</h3>

                <p className="text-white/90 text-lg leading-relaxed">{items[activeFeature].desc}</p>

                <button
                  onClick={() => setActiveFeature(null)}
                  className="mt-6 px-6 py-2 bg-white/20 hover:bg-white/30 rounded-full text-white font-medium transition-all duration-200 backdrop-blur-sm border border-white/30 hover:scale-105"
                >
                  Close
                </button>

                {/* Decorative elements */}
                <div className="absolute top-4 right-4 w-20 h-20 bg-white/10 rounded-full blur-xl" />
                <div className="absolute bottom-4 left-4 w-16 h-16 bg-white/10 rounded-full blur-lg" />
              </div>
            </div>
          )}
        </div>
      </section>
     
    </>
  )
}
