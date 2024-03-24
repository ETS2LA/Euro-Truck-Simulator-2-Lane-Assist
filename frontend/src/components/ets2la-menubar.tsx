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

import { useTheme } from "next-themes"
import { Menu, Moon, Sun } from "lucide-react"
import { GetVersion, CloseBackend, GetPlugins, DisablePlugin, EnablePlugin } from "@/app/server"
import useSWR from "swr"

export function ETS2LAMenubar() {
    const { setTheme } = useTheme()
    const { data, error, isLoading } = useSWR("http://localhost:37520/api/plugins", GetPlugins)
    if (isLoading) return <Menubar>Loading...</Menubar>
    if (error) return <Menubar>Error loading plugins</Menubar>
    const plugins:string[] = [];
    console.log(data)
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
        <MenubarTrigger>ETS2LA</MenubarTrigger>
        <MenubarContent>
        <MenubarItem onClick={() => GetVersion()}>
            Refresh <MenubarShortcut>Win+R</MenubarShortcut>
        </MenubarItem>
        <MenubarSeparator />
        <MenubarSub>
            <MenubarSubTrigger>Backend</MenubarSubTrigger>
            <MenubarSubContent>
            <MenubarItem>Restart</MenubarItem>
            </MenubarSubContent>
        </MenubarSub>
        <MenubarSeparator />
        <MenubarItem onClick={() => CloseBackend()}>
            Quit <MenubarShortcut>Win+P</MenubarShortcut>
        </MenubarItem>
        </MenubarContent>
    </MenubarMenu>
    <MenubarMenu>
        <MenubarTrigger>Plugins</MenubarTrigger>
        <MenubarContent>
            {uniqueChars.map((char, index) => (
            <MenubarSub key={char}>
                <MenubarSubTrigger>{char}</MenubarSubTrigger>
                <MenubarSubContent>
                {plugins ? plugins.map((plugin, i) => (
                    plugin.charAt(0) === char && (
                    <MenubarSub key={i}>
                        <MenubarSubTrigger>{plugin}</MenubarSubTrigger>
                        <MenubarSubContent>
                            <MenubarItem>Settings</MenubarItem>
                            <MenubarSeparator />
                            {data[plugin]["enabled"] ? (
                                <MenubarItem onClick={() => DisablePlugin(plugin)}>
                                    Disable
                                </MenubarItem>
                            ) : (
                                <MenubarItem onClick={() => EnablePlugin(plugin)}>
                                    Enable
                                </MenubarItem>
                            )}
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
        <MenubarTrigger>Theme</MenubarTrigger>
        <MenubarContent>
            <MenubarItem onClick={() => setTheme("light")}>Light</MenubarItem>
            <MenubarItem onClick={() => setTheme("dark")}>Dark</MenubarItem>
            <MenubarSeparator />
            <MenubarItem onClick={() => setTheme("system")}>System</MenubarItem>
        </MenubarContent>
    </MenubarMenu>
    </Menubar>
)
}
  