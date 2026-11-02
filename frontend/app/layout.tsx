import type { Metadata } from "next";
import type React from "react";
import "./globals.css";
import "./variant-picker.css";

import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";
import { BagProvider } from "@/components/BagProvider";

export const metadata: Metadata = {
  title: {
    default: "EVU — A Study in Modern Elegance",
    template: "%s | EVU",
  },
  description:
    "Explore the EVU edit. Considered contemporary fashion and a more refined wardrobe.",
  robots: {
    index: true,
    follow: true,
  },
};

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <BagProvider>
          <SiteHeader />
          {children}
          <SiteFooter />
        </BagProvider>
      </body>
    </html>
  );
}