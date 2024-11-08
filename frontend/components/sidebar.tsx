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

import { useProgress } from "react-transition-progress"
import { startTransition } from "react"

import { 
    ChevronUp, 
    House,
    TvMinimal,
    ChartNoAxesGantt,
    ChartArea,
    BookText,
    MessageSquare,
    Bolt,
    User,
    UserCog,
    UserRoundMinus
} from "lucide-react"
import Image from "next/image"
import { Button } from "./ui/button"
import { useRouter, usePathname } from "next/navigation"

import { toast } from "sonner"

export function ETS2LASidebar({toggleSidebar} : {toggleSidebar: () => void}) {
    const startProgress = useProgress()
    const router = useRouter()
    const path = usePathname()
    console.log(path)

    const buttonClassName = (targetPath: string) => {
        if(path == targetPath) {
            return "font-medium border-l-2 rounded-l-none"
        } else {
            return "font-medium"
        }
    }

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
            <SidebarContent className="bg-sidebarbg pt-2 custom-scrollbar" >
                <SidebarGroup>
                    <SidebarGroupLabel className="font-semibold" >
                        Main
                    </SidebarGroupLabel>
                    <SidebarMenuButton className={buttonClassName("/")} onClick={
                        () => {
                            startTransition(async () => {
                                startProgress()
                                router.push('/')
                                await new Promise(resolve => setTimeout(resolve, 50))
                            })
                        }
                    }>
                        <House /> Dashboard
                    </SidebarMenuButton>
                    <SidebarMenuButton className={buttonClassName("/visualization")} onClick={
                        () => {
                            startTransition(async () => {
                                startProgress()
                                router.push('/visualization')
                                await new Promise(resolve => setTimeout(resolve, 50))
                            })
                        }
                    }>
                        <TvMinimal /> Visualization
                    </SidebarMenuButton>
                </SidebarGroup>
                <SidebarGroup>
                    <SidebarGroupLabel className="font-semibold">
                        Plugins
                    </SidebarGroupLabel>
                    <SidebarMenuButton className={buttonClassName("/plugins")} onClick={
                        () => {
                            toast.success("Coming soon!")
                        }
                    }>
                        <ChartNoAxesGantt /> Manager
                    </SidebarMenuButton>
                    <SidebarMenuButton className={buttonClassName("/performance")} onClick={
                        () => {
                            toast.success("Coming soon!")
                        }
                    }>
                        <ChartArea /> Performance
                    </SidebarMenuButton>
                </SidebarGroup>
                <SidebarGroup>
                    <SidebarGroupLabel className="font-semibold">
                        Help
                    </SidebarGroupLabel>
                    <SidebarMenuButton className={buttonClassName("/wiki")} onClick={
                        () => {
                            startTransition(async () => {
                                startProgress()
                                router.push('/wiki')
                                await new Promise(resolve => setTimeout(resolve, 50))
                            })
                        }
                    }>
                        <BookText /> Wiki
                    </SidebarMenuButton>
                    <SidebarMenuButton className={buttonClassName("/chat")} onClick={
                        () => {
                            toast.success("Coming soon!")
                        }
                    }>
                        <MessageSquare /> Chat
                    </SidebarMenuButton>
                </SidebarGroup>
            </SidebarContent>
            <SidebarRail className="z-[999]" onClick={() => {
                toggleSidebar()
            }} />
            <SidebarFooter className="bg-sidebarbg">
                <SidebarMenuButton className={buttonClassName("/settings")} onClick={
                        () => {
                            startTransition(async () => {
                                startProgress()
                                router.push('/settings')
                                await new Promise(resolve => setTimeout(resolve, 50))
                            })
                        }
                    }>
                    <Bolt /> Settings
                </SidebarMenuButton>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                            <SidebarMenuButton className="w-full flex justify-between">
                                <div className="flex items-center gap-2">
                                    <span>Anonymous</span>
                                </div>
                                <ChevronUp className="w-4 h-4 justify-self-end" />
                            </SidebarMenuButton>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent
                                side="top"
                                className="w-[--radix-popper-anchor-width] bg-transparent backdrop-blur-lg backdrop-brightness-75"
                            >
                                <DropdownMenuItem>
                                    <UserCog /> <span>Account</span>
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                    <UserRoundMinus /> <span>Sign out</span>
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarFooter>
        </Sidebar>
    )
}
  