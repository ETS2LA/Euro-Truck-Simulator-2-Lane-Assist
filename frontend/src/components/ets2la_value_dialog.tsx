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
import { Input } from "./ui/input"
import { Switch } from './ui/switch'
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select"

export default function ValueDialog({onClose, open, title, json}: {onClose: any, open: boolean, title: string, json: string}) {
    if (!json) return <div />

    const [returnValue, setReturnValue] = useState(null)

    const SettingsRenderer = (data:any) => {
        // string, number, boolean, array, object, enum
        if (data.type.type == "string") {
            return <div className="flex flex-col gap-2">
                <h4>{translate(data.name)}</h4>
                <Input type="text" placeholder={data.type.default ? data.type.default : "Text"} onChange={(e) => {
                    setReturnValue(e.target.value)
                }} />
                <p className="text-xs text-muted-foreground">{translate(data.description)}</p>
            </div>
        }
        if (data.type.type == "number") {
            return (
                <div className="flex flex-col gap-2">
                    <h4>{translate(data.name)}</h4>	
                    <Input type="number" placeholder={data.type.default ? data.type.default : 0} className="font-customMono" onChange={(e) => {
                        setReturnValue(parseFloat(e.target.value))
                    }} />
                    <p className="text-xs text-muted-foreground">{translate(data.description)}</p>
                </div>
            )
        }
        if (data.type.type == "boolean") {
            return <div className="flex justify-between rounded-md border p-4 items-center">
                <div className="flex flex-col gap-1 pr-12">
                    <h4 className="font-semibold">{translate(data.name)}</h4>
                    <p className="text-xs text-muted-foreground">{translate(data.description)}</p>
                </div>
                <Switch checked={data.type.default ? data.type.default : false} onCheckedChange={(bool) => {
                    setReturnValue(bool)
                }} />
            </div>
        }
        if (data.type.type == "enum") {
            if (!data.type.options) {
                return <p className="text-xs text-muted-foreground">{translate("frontend.settings.enum.no_enum")}</p>
            }
            return <div className="flex flex-col gap-2">
                <h4>{translate(data.name)}</h4>
                <Select defaultValue={data.type.default ? data.type.default : ""} onValueChange={(value) => {
                    setReturnValue(value)
                }} >
                    <SelectTrigger>
                        <SelectValue placeholder={data.type.default ? data.type.default : ""}>{data.type.default ? data.type.default : ""}</SelectValue>
                    </SelectTrigger>
                    <SelectContent>
                        {data.type.options.map((value:any) => (
                            <SelectItem key={value} value={value}>{value}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">{translate(data.description)}</p>
            </div>
        }
        return <p className="text-xs text-muted-foreground">{translate("frontend.settings.unknown_data_type", data.type.type)}</p>
    }

    return <Dialog open={open}>
            <DialogTrigger className="absolute">
                <div>

                </div>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>
                        {title}
                    </DialogTitle>
                </DialogHeader>
                <div className="flex flex-col gap-2">
                    {SettingsRenderer(json[0])}
                    <br />
                    <Button variant={"outline"} className='text-foreground z-10 hover:font-semibold bg-background disabled:opacity-100 disabled:text-muted-foreground' onClick={() => {
                        onClose(returnValue)
                    }}>Confirm</Button>
                </div>
            </DialogContent>
        </Dialog>
}