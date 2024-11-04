"use client";
import { Menubar, MenubarCheckboxItem, MenubarContent, MenubarItem,
    MenubarMenu, MenubarRadioGroup, MenubarRadioItem, MenubarSeparator,
    MenubarShortcut, MenubarSub, MenubarSubContent, MenubarSubTrigger,
    MenubarTrigger } from "@/components/ui/menubar"
import { Separator } from "./ui/separator";
import { Badge } from "./ui/badge"
import { useRouter } from 'next/navigation';
import { useEffect, useState, useLayoutEffect } from "react";
import { useTheme } from "next-themes"
import { DiscordLogoIcon } from "@radix-ui/react-icons";
import { Blocks, Moon, Sun, Info, Bolt, SunMoon, CircleHelp, 
    MessageCircleHeart, HelpCircle, Settings, 
    MessageCircleQuestion, TextSearch, MessagesSquare,
    MessageSquare} from "lucide-react"
import { GetVersion, CloseBackend, GetPlugins, 
    DisablePlugin, EnablePlugin, RestartBackend, ColorTitleBar } from "@/pages/backend"
import { SetSettingByKey } from "@/pages/settingsServer";
import useSWR from "swr"
import {toast} from "sonner"
import { ETS2LAImmediateServer } from "./ets2la_immediate_server"
import { translate } from "@/pages/translation";
import { useRouter as routerUseRouter } from 'next/router';
import { DeleteUser } from "@/pages/account";

