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

import { Update, CheckForUpdate, GetMetadata } from "@/apis/backend"

import { useProgress } from "react-transition-progress"
import { startTransition } from "react"
import { ip } from "@/apis/backend"
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
    UserRoundMinus,
    ArrowLeftToLine
} from "lucide-react"

import { Button } from "./ui/button"
import { useRouter, usePathname } from "next/navigation"
import { useTheme } from "next-themes"
import { toast } from "sonner"

import useSWR from "swr"

export function ETS2LASidebar({toggleSidebar} : {toggleSidebar: () => void}) {
    const { data: update_data } = useSWR("update", CheckForUpdate)
    const { data: metadata } = useSWR("metadata", GetMetadata)
    const startProgress = useProgress()
    const router = useRouter()
    const path = usePathname()
    const { theme } = useTheme();

    const buttonClassName = (targetPath: string) => {
        if(path == targetPath) {
            return "font-medium bg-secondary transition-all hover:shadow-md"
        } else {
            return "font-medium transition-all hover:shadow-md"
        }
    }

    return (
        <Sidebar className="border-none font-geist" variant="inset">
            <SidebarHeader className="bg-sidebarbg w-full">
                <div className="flex flex-col gap-4 items-center w-full">
                    <div className="flex flex-col gap-1 w-full">
                        <p className="text-sm font-semibold pl-2">ETS2LA</p>
                        <p className="text-xs pl-2 font-semibold text-muted-foreground">{metadata && "v" + metadata.version || "ERROR: please refresh the page or purge .next/cache"}</p>
                    </div>
                    { update_data && 
                        <Button size={"sm"} variant={"outline"} className="w-full" onClick={() => { Update() }}>
                            Updates Available
                        </Button>
                    }
                </div>
            </SidebarHeader>
            <SidebarContent className="bg-sidebarbg custom-scrollbar" >
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
                            startTransition(async () => {
                                startProgress()
                                router.push('/plugins')
                                await new Promise(resolve => setTimeout(resolve, 50))
                            })
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
                            startTransition(async () => {
                                startProgress()
                                router.push('/chat')
                                await new Promise(resolve => setTimeout(resolve, 50))
                            })
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
                            <SidebarMenuButton className="w-full flex justify-between hover:shadow-md transition-all">
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
                    
                    {/* DO NOT UNCOMMENT - This breaks the app on startup
                    <SidebarMenuItem>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                            <SidebarMenuButton className="w-full flex justify-between hover:shadow-md transition-all">
                                <div className="flex items-center gap-2">
                                    <span>ETS2LA Mobile</span>
                                </div>
                                <ChevronUp className="w-4 h-4 justify-self-end" />
                            </SidebarMenuButton>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent
                                side="top"
                                className="w-[--radix-popper-anchor-width] bg-transparent backdrop-blur-md backdrop-brightness-90 text-center p-3"
                            >
                                <QRCodeSVG value={"https://example.com"} className="justify-self-center pb-1" />
                                <div className="flex items-center w-full justify-center">
                                    <div className="flex-1 h-px bg-muted-foreground mx-2"></div>
                                    <span className="text-xs whitespace-nowrap text-muted-foreground">OR</span>
                                    <div className="flex-1 h-px bg-muted-foreground mx-2"></div>
                                </div>
                                <p className="text-xs">
                                    <a href={"http://" + ip + ":3005"} className="underline" target="_blank" rel="noopener noreferrer">
                                        {"http://" + ip + ":3005"}
                                    </a>
                                </p>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </SidebarMenuItem>
                    */}
                </SidebarMenu>
            </SidebarFooter>
        </Sidebar>
    )
}
  