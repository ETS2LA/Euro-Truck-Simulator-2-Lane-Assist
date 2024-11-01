import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"  

import { toast } from "sonner"
import useSWR, { mutate } from "swr"
import { GetPlugins, EnablePlugin, DisablePlugin } from "../backend"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { useRouter } from "next/router"
import { Menu, Check, X } from "lucide-react"
import {
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"
import { translate } from "../translation"
import { Separator } from "@/components/ui/separator"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import {
    DropdownMenu,
    DropdownMenuCheckboxItem,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Tooltip, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { TooltipContent } from "@radix-ui/react-tooltip"

export default function Home({ ip }: { ip: string }) {
    const { push } = useRouter()
    const [ search, setSearch ] = useState<string>("")
    const [ searchTags, setSearchTags ] = useState<string[]>([])
    const [ searchAuthors, setSearchAuthors ] = useState<string[]>([])
    const { data, error, isLoading } = useSWR("plugins", () => GetPlugins(ip), { refreshInterval: 1000 }) as any
    if (isLoading) return <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto"><p className="absolute left-5 font-semibold text-xs text-stone-400">{translate("loading")}</p></Card>
    if (error){
        toast.error(translate("frontend.menubar.error_fetching_plugins", ip), {description: error.message})
        return <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto"><p className="absolute left-5 font-semibold text-xs text-stone-400">{error.message}</p></Card>
    } 

    if (!data){
        return <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto"><p className="absolute left-5 font-semibold text-xs text-stone-400">{translate("frontend.menubar.error_fetching_plugins", ip)}</p></Card>
    }

    const tags:string[] = [];
    for (const key in data) {
        // Check if the key is a number
        if (isNaN(parseInt(key))){
            // @ts-ignore
            for(const tag in data[key].description.tags){
                console.log(tag)
                // @ts-ignore
                if(!tags.includes(data[key].description.tags[tag])){
                    // @ts-ignore
                    tags.push(data[key].description.tags[tag])
                }
            }
        }
    }

    const authors:string[] = [];
    for (const key in data) {
        // Check if the key is a number
        if (isNaN(parseInt(key))){
            // @ts-ignore
            for(const author in data[key].authors){
                // @ts-ignore
                if(!authors.includes(data[key].authors[author].name)){
                    // @ts-ignore
                    authors.push(data[key].authors[author].name)
                }
            }
        }
    }

    let hidden:number = 0;
    const enabled_plugins:string[] = [];
    const disabled_plugins:string[] = [];
    for (const key in data) {
        // Check if the key is a number
        if (isNaN(parseInt(key))){
            if(key == "Global" || key == "global_json")
                continue;

            // Search Text
            if(search != "" && !key.toLowerCase().includes(search.toLowerCase())){
                hidden++;
                continue;
            }

            // Search Tags
            if(searchTags.length > 0){
                let found = [];
                // @ts-ignore
                for(const tag in data[key].description.tags){
                    // @ts-ignore
                    if(searchTags.includes(data[key].description.tags[tag])){
                        found.push(data[key].description.tags[tag])
                    }
                }
                if(found.length != searchTags.length){
                    hidden++;
                    continue;
                }
            }

            // Search Authors
            if(searchAuthors.length > 0){
                let found = false;
                // @ts-ignore
                for(const author in data[key].authors){
                    // @ts-ignore
                    if(searchAuthors.includes(data[key].authors[author].name)){
                        found = true;
                    }
                }
                if(!found){
                    hidden++;
                    continue;
                }
            }

            if(data[key].enabled){
                enabled_plugins.push(key)
            }
            else{
                disabled_plugins.push(key)
            }
        }
    }

    return (
        <div className="h-full font-customSans">
            <div className="flex flex-col gap-2 p-5 pt-[13px]">
                <h2>{translate("frontend.menubar.plugins")}</h2>
                <Separator className="translate-y-4" />
            </div>
            <div className="h-full pt-0 p-1 max-h-[calc(100vh-132px)]">
                <TooltipProvider>
                    <ResizablePanelGroup direction="horizontal" className="text-center gap-6 pr-4 h-full">
                        <ResizablePanel defaultSize={20} className="flex flex-col gap-4 pl-4 pt-5 text-left">
                            {/* Search options */}
                            <Input placeholder={translate("search")} value={search} onChange={(e) => setSearch(e.target.value)} />
                            <div className="p-0 h-3"></div> {/* Makeshift separator */}
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="outline" className="flex text-left items-center justify-start">
                                        <p className={searchTags.length > 0 ? "font-normal" : "font-normal text-muted-foreground"}>
                                            {searchTags.length > 0 ? translate("frontend.plugins.selected_tags", searchTags.length) : translate("frontend.plugins.select_tags")}
                                        </p>
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent className="w-56">
                                    {tags.map((tag, index) => (
                                        <DropdownMenuCheckboxItem key={index} checked={searchTags.includes(tag)} onClick={() => {
                                            if(searchTags.includes(tag)){
                                                setSearchTags(searchTags.filter((t) => t != tag))
                                            }
                                            else{
                                                setSearchTags([...searchTags, tag])
                                            }
                                        }}>{tag}</DropdownMenuCheckboxItem>
                                    ))}
                                </DropdownMenuContent>
                            </DropdownMenu>

                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="outline" className="flex text-left items-center justify-start">
                                        <p className={searchAuthors.length > 0 ? "font-normal" : "font-normal text-muted-foreground"}>
                                            {searchAuthors.length > 0 ? translate("frontend.plugins.selected_authors", searchAuthors.length) : translate("frontend.plugins.select_authors")}
                                        </p>
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent className="w-56">
                                    {authors.map((author, index) => (
                                        <DropdownMenuCheckboxItem key={index} checked={searchAuthors.includes(author)} onClick={() => {
                                            if(searchAuthors.includes(author)){
                                                setSearchAuthors(searchAuthors.filter((t) => t != author))
                                            }
                                            else{
                                                setSearchAuthors([...searchAuthors, author])
                                            }
                                        }}>{author}</DropdownMenuCheckboxItem>
                                    ))}
                                </DropdownMenuContent>
                            </DropdownMenu>

                            {
                                search != "" || searchTags.length > 0 || searchAuthors.length > 0 ? (
                                    <Button variant="outline" onClick={() => {
                                        setSearch("")
                                        setSearchTags([])
                                        setSearchAuthors([])
                                    }} className="text-muted-foreground font-normal">{translate("clear")}</Button>
                                ) : null
                            }

                        </ResizablePanel>
                        <ResizablePanel defaultSize={80} className="h-full w-full relative pt-5">
                            {/* Plugin list */}

                            <div className="w-full border rounded-t-md h-10 grid grid-cols-8 items-center text-left pl-12">
                                <p className="text-muted-foreground text-sm col-span-2">{translate("frontend.plugins.name")}</p>
                                <p className="text-muted-foreground text-sm col-span-2">{translate("frontend.plugins.authors")}</p>
                                <p className="text-muted-foreground text-sm col-span-2">{translate("frontend.plugins.tags")}</p>
                            </div>
                            
                            {enabled_plugins.map((plugin:any, index) => (
                                <div key={index} className="w-full group relative border border-t-0 h-10 grid grid-cols-8 items-center text-left pl-12 cursor-pointer">
                                    <Checkbox checked={data[plugin].enabled} onClick={() => {
                                        if(data[plugin].enabled){
                                            toast.promise(
                                                DisablePlugin(plugin, ip), 
                                                {
                                                    loading: translate("frontend.command.disabling_plugin", translate(data[plugin].description.name)),
                                                    success: translate("frontend.command.disabled_plugin", translate(data[plugin].description.name)),
                                                    error: translate("frontend.command.error_disabling_plugin", translate(data[plugin].description.name)),
                                                }
                                            )
                                        }
                                        else{
                                            toast.promise(
                                                EnablePlugin(plugin, ip), 
                                                {
                                                    loading: translate("frontend.command.enabling_plugin", translate(data[plugin].description.name)),
                                                    success: translate("frontend.command.enabled_plugin", translate(data[plugin].description.name)),
                                                    error: translate("frontend.command.error_enabling_plugin", translate(data[plugin].description.name)),
                                                }
                                            )
                                        }
                                        setTimeout(() => {
                                            mutate("plugins")
                                        }, 200)
                                    }} className="absolute left-3.5" />
                                    <div className="flex col-span-2 gap-2 text-center items-center">
                                        <Tooltip delayDuration={100}>
                                            <TooltipTrigger className="col-span-2 text-start">
                                                <p className="text-sm text-muted-foreground group-hover:text-foreground">{translate(data[plugin].description.name)}</p>
                                            </TooltipTrigger>
                                            <TooltipContent>
                                                <div className="rounded-md max-w-72 bg-background p-4 border">
                                                    <p className="text-sm">{translate(data[plugin].description.description)}</p>
                                                </div>
                                            </TooltipContent>
                                        </Tooltip>
                                        <p className="text-xs text-muted-foreground pt-[2.5px]">
                                            {data[plugin].frametimes[data[plugin].frametimes.length - 1] ? 
                                                Math.round(1/data[plugin].frametimes[1])
                                            : "unknown"} fps
                                        </p>
                                    </div>
                                    <div className="text-sm col-span-2 flex gap-1">{
                                        // @ts-ignore
                                        data[plugin].authors.map((author, index) => (
                                            <div className="flex items-center text-left gap-1">
                                                <p className="text-xs">{index > 0 && index < data[plugin].authors.length ? "& " : ""}{author.name}</p>
                                            </div> 
                                        ))
                                    }</div>
                                    <div className="text-sm col-span-4">{
                                        // @ts-ignore
                                        data[plugin].description.tags.map((tag, index) => (
                                            <Badge variant={"outline"} key={index} className="mr-1 font-customSans font-normal h-7 cursor-pointer" onClick={() => {
                                                setSearchTags([...searchTags, tag])
                                            }}>{tag}</Badge>
                                        ))    
                                    }</div>
                                    <div className="absolute right-0 opacity-0 group-hover:opacity-100 transition-all">
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <Menu size={18} className="opacity-50 hover:opacity-80 mx-3" />
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent className="scale-90">
                                                { !data[plugin].enabled ?
                                                    <DropdownMenuItem onClick={() => {
                                                        toast.promise(
                                                            EnablePlugin(plugin, ip), 
                                                            {
                                                                loading: translate("frontend.command.enabling_plugin", translate(data[plugin].description.name)),
                                                                success: translate("frontend.command.enabled_plugin", translate(data[plugin].description.name)),
                                                                error: translate("frontend.command.error_enabling_plugin", translate(data[plugin].description.name)),
                                                            }
                                                        )
                                                        setTimeout(() => {
                                                            mutate("plugins")
                                                        }, 200)
                                                    }} className="gap-2"><Check size={20} />{translate("frontend.menubar.plugins.plugin.enable")}</DropdownMenuItem>
                                                :
                                                    <DropdownMenuItem onClick={() => {
                                                        toast.promise(
                                                            DisablePlugin(plugin, ip), 
                                                            {
                                                                loading: translate("frontend.command.disabling_plugin", translate(data[plugin].description.name)),
                                                                success: translate("frontend.command.disabled_plugin", translate(data[plugin].description.name)),
                                                                error: translate("frontend.command.error_disabling_plugin", translate(data[plugin].description.name)),
                                                            }
                                                        )
                                                        setTimeout(() => {
                                                            mutate("plugins")
                                                        }, 200)
                                                    }} className="gap-2"><X size={20} />{translate("frontend.menubar.plugins.plugin.disable")}</DropdownMenuItem>
                                                }
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </div>
                                </div>
                            ))}

                            {disabled_plugins.map((plugin:any, index) => (
                                <div key={index} className="w-full group relative border border-t-0 h-10 grid grid-cols-8 items-center text-left pl-12 cursor-pointer">
                                    <Checkbox checked={data[plugin].enabled} onClick={() => {
                                        if(data[plugin].enabled){
                                            toast.promise(
                                                DisablePlugin(plugin, ip), 
                                                {
                                                    loading: translate("frontend.command.disabling_plugin", translate(data[plugin].description.name)),
                                                    success: translate("frontend.command.disabled_plugin", translate(data[plugin].description.name)),
                                                    error: translate("frontend.command.error_disabling_plugin", translate(data[plugin].description.name)),
                                                }
                                            )
                                        }
                                        else{
                                            toast.promise(
                                                EnablePlugin(plugin, ip), 
                                                {
                                                    loading: translate("frontend.command.enabling_plugin", translate(data[plugin].description.name)),
                                                    success: translate("frontend.command.enabled_plugin", translate(data[plugin].description.name)),
                                                    error: translate("frontend.command.error_enabling_plugin", translate(data[plugin].description.name)),
                                                }
                                            )
                                        }
                                        setTimeout(() => {
                                            mutate("plugins")
                                        }, 200)
                                    }} className="absolute left-3.5 opacity-60 group-hover:opacity-100" />
                                    <Tooltip delayDuration={100}>
                                        <TooltipTrigger className="col-span-2 text-start">
                                            <p className="text-sm text-muted-foreground group-hover:text-foreground">{translate(data[plugin].description.name)}</p>
                                        </TooltipTrigger>
                                        <TooltipContent>
                                            <div className="rounded-md max-w-72 bg-background p-4 border">
                                                <p className="text-sm">{translate(data[plugin].description.description)}</p>
                                            </div>
                                        </TooltipContent>
                                    </Tooltip>
                                    <div className="text-sm col-span-2 flex gap-1">{
                                        // @ts-ignore
                                        data[plugin].authors.map((author, index) => (
                                            <div className="flex items-center text-left gap-1">
                                                <p className="text-xs text-muted-foreground group-hover:text-foreground">{index > 0 && index < data[plugin].authors.length ? "& " : ""}{author.name}</p>
                                            </div> 
                                        ))
                                    }</div>
                                    <div className="text-sm col-span-4">{
                                        // @ts-ignore
                                        data[plugin].description.tags.map((tag, index) => (
                                            <Badge variant={"outline"} key={index} className="mr-1 font-customSans font-normal h-7 cursor-pointer opacity-60 group-hover:opacity-100" onClick={() => {
                                                setSearchTags([...searchTags, tag])
                                            }}>{tag}</Badge>
                                        ))    
                                    }</div>
                                    <div className="absolute right-0 opacity-0 group-hover:opacity-100 transition-all">
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <Menu size={18} className="opacity-50 hover:opacity-80 mx-3" />
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent className="scale-90">
                                                { !data[plugin].enabled ?
                                                    <DropdownMenuItem onClick={() => {
                                                        toast.promise(
                                                            EnablePlugin(plugin, ip), 
                                                            {
                                                                loading: translate("frontend.command.enabling_plugin", translate(data[plugin].description.name)),
                                                                success: translate("frontend.command.enabled_plugin", translate(data[plugin].description.name)),
                                                                error: translate("frontend.command.error_enabling_plugin", translate(data[plugin].description.name)),
                                                            }
                                                        )
                                                        setTimeout(() => {
                                                            mutate("plugins")
                                                        }, 200)
                                                    }} className="gap-2"><Check size={20} />{translate("frontend.menubar.plugins.plugin.enable")}</DropdownMenuItem>
                                                :
                                                    <DropdownMenuItem onClick={() => {
                                                        toast.promise(
                                                            DisablePlugin(plugin, ip), 
                                                            {
                                                                loading: translate("frontend.command.disabling_plugin", translate(data[plugin].description.name)),
                                                                success: translate("frontend.command.disabled_plugin", translate(data[plugin].description.name)),
                                                                error: translate("frontend.command.error_disabling_plugin", translate(data[plugin].description.name)),
                                                            }
                                                        )
                                                        setTimeout(() => {
                                                            mutate("plugins")
                                                        }, 200)
                                                    }} className="gap-2"><X size={20} />{translate("frontend.menubar.plugins.plugin.disable")}</DropdownMenuItem>
                                                }
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </div>
                                </div>
                            ))}

                            <div className="w-full border border-t-0 rounded-b-md h-10 items-center flex pl-4">
                                {hidden > 0 ? <p className="text-muted-foreground text-xs">{translate("frontend.plugins.hidden", hidden)}</p> : <p className="text-muted-foreground text-xs">{translate("frontend.plugins.end_list")}</p>}
                            </div>
                        </ResizablePanel>
                    </ResizablePanelGroup>

                </TooltipProvider>
            </div>
        </div>
    )
}