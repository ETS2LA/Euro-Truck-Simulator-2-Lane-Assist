import { ScrollArea } from "./ui/scroll-area"
import { Separator } from "./ui/separator"
import useSWR from "swr"
import { SkeletonCard } from "./skeleton_card"
import { GetGitHistory } from "@/pages/server"
import { Accordion } from "./ui/accordion"
import { AccordionContent, AccordionItem, AccordionTrigger } from "./ui/accordion"

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

    return (
        <ScrollArea className="h-full pt-3 text-end">
            <h4 className="pb-3 pl-3 font-medium flex gap-1">Commit History</h4>
            <Separator />
            <Accordion type="single" collapsible>
                {commits.map((commit: any, index: number) => {
                    return (
                        <AccordionItem value={commit}>
                            <AccordionTrigger className="pl-3 pr-2">
                            <p className="flex gap-3"><p className="text-stone-600">{index+1}. </p> {commit.author}</p>
                            </AccordionTrigger>
                            <AccordionContent>
                                <div className="text-sm text-gray-500 text-center">{commit.message}</div>
                            </AccordionContent>
                        </AccordionItem>
                    )
                })}
            </Accordion>
            <p className="text-xs text-gray-500 text-center pt-2 pb-2">Showing only the latest 100 commits</p>
        </ScrollArea>
    )
}