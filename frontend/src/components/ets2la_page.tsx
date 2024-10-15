import { Skeleton } from "@/components/ui/skeleton"
import useSWR, { mutate } from "swr"
import { GetPlugins } from "@/pages/backend"
import { Separator } from "./ui/separator"
import { set } from "date-fns"
import { Input } from "./ui/input"
import { GetSettingsJSON, SetSettingByKey, SetSettingByKeys } from "@/pages/settingsServer"
import { DisablePlugin, EnablePlugin } from "@/pages/backend"
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select"
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@/components/ui/tooltip"
import { Toggle } from "@/components/ui/toggle"
import { Switch } from "./ui/switch"
import { Button } from "./ui/button"
import { toast } from "sonner"
import { useEffect } from "react"
import { Slider } from "./ui/slider"
import { useState } from "react"
import { translate } from "@/pages/translation"
import React, { Component } from 'react';
import { SkeletonItem } from "./skeleton_item"
import {
	Check,
	X
} from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface SliderComponentProps {
    pluginSettings: Record<string, any>;
    data: {
        key: string;
        name: string;
        description: string;
		requires_restart?: boolean;
		type: string;
        options: {
            min: number;
            max: number;
            step?: number;
            suffix?: string;
        };
    };
    plugin: string;
    ip: string;
    setNeedsRestart: (needsRestart: boolean) => void;
    mutate: (key: string) => void;
    translate: (key: string) => string;
}

interface SliderComponentState {
    curSliderValue: number;
    tempSliderValue: number | null;
}

class SliderComponent extends Component<SliderComponentProps, SliderComponentState> {
    constructor(props: SliderComponentProps) {
        super(props);
        const value = props.pluginSettings[props.data.key] ? parseFloat(props.pluginSettings[props.data.key]) : 0;
        this.state = {
            curSliderValue: value,
            tempSliderValue: null
        };
    }

    handleValueChange = (value: number[]) => {
        this.setState({ tempSliderValue: value[0] });
    }

    handleValueCommit = (value: number[]) => {
        const { plugin, data, ip, setNeedsRestart, mutate, translate } = this.props;
        SetSettingByKey(plugin, data.key, value[0], ip).then(() => {
            if (data.requires_restart)
                setNeedsRestart(true);
            mutate("settings");
            toast.success(translate("frontend.settings.number.updated"), {
                duration: 500
            });
            this.setState({ curSliderValue: value[0], tempSliderValue: null });
        });
    }

    render() {
        const { data, translate, pluginSettings } = this.props;
        const { curSliderValue, tempSliderValue } = this.state;
        const value = pluginSettings[data.key] ? parseFloat(pluginSettings[data.key]) : 0;
        const step = data.options.step || 1;
        const suffix = data.options.suffix || "";

        return (
            <div className="flex flex-col gap-2">
                <h4>{translate(data.name)}  —  {value}{suffix}{tempSliderValue !== null ? tempSliderValue != value ? ` → ${tempSliderValue}${suffix}` : `` : ``}</h4>
                <Slider min={data.options.min} max={data.options.max} defaultValue={[value]} step={step} onValueChange={this.handleValueChange} onValueCommit={this.handleValueCommit} />
                <p className="text-xs text-muted-foreground">{translate(data.description)}</p>
            </div>
        );
    }
}

