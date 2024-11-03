import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarGroupAction,
    SidebarMenuButton,
    SidebarMenu,
    SidebarMenuItem,
    SidebarMenuSub,
    SidebarMenuSubItem,
    SidebarRail
} from "@/components/ui/sidebar"

import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger
} from "@/components/ui/dropdown-menu"

import { 
    Avatar,
    AvatarImage,
    AvatarFallback
} from "./ui/avatar"

import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger
} from "@/components/ui/collapsible"

import favicon from "@/assets/favicon.png"

import { ChevronUp } from "lucide-react"
import Image from "next/image"
import { Button } from "./ui/button"
import { useRouter } from "next/navigation"

export function ETS2LASidebar({toggleSidebar} : {toggleSidebar: () => void}) {
    const router = useRouter()
    return (
        <Sidebar className="border-none font-geist" variant="inset">
            <SidebarHeader className="bg-sidebarbg">
                <div className="flex gap-2 items-center">
                    <Image src={favicon} alt="ETS2LA" width={40} height={40} className="p-1 rounded-md" />
                    <div className="flex flex-col gap-0">
                        <p className="text-sm font-semibold">ETS2LA</p>
                        <p className="text-[10px] font-normal">Version 2.0.0</p>
                    </div>
                </div>
            </SidebarHeader>
            <SidebarContent className="bg-sidebarbg pt-2" >
                <SidebarGroup>
                    <SidebarGroupLabel className="font-semibold" >
                        Main
                    </SidebarGroupLabel>
                    <SidebarMenuButton className="font-medium" onClick={
                        () => router.push('/')
                    }>
                        Dashboard
                    </SidebarMenuButton>
                    <SidebarMenuButton className="font-medium">
                        Visualization
                    </SidebarMenuButton>
                </SidebarGroup>
                <SidebarGroup>
                    <SidebarGroupLabel className="font-semibold">
                        Plugins
                    </SidebarGroupLabel>
                    <SidebarMenuButton className="font-medium">
                        Manager
                    </SidebarMenuButton>
                    <SidebarMenuButton className="font-medium">
                        Performance
                    </SidebarMenuButton>
                </SidebarGroup>
                <SidebarGroup>
                    <SidebarGroupLabel className="font-semibold">
                        Help
                    </SidebarGroupLabel>
                    <SidebarMenuButton className="font-medium" onClick={
                        () => router.push('/wiki')
                    }>
                        Wiki
                    </SidebarMenuButton>
                    <SidebarMenuButton className="font-medium">
                        Chat
                    </SidebarMenuButton>
                </SidebarGroup>
            </SidebarContent>
            <SidebarRail className="z-[999]" onClick={() => {
                toggleSidebar()
            }} />
            <SidebarFooter className="bg-sidebarbg">
                <SidebarMenuButton className="font-medium">
                    Settings
                </SidebarMenuButton>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                            <SidebarMenuButton className="w-full flex justify-between">
                                <div className="flex items-center gap-2">
                                    <span>Tumppi066</span>
                                </div>
                                <ChevronUp className="w-4 h-4 justify-self-end" />
                            </SidebarMenuButton>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent
                                side="top"
                                className="w-[--radix-popper-anchor-width] bg-transparent backdrop-blur-lg backdrop-brightness-75"
                            >
                                <DropdownMenuItem>
                                    <span>Account</span>
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                    <span>Sign out</span>
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarFooter>
        </Sidebar>
    )
}
  