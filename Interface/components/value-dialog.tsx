"use client"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import useSWR, { mutate } from "swr"
import { GetPlugins, PluginFunctionCall } from "@/apis/backend"
import { Separator } from "./ui/separator"
import { Input } from "./ui/input"
import { GetSettingsJSON, SetSettingByKey, SetSettingByKeys } from "@/apis/settings"
import { DisablePlugin, EnablePlugin } from "@/apis/backend"
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select"
import { Toggle } from "@/components/ui/toggle"
import { Switch } from "./ui/switch"
import { Button } from "./ui/button"
import { toast } from "sonner"
import { useEffect } from "react"
import { Slider } from "./ui/slider"
import { useState } from "react"
import { translate } from "@/apis/translation"
import React, { Component } from 'react';
import { SkeletonItem } from "./skeleton_item"
import {
	Check,
	X
} from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "./ui/progress"

export default function ValueDialog({onClose, open, json}: {onClose: any, open: boolean, json: string}) {
    const [returnValue, setReturnValue] = useState({})
    
	if (!json) return <div />

    const TitleRenderer = (data:string) => {
		return <h3 className="font-medium">{translate(data)}</h3>
	}

	const DescriptionRenderer = (data:string) => {
		return <p className="text-sm text-muted-foreground">{translate(data)}</p>
	}

	const LabelRenderer = (data:string) => {
		return <p>{translate(data)}</p>
	}

	const SeparatorRenderer = () => {
		return <>
			<Separator />
		</>
	}

	const SpaceRenderer = (data:number) => {
		if (data) {
			return <div>
				{Array(data).fill(0).map((_, index) => (
					<div key={index} className="h-1"></div>
				))}
			</div>
		}
		return <div className="h-4"></div>
	}

	const InputRenderer = (data:any) => {
        // @ts-ignore
        const placeholder = returnValue[data.key] || data.options.default || ""
		if (data.options.type == "string") {
			return <div className="flex flex-col gap-2 w-full">
				<h4>{translate(data.name)}</h4>
				<Input type="text" placeholder={placeholder} onChange={(e) => {
                    // @ts-ignore
                    setReturnValue(prevState => ({
                        ...prevState,
                        [data.key]: e.target.value,
                    }))
                }} />
				<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
			</div>
		}

		if (data.options.type == "number") {
            const value = data.options.default || 0
			return (
				<div className="flex flex-col gap-2 w-full">
					<h4>{translate(data.name)}</h4>	
					<Input type="number" placeholder={value} className="font-customMono" onChange={(e) => {
                        // @ts-ignore
                        setReturnValue(prevState => ({
                            ...prevState,
                            [data.key]: e.target.value,
                        }))
					}} />
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
			)
		}
	}

	const SliderRenderer = (data:any) => {
        // @ts-ignore
        const value = returnValue[data.key] || data.options.default || 0
		return ( // Add return statement here
			<div className="flex flex-col gap-2">
                <h4>{translate(data.name)}  —  {value}{data.options.suffix}{value}</h4>
                <Slider min={data.options.min} max={data.options.max} defaultValue={[value]} step={data.options.step} onValueChange={(value) => {
                    // @ts-ignore
                    setReturnValue(prevState => ({
                        ...prevState,
                        [data.key]: value,
                    }))
                }} />
                <p className="text-xs text-muted-foreground">{translate(data.description)}</p>
            </div>
		);
	}

	const SwitchRenderer = (data:any) => {
        // @ts-ignore
        const placeholder = returnValue[data.key] || data.options.default || false
		return <div className={"flex justify-between p-0 items-center" + GetBorderClassname(data.options.border)}>
				<div className="flex flex-col gap-1 pr-12">
					<h4 className="font-semibold">{translate(data.name)}</h4>
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
				<Switch checked={placeholder} onCheckedChange={(bool) => {
                    // @ts-ignore
                    setReturnValue(prevState => ({
                        ...prevState,
                        [data.key]: bool,
                    }))
				}} />
			</div>
	}

	const SelectorRenderer = (data:any) => {
        // @ts-ignore
		const placeholder = returnValue[data.key] || data.options.default || ""
		return <div className="flex flex-col gap-2">
					<h4>{translate(data.name)}</h4>
					<Select defaultValue={placeholder} onValueChange={(value) => {
                        // @ts-ignore
                        setReturnValue(prevState => ({
                            ...prevState,
                            [data.key]: value,
                        }))
					}} >
						<SelectTrigger>
							<SelectValue placeholder={placeholder}>{placeholder}</SelectValue>
						</SelectTrigger>
						<SelectContent>
							{data.options.options.map((value:any) => (
								<SelectItem key={value} value={value}>{value}</SelectItem>
							))}
						</SelectContent>
					</Select>
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
	}

	const ToggleRenderer = (data:any) => {
        // @ts-ignore
        const placeholder = returnValue[data.key] || data.options.default || false
		return <div className="flex gap-4 w-full items-center">
				<Toggle pressed={placeholder} onPressedChange={(bool) => {
                    // @ts-ignore
                    setReturnValue(prevState => ({
                        ...prevState,
                        [data.key]: bool,
                    }))
				}} className="w-8 h-8 p-[7px] data-[state=on]:bg-background data-[state=on]:hover:bg-white/10 " variant={"outline"}>
					{placeholder ? <Check /> : <X />}
				</Toggle>
				{data.options.separator && <Separator orientation="vertical" />}
				<div>
					<h4>{translate(data.name)}</h4>
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
			</div>
	}

	const ButtonRenderer = (data:any) => {
        if(data.options.target != "submit"){
            return DescriptionRenderer(translate("frontend.dialog.not_supported", "Button.target"))
        }
        if(data.title != ""){
            return <div className={"flex justify-between p-4 items-center" + GetBorderClassname(data.options.border)}>
                    <div className="flex flex-col gap-1 pr-12">
                        <h4 className="font-semibold">{translate(data.title)}</h4>
                        <p className="text-xs text-muted-foreground">{translate(data.description)}</p>
                    </div>
                    <Button variant={"outline"} className="min-w-32" onClick={() => {
                        onClose(returnValue)
                    }}>{translate(data.text)}</Button>
                </div>
        }
        else{
            return <div className={"flex justify-between items-center" + GetBorderClassname(data.options.border)}>
                    <Button variant={"outline"} className="w-full" onClick={() => {
                        onClose(returnValue)
                    }}>{translate(data.text)}</Button>
                </div>
        }
	}

	const ProgressBarRenderer = (data:any) => {
		const value = data.value;
		const min = data.min;
		const max = data.max;
		const progress = (value - min) / (max - min) * 100;
		return <div className="flex flex-col gap-2 w-full">
			<Progress value={progress} />
			<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
		</div>
	}

	const GetBorderClassname = (border:boolean) => {
		if(border){
			return " p-4 border rounded-md"
		}
		return "p-4"
	}

    // @ts-ignore
	const PageRenderer = (data: any) => {
		if (!Array.isArray(data)) {
			data = [data]
		}
		const result = [];
		for (const item of data) {
			const key = Object.keys(item)[0];
			const key_data = item[key];

			if (key == "enabled_lock") {
				result.push(DescriptionRenderer(translate("frontend.dialog.not_supported", "EnabledLock")))
			}

			// Page looks
			if(key == "title"){
				result.push(TitleRenderer(key_data.text))
			}
			if(key == "description"){
				result.push(DescriptionRenderer(key_data.text))
			}
			if (key == "label") {
				result.push(LabelRenderer(key_data.text))
			}
			if (key == "separator") {
				result.push(SeparatorRenderer())
			}
			if (key == "space") {
				result.push(SpaceRenderer(key_data.amount))
			}
			if (key == "group") {
				const direction = key_data.direction
				if(direction == "horizontal"){
					result.push(<div className={"flex gap-4 w-full rounded-md" + GetBorderClassname(key_data.border)}>
						{PageRenderer(key_data.components)}
					</div>)
				}
				else{
					result.push(<div className={"flex flex-col gap-4 w-full rounded-md" + GetBorderClassname(key_data.border)}>
						{PageRenderer(key_data.components)}
					</div>)
				}
			}
            if (key == "form") {
                result.push(PageRenderer(key_data.components))
            }
			if (key == "tabview") {
				result.push(<Tabs className="w-full" defaultValue={key_data.components[0].tab.name}>
					<TabsList className="w-full bg-transparent border">
						{key_data.components.map((tab:any, index:number) => (
							<TabsTrigger key={index} value={tab.tab.name}>{translate(tab.tab.name)}</TabsTrigger>
						))}
					</TabsList>
					{key_data.components.map((tab:any, index:number) => (
						<TabsContent key={index} value={tab.tab.name} className="w-full rounded-md p-2 flex gap-6 flex-col">
							{PageRenderer(tab)}
						</TabsContent>
					))}
				</Tabs>)
			}
			if (key == "tab"){
				result.push(PageRenderer(key_data.components))
			}

			// Live Data
			if (key == "progress_bar") {
				result.push(ProgressBarRenderer(key_data))
			}

			// Functions
			if (key == "button") {
				result.push(ButtonRenderer(key_data))
			}

			// Options
			if (key == "input") {
				result.push(InputRenderer(key_data))
			}
			if (key == "slider") {
				result.push(SliderRenderer(key_data))
			}
			if (key == "switch") {
				result.push(SwitchRenderer(key_data))
			}
			if (key == "toggle") {
				result.push(ToggleRenderer(key_data))
			}
			if (key == "selector") {
				result.push(SelectorRenderer(key_data))
			}
		};

		return result;
	};

    return <Dialog open={open}>
            <DialogTrigger className="absolute">
                <div>

                </div>
            </DialogTrigger>
            <DialogContent>
                <div className="flex flex-col gap-2 font-geist">
                    {PageRenderer(json)}
                </div>
            </DialogContent>
        </Dialog>
}