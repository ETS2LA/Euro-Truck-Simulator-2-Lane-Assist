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
                        Disclaimer!
                    </DialogTitle>
                </DialogHeader>
                <DialogDescription className='flex flex-col gap-2'>
                    <p>ETS2LA is not responsible for any ill effects caused by using any of the features provided by this software. Please use the software at your own risk.</p>
                    <p>Using ETS2LA in TruckersMP has been <span className='font-bold'>allowed by TMP staff</span> but you are responsible for any bans or warnings caused by using this software.</p>
                    <br />
                    <div className='flex flex-col gap-0 relative group'>
                        <Button variant={"outline"} className='text-foreground z-10 hover:font-semibold bg-background border-none disabled:opacity-100 disabled:text-muted-foreground' onClick={onClose} disabled={!buttonEnabled}>I understand</Button>
                        <Progress className='w-[calc(100%+2px)] rounded-lg h-[38px] my-[-1px] mx-[-1px] absolute bg-accent/20' value={progress} max={100} sliderClassname='bg-accent' onSubmit={onClose} />
                    </div>
                </DialogDescription>
            </DialogContent>
        </Dialog>
}