export function ETS2LAPage({ ip, data, plugin }: { ip: string, data: any, plugin: string }) {
	const { data: pluginSettings, error: pluginSettingsError, isLoading: pluginSettingsLoading } = useSWR("settings", () => GetSettingsJSON(plugin, ip))
	const [needsRestart, setNeedsRestart] = useState(false)

	// Update the settings when the plugin changes
	useEffect(() => {
		setNeedsRestart(false)
		mutate("settings")
	}, [plugin])

	if (pluginSettingsLoading) {
		return <Skeleton />
	}

	if (pluginSettingsError) {
		return <p className="text-xs text-muted-foreground">{translate("frontend.settings.error", pluginSettingsError)}</p>
	}

	if (!data || !pluginSettings) {
		return <p className="text-xs text-muted-foreground">{translate("frontend.settings.backend_no_data")}</p>
	}

	const settings = data

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
		if(pluginSettings[data.key] == undefined){
			if(data.options.default != undefined){
				console.log("Setting default value for", data.key)
				pluginSettings[data.key] = data.options.default
			}
			else{
				pluginSettings[data.key] = data.options.type
			}
		}

		if (data.options.type == "string") {
			return <div className="flex flex-col gap-2 w-full">
				<h4>{translate(data.name)}</h4>
				<Input type="text" placeholder={pluginSettings[data.key]} onChange={(e) => {
					SetSettingByKey(plugin, data.key, e.target.value, ip).then(() => {
						if (data.requires_restart)
							setNeedsRestart(true)
						mutate("settings")
						toast.success(translate("frontend.settings.string.updated"), {
							duration: 500
						})
					})
				}} />
				<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
			</div>
		}

		if (data.options.type == "number") {
			return (
				<div className="flex flex-col gap-2 w-full">
					<h4>{translate(data.name)}</h4>	
					<Input type="number" placeholder={pluginSettings[data.key]} className="font-customMono" onChange={(e) => {
						SetSettingByKey(plugin, data.key, parseFloat(e.target.value), ip).then(() => {
							if (data.requires_restart)
								setNeedsRestart(true)
							mutate("settings");
							toast.success(translate("frontend.settings.number.updated"), {
								duration: 500
							});
						});
					}} />
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
			)
		}
	}

	const SliderRenderer = (data:any) => {
		return ( // Add return statement here
			<SliderComponent
				pluginSettings={pluginSettings}
				data={data}
				plugin={plugin}
				ip={ip}
				setNeedsRestart={setNeedsRestart}
				mutate={mutate}
				toast={toast}
				translate={translate}
			/>
		);
	}

	const SwitchRenderer = (data:any) => {
		return <div className={"flex justify-between p-4 items-center" + GetBorderClassname(data.options.border)}>
				<div className="flex flex-col gap-1 pr-12">
					<h4 className="font-semibold">{translate(data.name)}</h4>
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
				<Switch checked={pluginSettings[data.key] && pluginSettings[data.key] || false} onCheckedChange={(bool) => {
					SetSettingByKey(plugin, data.key, bool, ip).then(() => {
						if (data.requires_restart)
							setNeedsRestart(true)
						mutate("settings")
						toast.success(translate("frontend.settings.boolean.updated"), {
							duration: 500
						})
					})
				}} />
			</div>
	}

	const ToggleRenderer = (data:any) => {
		return <div className="flex gap-4 w-full items-center">
				<Toggle pressed={pluginSettings[data.key] && pluginSettings[data.key] || false} onPressedChange={(bool) => {
					SetSettingByKey(plugin, data.key, bool, ip).then(() => {
						if (data.requires_restart)
							setNeedsRestart(true)
						mutate("settings")
						toast.success(translate("frontend.settings.boolean.updated"), {
							duration: 500
						})
					})
				}} className="w-8 h-8 p-[7px] data-[state=on]:bg-background data-[state=on]:hover:bg-white/10 " variant={"outline"}>
					{pluginSettings[data.key] && pluginSettings[data.key] ? <Check /> : <X />}
				</Toggle>
				{data.options.separator && <Separator orientation="vertical" />}
				<div>
					<h4>{translate(data.name)}</h4>
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
			</div>
	}

	const ButtonRenderer = (data:any) => {
		return <div className={"flex justify-between p-4 items-center" + GetBorderClassname(data.options.border)}>
				<div className="flex flex-col gap-1 pr-12">
					<h4 className="font-semibold">{translate(data.title)}</h4>
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
				<Button variant={"outline"} onClick={() => {
					DisablePlugin(plugin, ip).then(() => {
						toast.success(translate("frontend.settings.plugin.disabled"), {
							duration: 500
						})
					})
				}
				} className="min-w-32">{translate(data.text)}</Button>
			</div>
	}

	const GetBorderClassname = (border:boolean) => {
		if(border){
			return " p-4 border rounded-md"
		}
		return "p-4"
	}

	const PageRenderer = (data: any) => {
		if (!Array.isArray(data)) {
			data = [data]
		}
		return data.map((item: any) => {
			const key = Object.keys(item)[0];
			const key_data = item[key];

			// Page looks
			if(key == "title"){
				return TitleRenderer(key_data.text)
			}
			if(key == "description"){
				return DescriptionRenderer(key_data.text)
			}
			if (key == "label") {
				return LabelRenderer(key_data.text)
			}
			if (key == "separator") {
				return SeparatorRenderer()
			}
			if (key == "space") {
				return SpaceRenderer(key_data.amount)
			}
			if (key == "group") {
				const direction = key_data.direction
				if(direction == "horizontal"){
					return <div className={"flex gap-4 w-full rounded-md" + GetBorderClassname(key_data.border)}>
						{PageRenderer(key_data.components)}
					</div>
				}
				else{
					return <div className={"flex flex-col gap-4 w-full rounded-md" + GetBorderClassname(key_data.border)}>
						{PageRenderer(key_data.components)}
					</div>
				}
			}
			if (key == "tabview") {
				return <Tabs className="w-full" defaultValue={key_data.components[0].tab.name}>
					<TabsList className="w-full bg-transparent border">
						{key_data.components.map((tab:any, index:number) => (
							<TabsTrigger key={index} value={tab.tab.name}>{translate(tab.tab.name)}</TabsTrigger>
						))}
					</TabsList>
					{key_data.components.map((tab:any, index:number) => (
						<TabsContent key={index} value={tab.tab.name} className="w-full border rounded-md p-4">
							{PageRenderer(tab)}
						</TabsContent>
					))}
				</Tabs>
			}
			if (key == "tab"){
				return PageRenderer(key_data.components)
			}

			// Functions
			if (key == "button") {
				return ButtonRenderer(key_data)
			}

			// Options
			if (key == "input") {
				return InputRenderer(key_data)
			}
			if (key == "slider") {
				return SliderRenderer(key_data)
			}
			if (key == "switch") {
				return SwitchRenderer(key_data)
			}
			if (key == "toggle") {
				return ToggleRenderer(key_data)
			}
		});
	};

	const SettingsRenderer = (data:any) => {
		if(!pluginSettings[data.key])
		{
			if(data.type.default != undefined){
				pluginSettings[data.key] = data.type.default
			}	
		}

		// string, number, boolean, array, object, enum
		if (data.type.type == "string") {
			return <div className="flex flex-col gap-2">
				<h4>{translate(data.name)}</h4>
				<Input type="text" placeholder={pluginSettings[data.key]} onChange={(e) => {
					SetSettingByKey(plugin, data.key, e.target.value, ip).then(() => {
						if (data.requires_restart)
							setNeedsRestart(true)
						mutate("settings")
						toast.success(translate("frontend.settings.string.updated"), {
							duration: 500
						})
					})
				}} />
				<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
			</div>
		}

		if (data.type.type == "number") {
			if(!parseFloat(pluginSettings[data.key])){
				return (
					<div className="flex flex-col gap-2">
						<h4>...</h4>
						<Slider />
						<p className="text-xs text-muted-foreground">...</p>
					</div>
				)
			}
			if (data.type.min !== undefined && data.type.max !== undefined) { // Ensure min and max are not undefined
				return ( // Add return statement here
					<SliderComponent
						pluginSettings={pluginSettings}
						data={data}
						plugin={plugin}
						ip={ip}
						setNeedsRestart={setNeedsRestart}
						mutate={mutate}
						toast={toast}
						translate={translate}
					/>
				);
			}
			else
			{
				return (
					<div className="flex flex-col gap-2">
						<h4>{translate(data.name)}</h4>	
						<Input type="number" placeholder={pluginSettings[data.key]} className="font-customMono" onChange={(e) => {
							SetSettingByKey(plugin, data.key, parseFloat(e.target.value), ip).then(() => {
								if (data.requires_restart)
									setNeedsRestart(true)
								mutate("settings");
								toast.success(translate("frontend.settings.number.updated"), {
									duration: 500
								});
							});
						}} />
						<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
					</div>
				)
			}
		}

		if (data.type.type == "boolean") {
			return <div className="flex justify-between rounded-md border p-4 items-center">
				<div className="flex flex-col gap-1 pr-12">
					<h4 className="font-semibold">{translate(data.name)}</h4>
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
				<Switch checked={pluginSettings[data.key] && pluginSettings[data.key] || false} onCheckedChange={(bool) => {
					SetSettingByKey(plugin, data.key, bool, ip).then(() => {
						if (data.requires_restart)
							setNeedsRestart(true)
						mutate("settings")
						toast.success(translate("frontend.settings.boolean.updated"), {
							duration: 500
						})
					})
				}} />
			</div>
		}

		if (data.type.type == "array") {
			return <div>
				<h4>{translate(data.name)}</h4>
				<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				<div className="pt-2 flex flex-col gap-2">
					{pluginSettings[data.key] && pluginSettings[data.key].map((value:any, index:number) => (
						<div key={index} className="flex gap-2 items-center">
							<Input type={data.type.value_type && data.type.value_type || "text"} className="font-customMono" placeholder={value} onChange={(e) => {
								let newSettings = [...pluginSettings[data.key]]
								if (data.type.value_type == "number") {
									newSettings[index] = parseFloat(e.target.value)
								}
								if (data.type.value_type == "string") {
									newSettings[index] = e.target.value
								}
								SetSettingByKeys(plugin, data.key, newSettings, ip).then(() => {
									if (data.requires_restart)
										setNeedsRestart(true)
									mutate("settings")
									toast.success(translate("frontend.settings.array.updated_element"), {
										duration: 500
									})
								})
							}} />
							<Button variant={"destructive"} className="text-xs h-8 p-3" onClick={() => {
								let newSettings = [...pluginSettings[data.key]]
								newSettings.splice(index, 1)
								SetSettingByKeys(plugin, data.key, newSettings, ip).then(() => {
									if (data.requires_restart)
										setNeedsRestart(true)
									mutate("settings")
									toast.success(translate("frontend.settings.array.removed_element"), {
										duration: 500
									})
								})
							}} >{translate("frontend.settings.array.remove")}</Button>
						</div>
					))}
					<Button variant={"outline"} className="text-xs h-8 p-3" onClick={() =>
						{
							if (data.type.value_type == "number") {
								if (!pluginSettings[data.key] || pluginSettings[data.key].length == 0) {
									SetSettingByKey(plugin, data.key, [0], ip).then(() => {
										if (data.requires_restart)
											setNeedsRestart(true)
										mutate("settings")
										toast.success(translate("frontend.settings.array.added_element"), {
											duration: 500
										})
									})
								}
								else {
										SetSettingByKey(plugin, data.key, [...pluginSettings[data.key], 0], ip).then(() => {
										if (data.requires_restart)
											setNeedsRestart(true)
										mutate("settings")
										toast.success(translate("frontend.settings.array.added_element"), {
											duration: 500
										})
									})
								}
							} else {
								if (!pluginSettings[data.key] || pluginSettings[data.key].length == 0) {
									SetSettingByKey(plugin, data.key, [""], ip).then(() => {
										if (data.requires_restart)
											setNeedsRestart(true)
										mutate("settings")
										toast.success(translate("frontend.settings.array.added_element"), {
											duration: 500
										})
									})
								}
								else
								{
									SetSettingByKey(plugin, data.key, [...pluginSettings[data.key], ""], ip).then(() => {
										if (data.requires_restart)
											setNeedsRestart(true)
										mutate("settings")
										toast.success(translate("frontend.settings.array.added_element"), {
											duration: 500
										})
									})
								}
							}
						}
					}> 
						{translate("frontend.settings.array.add")}
					</Button>
				</div>
			</div>
		}

		if (data.type.type == "object") {
			return <p className="text-xs text-muted-foreground">Tried to show object [ {translate(data.name)} ] but objects are not yet supported!</p>
		}

		if (data.type.type == "enum") {
			if (!data.type.options) {
				return <p className="text-xs text-muted-foreground">{translate("frontend.settings.enum.no_enum")}</p>
			}
			return <div className="flex flex-col gap-2">
				<h4>{translate(data.name)}</h4>
				<Select defaultValue={pluginSettings[data.key]} onValueChange={(value) => {
					SetSettingByKey(plugin, data.key, value, ip).then(() => {
						if (data.requires_restart)
							setNeedsRestart(true)
						mutate("settings")
						toast.success(translate("frontend.settings.enum.updated"), {
							duration: 500
						})
					})
				}} >
					<SelectTrigger>
						<SelectValue placeholder={pluginSettings[data.key]}>{pluginSettings[data.key]}</SelectValue>
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

	console.log(settings)

	return (
		<TooltipProvider delayDuration={0}>
			<div className="text-left flex flex-col w-full max-w-[calc(60vw-64px)] gap-6 relative">
				{PageRenderer(settings)}
				<div className="h-12"></div>
			</div>
		</TooltipProvider>
	)
}
