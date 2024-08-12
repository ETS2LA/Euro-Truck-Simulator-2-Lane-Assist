"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Tiptap from "@/components/tiptap"
import { SendCrashReport } from "../server"
import { useState } from "react"
import { toast } from "sonner"
import { translate } from "../translation"

export default function Home() {
    const [text, setText] = useState<string>("")

    const onUpdate = (editor: any) => {
        setText(editor.editor.getText());
    }

    const onSubmit = () => {
        if (text === "" || text === " ") {
            toast.error(translate("frontend.feedback.empty"))
            return
        }
        toast.promise(SendCrashReport("Feedback", text, "Sent from 2.0 frontend"), {
            loading: translate("frontend.feedback.sending"),
            success: translate("frontend.feedback.sent"),
            error: translate("frontend.feedback.error_sending"),
        })
    }

    return (
        <Card className="flex flex-col content-center text-center h-[calc(100vh-72px)] overflow-auto">
            <div className="flex flex-col justify-self-center h-full w-full justify-center items-center gap-2">
                <div className="w-[800px]">
                    <h3>{translate("frontend.feedback")}</h3>
                    <p className="text-zinc-600">{translate("frontend.feedback.description")}</p>
                    <p className="text-zinc-600">{translate("frontend.feedback.disclaimer")}</p>
                </div>
                <div className="w-[800px] h-80 border rounded-lg p-2">
                    <Tiptap className="w-full h-full text-start overflow-auto font-semibold" onUpdate={onUpdate} />
                </div>
                <Button className="w-[800px] mt-2" onClick={onSubmit}>{translate("frontend.feedback.submit")}</Button>
            </div>
        </Card>
    )
}