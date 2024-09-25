"use client"
import { useEditor, EditorContent } from '@tiptap/react'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from './ui/button'
import { useState, useEffect, use } from 'react'
import { Progress } from './ui/progress'
import { translate } from '@/pages/translation'

export default function DisclaimerDialog({onClose, open}: {onClose: any, open: boolean}) {
    const [startTime, setStartTime] = useState(Date.now())
    const [buttonEnabled, setButtonEnabled] = useState(false);
    const [progress, setProgress] = useState(0);
    const waitTime = 5000;

    useEffect(() => {
        setStartTime(Date.now());
        setProgress(0);
    }, [])

    useEffect(() => {
        let interval = setInterval(() => {
            if (progress < 100) {
                setProgress(Date.now() - startTime > waitTime ? 100 : progress + 100 / (waitTime / 500));
                console.log(progress)
            } else {
                setProgress(100);
                clearInterval(interval);
                setButtonEnabled(true);
            }
        }, 500);
        return () => {
            clearInterval(interval);
        }
    }, [progress, startTime])

    return <Dialog open={open}>
            <DialogTrigger className="absolute">
                <div>

                </div>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>
                        {translate("frontend.disclaimer.title")}
                    </DialogTitle>
                </DialogHeader>
                <DialogDescription className='flex flex-col gap-2'>
                    <p>{translate("frontend.disclaimer.description.line1")}</p>
                    <p>{translate("frontend.disclaimer.description.line2")}</p>
                    <br />
                    <div className='flex flex-col gap-0 relative group'>
                        <Button variant={"outline"} className='text-foreground z-10 hover:font-semibold bg-background border-none disabled:opacity-100 disabled:text-muted-foreground' onClick={onClose} disabled={!buttonEnabled}>{translate("frontend.disclaimer.ok")}</Button>
                        <Progress className='w-[calc(100%+2px)] rounded-lg h-[38px] my-[-1px] mx-[-1px] absolute bg-accent/20' value={progress} max={100} sliderClassname='bg-accent' onSubmit={onClose} />
                    </div>
                </DialogDescription>
            </DialogContent>
        </Dialog>
}