"use client"

import { Card } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import Tiptap from "@/components/tiptap"
import { SendCrashReport } from "../server"
import { useState } from "react"
import { Editor } from "@tiptap/react"
import { toast } from "sonner"

export default function Home() {
    const [text, setText] = useState<string>("xd")

    const onUpdate = (editor: any) => {
        setText(editor.editor.getText());
    }

    const onSubmit = () => {
        toast.promise(SendCrashReport("Feedback", text, "Sent from 2.0 frontend"))
    }

    return (
        <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto w-full">
            <div className="flex flex-col justify-self-center h-full w-full justify-center items-center gap-2">
                <Label className="">Feedback</Label>
                <div className="w-[800px] h-80 border rounded-lg p-2">
                    <Tiptap className="w-full h-full text-start overflow-auto font-semibold" onUpdate={onUpdate} />
                </div>
                <Button className="w-[200px]" onClick={onSubmit}>Submit</Button>
            </div>
        </Card>
    )
}