export function ETS2LAMenubar({ ip, onLogout, isCollapsed }: { ip: string, onLogout: () => void, isCollapsed?: boolean }) {
    const [dragging, setDragging] = useState(false);
    const [windowPosition, setWindowPosition] = useState({ x: 0, y: 0 });
    const [lastMousePosition, setLastMousePosition] = useState({ x: 0, y: 0 });
    const [clickOffset, setClickOffset] = useState({ x: 0, y: 0 });
    const { theme, setTheme } = useTheme();
    const { push } = useRouter();
    const { pathname } = routerUseRouter();
    const isBasic = pathname.includes("basic");

    const { data, error, isLoading } = useSWR("plugins", () => GetPlugins(ip), { refreshInterval: 1000 });
    const plugins = data ? Object.keys(data).filter(key => key !== "Global" && key !== "global_json") : [];
    // @ts-ignore
    const pluginChars = plugins.map(plugin => data[plugin]?.file ? translate(data[plugin].file.name).charAt(0) : plugin.charAt(0));
    const uniqueChars = Array.from(new Set(pluginChars)).sort();

    const SetThemeColor = (theme: string) => {
        setTheme(theme);
        toast.promise(ColorTitleBar(ip, theme), {
            loading: translate("frontend.menubar.setting_theme", translate(`frontend.theme.${theme}`)),
            success: translate("frontend.menubar.theme_set", translate(`frontend.theme.${theme}`)),
            error: translate("frontend.menubar.error_setting_theme", translate(`frontend.theme.${theme}`)),
        });
    };

    useEffect(() => {
        const initialWindowPosition = { x: window.screenX, y: window.screenY };
        setWindowPosition(initialWindowPosition);
    }, []);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (dragging) {
                const newX = windowPosition.x + (e.screenX - lastMousePosition.x);
                const newY = windowPosition.y + (e.screenY - lastMousePosition.y);
                setWindowPosition({ x: newX, y: newY });
                // @ts-ignore
                window.pywebview._bridge.call('pywebviewMoveWindow', [newX, newY], "move");
                setLastMousePosition({ x: e.screenX, y: e.screenY });
            }
        };

        const handleMouseUp = () => {
            setDragging(false);
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };

        if (dragging) {
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
        }

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }, [dragging, windowPosition, lastMousePosition]);

    const handleMouseDown = (e: React.MouseEvent) => {
        if (e.target instanceof HTMLElement && e.target.classList.contains('pywebview-drag-region')) {
            e.preventDefault();
            setDragging(true);
            setLastMousePosition({ x: e.screenX, y: e.screenY });
            setClickOffset({
                x: e.clientX - e.target.getBoundingClientRect().left,
                y: e.clientY - e.target.getBoundingClientRect().top,
            });
        }
    };

    function getMenubarClassname(collapsed: any, isBasic: any) {
        return isBasic 
            ? (collapsed ? "pywebview-drag-region absolute top-3 left-[8.75vw] right-[8.75vw] bg-transparent border-none bg-background"
                         : "pywebview-drag-region absolute top-3 left-3 right-3 bg-transparent border-none bg-background")
            : "pywebview-drag-region";
    }

    // Return loading or error states early
    if (isLoading) {
        return <Menubar><p className="absolute left-5 font-semibold text-xs text-stone-400">{translate("loading")}</p></Menubar>;
    }

    if (error) {
        toast.error(translate("frontend.menubar.error_fetching_plugins", ip), { description: error.message });
        return <Menubar><ETS2LAImmediateServer ip={ip} /><p className="absolute left-5 font-semibold text-xs text-stone-400">{error.message}</p></Menubar>;
    }

    return (
        <div className={isBasic && "p-1.5" || "pywebview-drag-region"} onMouseDown={handleMouseDown}>
            <Menubar className={getMenubarClassname(isCollapsed, isBasic)}>
            <MenubarMenu>
                <MenubarTrigger className="font-bold">
                    <div className="flex flex-row gap-1.5 items-center">
                        ETS2LA    
                    </div>
                </MenubarTrigger>
                <MenubarContent>
                    <MenubarItem onClick={() => push("/")}>{translate("frontend.menubar.main_menu")}</MenubarItem>
                    <MenubarSeparator />
                    <MenubarSub>
                            <MenubarSubTrigger>{translate("frontend.menubar.backend")}</MenubarSubTrigger>
                            <MenubarSubContent>
                            <MenubarItem onClick={() => RestartBackend()}>{translate("frontend.menubar.backend.restart")} <MenubarShortcut>R</MenubarShortcut></MenubarItem>
                            <MenubarItem onClick={() => CloseBackend()}>
                                {translate("frontend.menubar.backend.quit")} <MenubarShortcut>Q</MenubarShortcut>
                            </MenubarItem>
                        </MenubarSubContent>
                    </MenubarSub>
                    <MenubarSeparator />
                    <MenubarSub>
                        <MenubarSubTrigger>{translate("frontend.menubar.account")}</MenubarSubTrigger>
                        <MenubarSubContent>
                            {!isBasic &&
                                <>
                                    <MenubarItem onClick={() => onLogout()}>{translate("frontend.menubar.account.logout")}</MenubarItem>
                                    <MenubarItem>{translate("frontend.menubar.account.settings")}</MenubarItem>
                                    <MenubarSeparator />
                                    <MenubarItem onClick={() => {DeleteUser(); onLogout()}} className={theme === "dark" ? "bg-red-900 rounded-sm rounded-t-none" : "bg-red-500 text-white rounded-sm rounded-t-none"}>{translate("frontend.menubar.account.delete")}</MenubarItem>
                                </>
                                || 
                                <MenubarItem onClick={() => push("/")}>{translate("frontend.menubar.enter_normal_mode")}</MenubarItem>
                            }
                        </MenubarSubContent>
                    </MenubarSub>
                    <MenubarSeparator />
                    <MenubarItem>{translate("frontend.menubar.about")}</MenubarItem>
                </MenubarContent>
            </MenubarMenu>
            <Separator orientation="vertical" className="m-1" />
            {
                !isBasic && (
                    <MenubarMenu>
                        <MenubarTrigger>
                            <div className="flex flex-row gap-1 items-center">
                                <Blocks className="w-4 h-4" />{translate("frontend.menubar.plugins")}    
                            </div>
                        </MenubarTrigger>
                        <MenubarContent>
                            <MenubarItem onClick={() => push("/plugins")}>{translate("frontend.menubar.plugins.plugin_picker")}</MenubarItem>
                            {uniqueChars.map((char, index) => (
                                <MenubarSub key={char}>
                                <MenubarSubTrigger>{char}</MenubarSubTrigger>
                                <MenubarSubContent>
                                {plugins ? plugins.map((plugin, i) => (
                                    (data ? (data as any)[plugin]["description"] ? translate((data as any)[plugin]["description"]["name"]).charAt(0) : plugin.charAt(0) : plugin.charAt(0)) === char && (
                                    <MenubarSub key={i}>
                                        <MenubarSubTrigger>{data ? translate((data as any)[plugin]["description"]["name"]) : plugin}</MenubarSubTrigger>
                                        <MenubarSubContent>
                                            {data ? (data as any)[plugin]["enabled"] ? (
                                                <MenubarItem onClick={() => {
                                                        toast.promise(DisablePlugin(plugin, ip=ip), {
                                                            loading: translate("frontend.menubar.plugin.disabling"),
                                                            success: translate("frontend.menubar.plugin.disabled", data ? (data as any)[plugin]["description"] ? translate((data as any)[plugin]["description"]["name"]) : plugin : plugin),
                                                            error: translate("frontend.menubar.plugin.error_disabling"),
                                                        })
                                                    }}>
                                                    {translate("frontend.menubar.plugins.plugin.disable")}
                                                </MenubarItem>
                                            ) : (
                                                <MenubarItem onClick={() => {
                                                    toast.promise(EnablePlugin(plugin, ip=ip), {
                                                            loading: translate("frontend.menubar.plugin.enabling"),
                                                            success: translate("frontend.menubar.plugin.enabled", data ? (data as any)[plugin]["description"] ? translate((data as any)[plugin]["description"]["name"]) : plugin : plugin),
                                                            error: translate("frontend.menubar.plugin.error_enabling"),
                                                        })
                                                    }}>
                                                    {translate("frontend.menubar.plugins.plugin.enable")}
                                                </MenubarItem>
                                            ): null}
                                            <MenubarSeparator />
                                            <MenubarItem onClick={() => push("/plugins/" + plugin)}>{translate("frontend.menubar.plugins.plugin.settings")}</MenubarItem>
                                        </MenubarSubContent>
                                    </MenubarSub>
                                    )
                                )) : null}
                                </MenubarSubContent>
                            </MenubarSub>
                            ), plugins)}
                            <MenubarSeparator />
                            <MenubarItem onClick={() => push("/performance")}>{translate("frontend.menubar.plugins.performance")}</MenubarItem>
                        </MenubarContent>
                    </MenubarMenu>
                )
            }
            {!isBasic && (
                <MenubarMenu>
                    <MenubarTrigger>
                        <div className="flex flex-row gap-1 items-center">
                            {theme === "light" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}{translate("frontend.menubar.theme")}    
                        </div>
                    </MenubarTrigger>
                    <MenubarContent>
                        <MenubarItem onClick={() => {
                            SetThemeColor("light")
                            SetSettingByKey("global", "theme", "light", ip=ip)
                        }}>
                            <div className="flex flex-row gap-2 items-center">
                                <Sun className="w-4 h-4"/>{translate("frontend.theme.light")}    
                            </div>
                        </MenubarItem>
                        <MenubarItem onClick={() => {
                            SetThemeColor("dark")
                            SetSettingByKey("global", "theme", "dark", ip=ip)
                        }}>
                            <div className="flex flex-row gap-2 items-center">
                                <Moon className="w-4 h-4"/>{translate("frontend.theme.dark")}    
                            </div>
                        </MenubarItem>
                    </MenubarContent>
                </MenubarMenu>
            )}
            <MenubarMenu>
                <MenubarTrigger>
                    <div className="flex flex-row gap-1 items-center">
                        <Settings className="w-4 h-4"/>{translate("frontend.menubar.settings")}
                    </div>
                </MenubarTrigger>
                <MenubarContent>
                    <MenubarItem onClick={() => push("/settings")}>{translate("frontend.menubar.settings")}</MenubarItem>
                </MenubarContent>
            </MenubarMenu>
            <MenubarMenu>
                <MenubarTrigger>
                    <div className="flex flex-row gap-1 items-center">
                        <Info className="w-4 h-4" />{translate("frontend.menubar.help")}    
                    </div>
                </MenubarTrigger>
                <MenubarContent>
                    <MenubarItem onClick={() => window.open("https://wiki.tumppi066.fi", "_blank")}>
                        <div className="flex flex-row gap-2 items-center">
                            <HelpCircle className="w-4 h-4"/>{translate("frontend.menubar.help.wiki")}    
                        </div>
                        <MenubarShortcut>W</MenubarShortcut>
                    </MenubarItem>
                    <MenubarItem onClick={() => window.open("https://discord.tumppi066.fi", "_blank")}>
                        <div className="flex flex-row gap-2 items-center">
                            <DiscordLogoIcon className="w-4 h-4"/>{translate("frontend.menubar.help.discord")}    
                        </div>    
                        <MenubarShortcut>D</MenubarShortcut>
                    </MenubarItem>
                    <MenubarSeparator />
                    <MenubarItem onClick={() => push("/feedback")}>
                        <div className="flex flex-row gap-2 items-center">
                            <MessageCircleHeart className="w-4 h-4"/>{translate("frontend.menubar.help.feedback")}    
                        </div>
                        <MenubarShortcut>F</MenubarShortcut>
                    </MenubarItem>
                </MenubarContent>
            </MenubarMenu>
            {!isBasic && (  
                <MenubarMenu>
                    <MenubarTrigger>
                        <div className="flex flex-row gap-1 items-center">
                            <MessageCircleQuestion className="w-4 h-4" />Support
                        </div>
                    </MenubarTrigger>
                    <MenubarContent>
                        <MenubarItem onClick={() => push("/support") }>
                            <div className="flex flex-row gap-2 items-center">
                                <MessageSquare className="w-4 h-4"/>Chat    
                            </div>
                            <MenubarShortcut>C</MenubarShortcut>
                        </MenubarItem>
                        <MenubarSeparator/>
                        <MenubarItem>
                            <div className="flex flex-row gap-2 items-center">
                                <Info className="w-4 h-4"/>Resources 
                            </div>    
                            <MenubarShortcut>R</MenubarShortcut>
                        </MenubarItem>
                    </MenubarContent>
                </MenubarMenu>
            )}
            </Menubar>
            <ETS2LAImmediateServer ip={ip} collapsed={isCollapsed} />
        </div>
    )
}
