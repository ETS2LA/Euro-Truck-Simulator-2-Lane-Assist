import { Skeleton } from "@/components/ui/skeleton"
import useSWR, { mutate } from "swr"
import { GetPlugins } from "@/pages/backend"
import { Separator } from "./ui/separator"
import { set } from "date-fns"
import { Input } from "./ui/input"
import { GetSettingsJSON, SetSettingByKey, SetSettingByKeys } from "@/pages/settingsServer"
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
import { Switch } from "./ui/switch"
import { Button } from "./ui/button"
import { toast } from "sonner"
import { useEffect } from "react"
import { Slider } from "./ui/slider"
import { useState } from "react"

export function ETS2LASettingsPage({ ip, plugin }: { ip: string, plugin: string }) {
	const { data, error, isLoading } = useSWR("plugins", () => GetPlugins(ip), { refreshInterval: 500 })
	const { data: pluginSettings, error: pluginSettingsError, isLoading: pluginSettingsLoading } = useSWR("settings", () => GetSettingsJSON(plugin, ip))
	const [tempValue, setTempValue] = useState(0)

	// Update the settings when the plugin changes
	useEffect(() => {
		mutate("settings")
	}, [plugin])

	if (isLoading || pluginSettingsLoading) {
		return <Skeleton />
	}

	if (error || pluginSettingsError) {
		return <p className="text-xs text-muted-foreground">Error: {error}</p>
	}

	if (!data || !pluginSettings) {
		return <p className="text-xs text-muted-foreground">Got no data from the backend.</p>
	}

	console.log(plugin)
	console.log(data)

	const pluginData = data[plugin]

	if (!pluginData) {
		return <p className="text-xs text-muted-foreground">No data available for this plugin.</p>
	}

	const settings = pluginData.file.settings

	const TitleRenderer = (data:string) => {
		return <h3 className="font-medium">{data}</h3>
	}

	const DescriptionRenderer = (data:string) => {
		return <p className="text-sm text-muted-foreground">{data}</p>
	}

	const SeparatorRenderer = () => {
		return <>
			<div className="h-5"></div>
			<Separator />
			<div className="h-1"></div>
		</>
	}

	const SpecialsRenderer = (data:any) => {
		console.log(data)
		return <div>
			{data.map((special:any, index:number) => (
				<div key={index}>
					{special.special == "Title" && TitleRenderer(special.special_data)}
					{special.special == "Description" && DescriptionRenderer(special.special_data)}
					{special.special == "Separator" && SeparatorRenderer()}
				</div>
			))}
		</div>
	}

	const SettingsRenderer = (data:any) => {
		// string, number, boolean, array, object, enum
		console.log(data)
		if (data.type.type == "string") {
			return <div className="flex flex-col gap-2">
				<h4>{data.name}</h4>
				<Input type="text" placeholder={pluginSettings[data.key]} onChange={(e) => {
					SetSettingByKey(plugin, data.key, e.target.value, ip).then(() => {
						mutate("settings")
						toast.success("Updated setting.", {
							duration: 500
						})
					})
				}} />
				<p className="text-xs text-muted-foreground">{data.description}</p>
			</div>
		}

		if (data.type.type == "number") {
			if (data.type.min !== undefined && data.type.max !== undefined) { // Ensure min and max are not undefined
				const defaultValue = pluginSettings[data.key] && parseFloat(pluginSettings[data.key]) || 0
				const step = data.type.step && data.type.step || 1
				const suffix = data.type.suffix && data.type.suffix || ""
				return ( // Add return statement here
					<div className="flex flex-col gap-2">
						<h4>{data.name} - {defaultValue}{suffix}</h4>
						<Slider min={data.type.min} max={data.type.max} defaultValue={[defaultValue]} step={step} onValueCommit={(value) => {
							SetSettingByKey(plugin, data.key, value[0], ip).then(() => {
								mutate("settings")
								toast.success("Updated setting.", {
									duration: 500
								})
							})
						}} />
						<p className="text-xs text-muted-foreground">{data.description}</p>
					</div>
				);
			}
			else
			{
				return (
					<div className="flex flex-col gap-2">
						<h4>{data.name}</h4>	
						<Input type="number" placeholder={pluginSettings[data.key]} onChange={(e) => {
							SetSettingByKey(plugin, data.key, parseFloat(e.target.value), ip).then(() => {
								mutate("settings");
								toast.success("Updated setting.", {
									duration: 500
								});
							});
						}} />
						<p className="text-xs text-muted-foreground">{data.description}</p>
					</div>
				)
			}
		}

		if (data.type.type == "boolean") {
			return <div className="flex justify-between rounded-md border p-4 items-center">
				<div className="flex flex-col gap-1 pr-12">
					<h4 className="font-semibold">{data.name}</h4>
					<p className="text-xs text-muted-foreground">{data.description}</p>
				</div>
				<Switch checked={pluginSettings[data.key] && pluginSettings[data.key] || false} onCheckedChange={(bool) => {
					SetSettingByKey(plugin, data.key, bool, ip).then(() => {
						mutate("settings")
						toast.success("Updated setting.", {
							duration: 500
						})
					})
				}} />
			</div>
		}

		if (data.type.type == "array") {
			return <div>
				<h4>{data.name}</h4>
				<p className="text-xs text-muted-foreground">{data.description}</p>
				<div className="pt-2 flex flex-col gap-2">
					{pluginSettings[data.key] && pluginSettings[data.key].map((value:any, index:number) => (
						<div key={index} className="flex gap-2">
							<Input type={data.type.value_type && data.type.value_type || "text"} placeholder={value} onChange={(e) => {
								let newSettings = [...pluginSettings[data.key]]
								if (data.type.value_type == "number") {
									newSettings[index] = parseFloat(e.target.value)
								}
								if (data.type.value_type == "string") {
									newSettings[index] = e.target.value
								}
								SetSettingByKeys(plugin, data.key, newSettings, ip).then(() => {
									mutate("settings")
									toast.success("Updated array element.", {
										duration: 500
									})
								})
							}} />
							<Button variant={"destructive"} className="text-xs h-8 p-3" onClick={() => {
								let newSettings = [...pluginSettings[data.key]]
								newSettings.splice(index, 1)
								SetSettingByKeys(plugin, data.key, newSettings, ip).then(() => {
									mutate("settings")
									toast.success("Removed array element." , {
										duration: 500
									})
								})
							}} >Remove</Button>
						</div>
					))}
					<Button variant={"outline"} className="text-xs h-8 p-3" onClick={() =>
						{
							if (data.type.value_type == "number") {
								SetSettingByKey(plugin, data.key, [...pluginSettings[data.key], 0], ip).then(() => {
									mutate("settings")
									toast.success("Added new element to array.", {
										duration: 500
									})
								})
							} else {
								SetSettingByKey(plugin, data.key, [...pluginSettings[data.key], ""], ip).then(() => {
									mutate("settings")
									toast.success("Added new element to array.", {
										duration: 500
									})
								})
							}
						}
					}> 
						Add Element
					</Button>
					
				</div>
			</div>
		}

		if (data.type.type == "object") {
			return <p className="text-xs text-muted-foreground">Tried to show object [ {data.name} ] but objects are not yet supported!</p>
		}

		if (data.type.type == "enum") {
			if (!data.type.options) {
				return <p className="text-xs text-muted-foreground">No enum values provided.</p>
			}
			return <div className="flex flex-col gap-2">
				<h4>{data.name}</h4>
				<Select defaultValue={pluginSettings[data.key]} onValueChange={(value) => {
					SetSettingByKey(plugin, data.key, value, ip).then(() => {
						mutate("settings")
						toast.success("Updated setting.", {
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
				<p className="text-xs text-muted-foreground">{data.description}</p>
			</div>
		}

		return <p className="text-xs text-muted-foreground">Unknown data type: {data.type.type}</p>
	}


	return (
		<TooltipProvider delayDuration={0}>
			<div className="text-left flex flex-col w-full max-w-[calc(60vw-64px)] gap-6">
				{settings.map((setting:any, index:number) => (
					<div key={index}>
						{setting.specials && SpecialsRenderer(setting.specials)}
						{!setting.specials && SettingsRenderer(setting)}
					</div>
				))}
				<div className="h-12"></div>
			</div>
		</TooltipProvider>
	)
}
