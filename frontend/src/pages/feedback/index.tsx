import { Card } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import Tiptap from "@/components/tiptap"
import { SendCrashReport } from "../server"

export default function Home() {
    return (
        <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto w-full">
            <div className="flex flex-col justify-self-center h-full w-full justify-center items-center gap-2">
                <Label className="">Feedback</Label>
                <div className="w-[800px] h-80 border rounded-lg p-2">
                    <Tiptap className="w-full h-full text-start overflow-auto font-semibold" />
                </div>
                <Button className="w-[200px]">Submit</Button>
            </div>
        </Card>
    )
}