"use client"
import { SidebarProvider, SidebarTrigger, SidebarInset } from "@/components/ui/sidebar";
import { ThemeProvider } from "@/components/theme-provider";
import { ETS2LASidebar } from "@/components/sidebar";
import { useIsMobile } from "@/hooks/use-mobile";
import localFont from "next/font/local";
import "./globals.css";
import WindowControls from "@/components/window-controls";
import { useState } from "react";

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

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    const [isCollapsed, setIsCollapsed] = useState(false);
    const isMobile = useIsMobile();

    const toggleSidebar = () => {
        setIsCollapsed(!isCollapsed);
    }

    return (
        <html lang="en">
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            </head>
            <body
                className={`${geistSans.variable} ${geistMono.variable} antialiased bg-sidebarbg overflow-hidden`}
            >
                <ThemeProvider
                    attribute="class"
                    defaultTheme="system"
                    enableSystem
                    disableTransitionOnChange
                >
                    <WindowControls isCollapsed={isCollapsed} />
                    <SidebarProvider open={!isCollapsed}>
                        <ETS2LASidebar toggleSidebar={toggleSidebar} />
                        <SidebarInset className="relative transition-all">
                            {isMobile && <SidebarTrigger className="absolute top-2 left-2" />}
                            {children}
                        </SidebarInset>
                    </SidebarProvider>
                </ThemeProvider>
            </body>
        </html>
    );
}
