import { ScrollArea } from "./ui/scroll-area"
import { Separator } from "./ui/separator"
import useSWR from "swr"
import { SkeletonCard } from "./skeleton_card"
import { GetGitHistory } from "@/pages/server"
import { Accordion } from "./ui/accordion"
import { AccordionContent, AccordionItem, AccordionTrigger } from "./ui/accordion"
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar"

export default function VersionHistory({ip}: {ip: string}) {
    const { data, isLoading, error } = useSWR("api/git/history", () => GetGitHistory(ip))
    if (isLoading) return <SkeletonCard />
    if (error) return <p className="text-red-500">Error fetching git history</p>
    if (!data) return <div>
            <p className="text-red-500">No git history found... data: </p>
            <p>{data}</p>
        </div>

    // Limit data to the first 100 commits
    let commits = data.slice(0, 100);    

    const getImage = (url: string) => {
        return url
    }

    return (
        <ScrollArea className="h-full pt-3 text-end">
            <h4 className="pb-3 pl-3 font-medium flex gap-1">Commit History <p className="text-xs text-stone-600">(updates)</p></h4>
            <Separator />
            <Accordion type="single" collapsible>
                {commits.map((commit: any, index: number) => {
                    return (
                        <AccordionItem value={commit}>
                            <AccordionTrigger className="pl-3 pr-2">
                            <Avatar>
                                <AvatarImage src={getImage(commit.picture)}/>
                                <AvatarFallback>Avatar</AvatarFallback>
                            </Avatar>
                            <p className="flex gap-3"><p className="text-stone-600">{index+1}. </p> {commit.author}</p>
                            </AccordionTrigger>
                            <AccordionContent className="gap-y-2 flex flex-col">
                                <div className="text-sm text-stone-500 text-start pl-3 pr-2">{commit.message}</div>
                                <div className="text-xs text-stone-500 text-start pl-3 pr-2">on {new Date(commit.time * 1000).toLocaleDateString()} - {new Date(commit.time * 1000).toTimeString().split(" ")[0]}</div>
                            </AccordionContent>
                        </AccordionItem>
                    )
                })}
            </Accordion>
            <p className="text-xs text-gray-500 text-center pt-2 pb-2">Showing only the latest 100 commits</p>
        </ScrollArea>
    )
}