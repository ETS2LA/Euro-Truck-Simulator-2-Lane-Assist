"use client"
import {
    Menubar,
    MenubarCheckboxItem,
    MenubarContent,
    MenubarItem,
    MenubarMenu,
    MenubarRadioGroup,
    MenubarRadioItem,
    MenubarSeparator,
    MenubarShortcut,
    MenubarSub,
    MenubarSubContent,
    MenubarSubTrigger,
    MenubarTrigger,
} from "@/components/ui/menubar"
import { Badge } from "./ui/badge"
import { useRouter } from 'next/navigation';
import { useEffect } from "react";
import { useTheme } from "next-themes"
import { DiscordLogoIcon } from "@radix-ui/react-icons";
import { 
    Blocks, 
    Moon, Sun, 
    Info, Bolt, 
    SunMoon, 
    CircleHelp, 
    MessageCircleHeart, 
    HelpCircle } from "lucide-react"
import { GetVersion, CloseBackend, GetPlugins, DisablePlugin, EnablePlugin } from "@/pages/server"
import useSWR from "swr"
import {toast} from "sonner"
import { ETS2LAImmediateServer } from "./ets2la-immediate-server"

export function ETS2LAMenubar({ip}: {ip: string}) {
    const { theme, setTheme } = useTheme()
    const { push } = useRouter()
    // Get the plugins from the backend (pass ip to the GetPlugins function and refresh every second)
    const { data, error, isLoading } = useSWR(ip, () => GetPlugins(ip), { refreshInterval: 1000 })
    if (isLoading) return <Menubar><p className="absolute left-5 font-semibold text-xs text-stone-400">Loading...</p></Menubar>
    if (error){
        toast.error("Error fetching plugins from " + ip, {description: error.message})
        return <Menubar><ETS2LAImmediateServer ip={ip} /><p className="absolute left-5 font-semibold text-xs text-stone-400">{error.message}</p></Menubar>
    } 
    const plugins:string[] = [];
    for (const key in data) {
        console.log(key)
        plugins.push(key)
    }
    // Get the first characters of the plugin strings
    const pluginChars = plugins ? plugins.map((plugin) => plugin.charAt(0)) : [];
    // Remove duplicates (without Set)
    const uniqueChars:string[] = [];
    for (const char of pluginChars) {
        if (!uniqueChars.includes(char)) {
            uniqueChars.push(char);
        }
    }
    // Sort the unique characters alphabetically
    uniqueChars.sort();
return (
    <Menubar>
    <MenubarMenu>
        <MenubarTrigger className="font-bold">
            <div className="flex flex-row gap-1.5 items-center">
                ETS2LA    
            </div>
        </MenubarTrigger>
        <MenubarContent>
            <MenubarItem onClick={() => push("/")}>Main Menu</MenubarItem>
            <MenubarSeparator />
            <MenubarSub>
                    <MenubarSubTrigger>Backend</MenubarSubTrigger>
                    <MenubarSubContent>
                    <MenubarItem>Restart <MenubarShortcut>R</MenubarShortcut></MenubarItem>
                    <MenubarItem onClick={() => CloseBackend()}>
                        Quit <MenubarShortcut>Q</MenubarShortcut>
                    </MenubarItem>
                </MenubarSubContent>
            </MenubarSub>
            <MenubarSeparator />
            <MenubarItem>About ETS2LA</MenubarItem>
        </MenubarContent>
    </MenubarMenu>
    <MenubarMenu>
        <MenubarTrigger>
            <div className="flex flex-row gap-1 items-center">
                <Blocks className="w-4 h-4" />Plugins    
            </div>
        </MenubarTrigger>
        <MenubarContent>
            <MenubarItem onClick={() => push("/plugins")}>Plugin Picker</MenubarItem>
            {uniqueChars.map((char, index) => (
            <MenubarSub key={char}>
                <MenubarSubTrigger>{char}</MenubarSubTrigger>
                <MenubarSubContent>
                {plugins ? plugins.map((plugin, i) => (
                    plugin.charAt(0) === char && (
                    <MenubarSub key={i}>
                        <MenubarSubTrigger>{plugin}</MenubarSubTrigger>
                        <MenubarSubContent>
                            {data ? (data as any)[plugin]["enabled"] ? (
                                <MenubarItem onClick={() => {
                                        toast.promise(DisablePlugin(plugin, ip=ip), {
                                            loading: "Disabling " + plugin + "...",
                                            success: "Plugin " + plugin + " disabled!",
                                            error: "Error disabling " + plugin + "!"
                                        })
                                    }}>
                                    Disable
                                </MenubarItem>
                            ) : (
                                <MenubarItem onClick={() => {
                                        toast.promise(EnablePlugin(plugin, ip=ip), {
                                            loading: "Enabling " + plugin + "...",
                                            success: "Plugin " + plugin + " enabled!",
                                            error: "Error enabling " + plugin + "!"
                                        })
                                    }}>
                                    Enable
                                </MenubarItem>
                            ): null}
                            <MenubarSeparator />
                            <MenubarItem onClick={() => push("/plugins/" + plugin)}>Settings</MenubarItem>
                        </MenubarSubContent>
                    </MenubarSub>
                    )
                )) : null}
                </MenubarSubContent>
            </MenubarSub>
            ), plugins)}
        </MenubarContent>
    </MenubarMenu>
    <MenubarMenu>
        <MenubarTrigger>
            <div className="flex flex-row gap-1 items-center">
                 {theme === "light" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}Theme    
            </div>
        </MenubarTrigger>
        <MenubarContent>
            <MenubarItem onClick={() => setTheme("light")}>
                <div className="flex flex-row gap-2 items-center">
                    <Sun className="w-4 h-4"/>Light    
                </div>
            </MenubarItem>
            <MenubarItem onClick={() => setTheme("dark")}>
                <div className="flex flex-row gap-2 items-center">
                    <Moon className="w-4 h-4"/>Dark    
                </div>
            </MenubarItem>
            <MenubarSeparator />
            <MenubarItem onClick={() => setTheme("system")}>
                <div className="flex flex-row gap-2 items-center">
                    <SunMoon className="w-4 h-4"/>System    
                </div>
            </MenubarItem>
        </MenubarContent>
    </MenubarMenu>
    <MenubarMenu>
        <MenubarTrigger>
            <div className="flex flex-row gap-1 items-center">
                <Info className="w-4 h-4" />Help    
            </div>
        </MenubarTrigger>
        <MenubarContent>
            <MenubarItem onClick={() => window.open("https://wiki.tumppi066.fi", "_blank")}>
                <div className="flex flex-row gap-2 items-center">
                    <HelpCircle className="w-4 h-4"/>Wiki    
                </div>
                <MenubarShortcut>W</MenubarShortcut>
            </MenubarItem>
            <MenubarItem onClick={() => window.open("https://discord.tumppi066.fi", "_blank")}>
                <div className="flex flex-row gap-2 items-center">
                    <DiscordLogoIcon className="w-4 h-4"/>Discord    
                </div>    
                <MenubarShortcut>D</MenubarShortcut>
            </MenubarItem>
            <MenubarSeparator />
            <MenubarItem>
                <div className="flex flex-row gap-2 items-center">
                    <MessageCircleHeart className="w-4 h-4"/>Feedback    
                </div>
                <MenubarShortcut>F</MenubarShortcut>
            </MenubarItem>
        </MenubarContent>
    </MenubarMenu>
    <ETS2LAImmediateServer ip={ip} />
    </Menubar>
)
}
  