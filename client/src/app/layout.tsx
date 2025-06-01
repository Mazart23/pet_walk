import { Inter } from "next/font/google";
import "../styles/index.css";
import dynamic from "next/dynamic";

const LayoutClientShell = dynamic(() => import("@/components/LayoutClientShell"), { ssr: false });

const inter = Inter({ subsets: ["latin"] });

export const getColorFromUsername = (username: string | undefined): string => {
  if (!username) return "#33cc33";
  const hash = Array.from(username).reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const hue = hash % 360;
  return `hsl(${hue}, 70%, 50%)`;
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head />
      <body className={`bg-[#FCFCFC] dark:bg-black ${inter.className}`}>
        <LayoutClientShell>
          {children}
        </LayoutClientShell>
      </body>
    </html>
  );
}
