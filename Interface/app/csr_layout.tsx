"use client"

import { SidebarProvider, SidebarTrigger, SidebarInset } from "@/components/ui/sidebar";
import { ThemeProvider } from "@/components/theme-provider";
import { ETS2LASidebar } from "@/components/sidebar";
import { useIsMobile } from "@/hooks/use-mobile";
import "./globals.css";
import WindowControls from "@/components/window-controls";
import React, { useState, useEffect } from "react";
import { ProgressBar, ProgressBarProvider } from "react-transition-progress";
import { Toaster } from "@/components/ui/sonner"
import { States } from "@/components/states";
import { Popups } from "@/components/popups";
import { changeLanguage, loadTranslations } from "@/apis/translation";
import { GetCurrentLanguage } from "@/apis/backend";
import { Fireworks } from "@fireworks-js/react";
import { GetSettingByKey } from "@/apis/settings";
import { Disclaimer } from "@/components/disclaimer";
import AccountHandler from "@/apis/account";
import Snowfall from "react-snowfall"
import useSWR from "swr";
import Loader from "@/components/loader";
import { useCollapsed } from "@/contexts/collapsed";

export default function CSRLayout({ children, }: Readonly<{ children: React.ReactNode; }>) {
    const { data: language, isLoading: loadingLanguage } = useSWR("language", GetCurrentLanguage, { refreshInterval: 2000 });
    const { isCollapsed, setIsCollapsed } = useCollapsed();
    const [isSnowAllowed, setIsSnowAllowed] = useState(false);
    const [areFireworksAllowed, setAreFireworksAllowed] = useState(false);
    const [loadingTranslations, setLoadingTranslations] = useState(true);
    const isMobile = useIsMobile();

    useEffect(() => {
        if (language) {
            changeLanguage(language);
            setLoadingTranslations(true);
            loadTranslations().then(() => {
                setLoadingTranslations(false);
            });
        }
    }, [language]);

    useEffect(() => {
        GetSettingByKey("global", "snow", true).then((snow) => {
            setIsSnowAllowed(snow === true);
        });
        GetSettingByKey("global", "fireworks", true).then((fireworks) => {
            setAreFireworksAllowed(fireworks === true);
        });
    });

    const date = new Date();
    const month = date.getMonth();
    const day = date.getDate();
    const isNewYear = ((month === 0 && day === 1) || (month === 11 && day === 31)) && areFireworksAllowed;
    const isSnowing = (month >= 10 || month === 0) && isSnowAllowed;

    useEffect(() => {
        loadTranslations().then(() => {
            setLoadingTranslations(false);
        });
    }, []);

    const toggleSidebar = () => {
        setIsCollapsed(!isCollapsed);
    }

    return (
        <div className="h-screen w-screen flex overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-full pointer-events-none z-50">
                {isSnowing && <Snowfall snowflakeCount={50} speed={[-0.5, 0.5]} wind={[-0.5, 0.5]} radius={[0, 0.5]} />}
                {isNewYear && <Fireworks className="w-full h-full" options={{
                    rocketsPoint: { min: 0, max: 100 },
                    delay: { min: 500, max: 2000 },
                }} />
                }
            </div>
            <AccountHandler />
            <ThemeProvider
                attribute="class"
                defaultTheme="dark"
                enableSystem
                disableTransitionOnChange
            >
                {(loadingTranslations || loadingLanguage) && (
                    <div className="absolute top-0 left-0 w-full h-full bg-sidebar flex items-center justify-center flex-col gap-2">
                        <Loader className={"opacity-50"} />
                        <p className="font-geist text-muted-foreground">
                            Loading translations...
                        </p>
                    </div>
                ) || (
                    <>
                        <Disclaimer />
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
                    </>
                )}
            </ThemeProvider>
        </div>
    );
}