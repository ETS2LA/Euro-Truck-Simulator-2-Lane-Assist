import PluginList from "@/components/plugin_list"
import { Card } from "@/components/ui/card"
import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"
import VersionHistory from "@/components/version_history"
import {
    ContextMenu,
    ContextMenuCheckboxItem,
    ContextMenuContent,
    ContextMenuItem,
    ContextMenuLabel,
    ContextMenuRadioGroup,
    ContextMenuRadioItem,
    ContextMenuSeparator,
    ContextMenuShortcut,
    ContextMenuSub,
    ContextMenuSubContent,
    ContextMenuSubTrigger,
    ContextMenuTrigger,
} from "@/components/ui/context-menu"
import { toast } from "sonner"
import { useRouter } from "next/router"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { translate } from "./translation"
import { Separator } from "@/components/ui/separator"
import { GetUserData } from "./account"
import useSWR from "swr"  


export default function Home({ip} : {ip: string}) {
    const push = useRouter().push;
    const [userData, setUserData] = useState(null);

    GetUserData().then((data) => {
        setUserData(data);
    })

    return (
        <div className="w-full h-[calc(100vh-72px)]">
            <ResizablePanelGroup direction="horizontal" className="overflow-auto text-center gap-1.5">
                <ResizablePanel defaultSize={80} className="content-center rounded-md">
                    <ResizablePanelGroup direction="vertical" className="overflow-auto text-center gap-1.5">
                        <ResizablePanel defaultSize={10} className="flex flex-col justify-center text-left">
                            <h2 className="font-customSans pl-3">{translate("frontend.hello", userData ? userData["username"] : "loading...")}</h2>
                        </ResizablePanel> 
                        <ResizablePanel defaultSize={90}>
                            <ResizablePanelGroup direction="horizontal" className="overflow-auto text-center gap-1.5">
                                <ResizablePanel defaultSize={30} className="flex flex-col text-left gap-[18px] opacity-50 hover:opacity-100 transition-all">
                                    <p className="text-xs text-muted-foreground pl-3">Check out these updates from our developers!</p>
                                    <div className="border rounded-lg h-[calc(100%-34px)]">
                                        <VersionHistory ip={ip} />
                                    </div>
                                </ResizablePanel>
                                <div />
                                <ResizablePanel defaultSize={70} className="flex flex-col text-left gap-[18px] opacity-50 hover:opacity-100 transition-all">
                                    <p className="text-xs text-muted-foreground pl-3">Here are some of your stats!</p>
                                    <div className="border border-dashed rounded-lg h-[calc(100%-34px)]">

                                    </div>
                                </ResizablePanel>
                            </ResizablePanelGroup>
                        </ResizablePanel>
                    </ResizablePanelGroup>
                </ResizablePanel>
                <div />
                <ResizablePanel defaultSize={20}>
                    <ResizablePanelGroup direction="vertical" className="overflow-auto text-center gap-1.5">
                        <ResizablePanel defaultSize={10} className="flex flex-col justify-center text-left opacity-50 hover:opacity-100 transition-all">
                            
                        </ResizablePanel> 
                        <ResizablePanel defaultSize={90}>
                            <ResizablePanelGroup direction="vertical" className="overflow-auto text-center gap-3">
                                <ResizablePanel defaultSize={75} className="flex flex-col text-left gap-[18px] opacity-50 hover:opacity-100 transition-all">
                                    <p className="text-xs text-muted-foreground pl-3">Manage your plugins here.</p>
                                    <div className="border rounded-lg h-[calc(100%-34px)]">
                                        <PluginList ip={ip} />
                                    </div>
                                </ResizablePanel>
                                <ResizablePanel defaultSize={25} className="opacity-50 hover:opacity-100 transition-all">
                                    <div className="border rounded-lg h-full flex flex-col gap-3 justify-center items-center">
                                        <Button onClick={() => push("/basic")} variant={"outline"} className="w-48">{translate("frontend.mainmenu.basic_mode")}</Button>
                                        <Button onClick={() => open("http://localhost:60407/ETS2LA Visualisation.html", "_blank")} variant={"outline"} className="w-48">{translate("frontend.mainmenu.open_in_browser")}</Button>
                                    </div>
                                </ResizablePanel>
                            </ResizablePanelGroup>
                        </ResizablePanel>
                    </ResizablePanelGroup>
                </ResizablePanel>
            </ResizablePanelGroup>
        </div>
    )
}