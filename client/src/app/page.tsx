import { Metadata } from "next";
import ScrollUp from "@/components/Common/ScrollUp";

export const metadata: Metadata = {
  title: "PetWalk",
  description: "This is an app for pet lovers!",
  // other metadata
};

export default function Home() {
  return (
    <>
      <ScrollUp />
      <div className="flex min-h-[100vh]">
      </div>
    </>
  );
}