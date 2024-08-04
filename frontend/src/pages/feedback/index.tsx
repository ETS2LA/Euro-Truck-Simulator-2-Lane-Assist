"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Tiptap from "@/components/tiptap"
import { SendCrashReport } from "../server"
import { useState } from "react"
import { toast } from "sonner"

export default function Home() {
    const [text, setText] = useState<string>("")

    const onUpdate = (editor: any) => {
        setText(editor.editor.getText());
    }

    const onSubmit = () => {
        if (text === "" || text === " ") {
            toast.error("Feedback is empty, please provide any feedback you have.")
            return
        }
        toast.promise(SendCrashReport("Feedback", text, "Sent from 2.0 frontend"), {
            loading: "Sending feedback...",
            success: "Feedback sent!",
            error: "there was an error sending the feedback, try again later.",
        })
    }

    return (
        <Card className="flex flex-col content-center text-center h-[calc(100vh-72px)] overflow-auto">
            <div className="flex flex-col justify-self-center h-full w-full justify-center items-center gap-2">
                <div className="w-[800px]">
                    <h3>Feedback</h3>
                    <p className="text-zinc-600">Please provide any feedback you have. This will be send directly to a private channel for developers to see.</p>
                    <p className="text-zinc-600">Do not share any personal information.</p>
                </div>
                <div className="w-[800px] h-80 border rounded-lg p-2">
                    <Tiptap className="w-full h-full text-start overflow-auto font-semibold" onUpdate={onUpdate} />
                </div>
                <Button className="w-[800px] mt-2" onClick={onSubmit}>Submit</Button>
            </div>
        </Card>
    )
}