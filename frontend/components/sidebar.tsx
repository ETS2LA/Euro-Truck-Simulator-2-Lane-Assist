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
import { translate } from "@/apis/translation"
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
                        <p className="text-sm font-semibold pl-2 cursor-pointer" onMouseDown={() => {
                            startTransition(async () => {
                                startProgress()
                                router.push('/about')
                                await new Promise(resolve => setTimeout(resolve, 50))
                            })
                        }}>ETS2LA</p>
                        <p className="text-xs pl-2 font-semibold text-muted-foreground">{metadata && "v" + metadata.version || "ERROR: please refresh the page or purge .next/cache"}</p>
                    </div>
                    { update_data && 
                        <Button size={"sm"} variant={"outline"} className="w-full" onMouseDown={() => { Update() }}>
                            {translate("frontend.sidebar.updates_available")}
                        </Button>
                    }
                </div>
            </SidebarHeader>
            <SidebarContent className="bg-sidebarbg custom-scrollbar" >
                <SidebarGroup>
                    <SidebarGroupLabel className="font-semibold" >
                        {translate("frontend.sidebar.main")}
                    </SidebarGroupLabel>
                    <SidebarMenuButton className={buttonClassName("/")} onMouseDown={
                        () => {
                            startTransition(async () => {
                                startProgress()
                                router.push('/')
                                await new Promise(resolve => setTimeout(resolve, 50))
                            })
                        }
                    }>
                        <House /> {translate("frontend.sidebar.dashboard")}
                    </SidebarMenuButton>
                    <SidebarMenuButton className={buttonClassName("/visualization")} onMouseDown={
                        () => {
                            startTransition(async () => {
                                startProgress()
                                router.push('/visualization')
                                await new Promise(resolve => setTimeout(resolve, 50))
                            })
                        }
                    }>
                        <TvMinimal /> {translate("frontend.sidebar.visualization")}
                    </SidebarMenuButton>
                </SidebarGroup>
                <SidebarGroup>
                    <SidebarGroupLabel className="font-semibold">
                        {translate("frontend.sidebar.plugins")}
                    </SidebarGroupLabel>
                    <SidebarMenuButton className={buttonClassName("/plugins")} onMouseDown={
                        () => {
                            startTransition(async () => {
                                startProgress()
                                router.push('/plugins')
                                await new Promise(resolve => setTimeout(resolve, 50))
                            })
                        }
                    }>
                        <ChartNoAxesGantt /> {translate("frontend.sidebar.manager")}
                    </SidebarMenuButton>
                    <SidebarMenuButton className={buttonClassName("/performance")} onMouseDown={
                        () => {
                            toast.success("Coming soon!")
                        }
                    }>
                        <ChartArea /> {translate("frontend.sidebar.performance")}
                    </SidebarMenuButton>
                </SidebarGroup>
                <SidebarGroup>
                    <SidebarGroupLabel className="font-semibold">
                        {translate("frontend.sidebar.help")}
                    </SidebarGroupLabel>
                    <SidebarMenuButton className={buttonClassName("/wiki")} onMouseDown={
                        () => {
                            startTransition(async () => {
                                startProgress()
                                router.push('/wiki')
                                await new Promise(resolve => setTimeout(resolve, 50))
                            })
                        }
                    }>
                        <BookText /> {translate("frontend.sidebar.wiki")}
                    </SidebarMenuButton>
                    <SidebarMenuButton className={buttonClassName("/chat")} onMouseDown={
                        () => {
                            startTransition(async () => {
                                startProgress()
                                router.push('/chat')
                                await new Promise(resolve => setTimeout(resolve, 50))
                            })
                        }
                    }>
                        <MessageSquare /> {translate("frontend.sidebar.chat")}
                    </SidebarMenuButton>
                </SidebarGroup>
            </SidebarContent>
            <SidebarRail className="z-[999]" onMouseDown={() => {
                toggleSidebar()
            }} />
            <SidebarFooter className="bg-sidebarbg">
                <SidebarMenuButton className={buttonClassName("/settings")} onMouseDown={
                        () => {
                            startTransition(async () => {
                                startProgress()
                                router.push('/settings')
                                await new Promise(resolve => setTimeout(resolve, 50))
                            })
                        }
                    }>
                    <Bolt /> {translate("frontend.sidebar.settings")}
                </SidebarMenuButton>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <SidebarMenuButton className="w-full flex justify-between hover:shadow-md transition-all">
                                    <div className="flex items-center gap-2">
                                        <span>{translate("frontend.sidebar.anonymous")}</span>
                                    </div>
                                    <ChevronUp className="w-4 h-4 justify-self-end" />
                                </SidebarMenuButton>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent
                                side="top"
                                className="w-[--radix-popper-anchor-width] bg-transparent backdrop-blur-lg backdrop-brightness-75"
                            >
                                <DropdownMenuItem>
                                    <UserCog size={20} /> <span>{translate("frontend.sidebar.account")}</span>
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                    <UserRoundMinus /> <span>{translate("frontend.sidebar.sign_out")}</span>
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
  