"use client"

import { SidebarProvider, SidebarTrigger, SidebarInset } from "@/components/ui/sidebar";
import { ThemeProvider } from "@/components/theme-provider";
import { ETS2LASidebar } from "@/components/sidebar";
import { useIsMobile } from "@/hooks/use-mobile";
import "./globals.css";
import WindowControls from "@/components/window-controls";
import { useState } from "react";
import { ProgressBar, ProgressBarProvider } from "react-transition-progress";
import { Toaster } from "@/components/ui/sonner"
import { States } from "@/components/states";
import { Popups } from "@/components/popups";

export default function CSRLayout({ children, }: Readonly<{ children: React.ReactNode; }>) {
    const [isCollapsed, setIsCollapsed] = useState(false);
    const isMobile = useIsMobile();

    const toggleSidebar = () => {
        setIsCollapsed(!isCollapsed);
    }

    return (
        <ThemeProvider
            attribute="class"
            defaultTheme="dark"
            enableSystem
            disableTransitionOnChange
        >
            <ProgressBarProvider>
                <Toaster position={isCollapsed ? "bottom-center" : "bottom-right"} toastOptions={{
                    unstyled: true,
                    classNames: {
                        toast: "rounded-lg shadow-lg backdrop-blur-md backdrop-brightness-75 w-[354px] border p-4 flex gap-2 items-center text-sm",
                    }
                }} />
                <WindowControls isCollapsed={isCollapsed} />
                <States />
                <Popups />
                <SidebarProvider open={!isCollapsed}>
                    <ETS2LASidebar toggleSidebar={toggleSidebar} />
                    <SidebarInset className={`relative transition-all duration-300 overflow-hidden ${isCollapsed ? "max-h-[100vh]" : "max-h-[97.6vh]"}`}>
                        <ProgressBar className="absolute h-2 z-20 rounded-tl-lg shadow-lg shadow-sky-500/20 bg-sky-500 top-0 left-0" />
                        {isMobile && <SidebarTrigger className="absolute top-2 left-2" />}
                        {children}
                    </SidebarInset>
                </SidebarProvider>
            </ProgressBarProvider>
        </ThemeProvider>
    );
}