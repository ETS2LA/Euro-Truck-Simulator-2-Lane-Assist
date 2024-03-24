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
import { GetVersion, CloseBackend, GetPlugins } from "@/app/server"

export async function ETS2LAMenubar() {
    const { setTheme } = useTheme()
    const plugins = await GetPlugins() // Array of plugin strings
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
            {plugins.map((plugin) => (
                <MenubarSub key={plugin}>
                    <MenubarSubTrigger>{plugin}</MenubarSubTrigger>
                    <MenubarSubContent>
                        <MenubarItem>Enable</MenubarItem>
                        <MenubarItem>Disable</MenubarItem>
                        <MenubarSeparator />
                        <MenubarItem>Load UI</MenubarItem>
                    </MenubarSubContent>
                </MenubarSub>
            ))}
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
  