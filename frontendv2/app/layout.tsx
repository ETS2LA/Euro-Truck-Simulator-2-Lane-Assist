import { SidebarProvider, SidebarTrigger, SidebarInset } from "@/components/ui/sidebar"
import { ThemeProvider } from "@/components/theme-provider"
import { ETS2LASidebar } from "@/components/sidebar"
import localFont from "next/font/local";
import type { Metadata } from "next";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "ETS2LA",
  description: "Euro Truck Simulator 2 Lane Assist",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-sidebarbg`}
      >
        <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
        >
          <SidebarProvider className="">
            <ETS2LASidebar />
            <SidebarInset>
                {children}
            </SidebarInset>
          </SidebarProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
