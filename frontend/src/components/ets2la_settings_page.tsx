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
import { Switch } from "./ui/switch"
import { Button } from "./ui/button"
import { toast } from "sonner"
import { useEffect } from "react"
import { Slider } from "./ui/slider"
import { useState } from "react"
import { translate } from "@/pages/translation"

export function ETS2LASettingsPage({ ip, plugin }: { ip: string, plugin: string }) {
	const { data, error, isLoading } = useSWR("plugins", () => GetPlugins(ip), { refreshInterval: 500 })
	const { data: pluginSettings, error: pluginSettingsError, isLoading: pluginSettingsLoading } = useSWR("settings", () => GetSettingsJSON(plugin, ip))
	const [needsRestart, setNeedsRestart] = useState(false)

	// Update the settings when the plugin changes
	useEffect(() => {
		setNeedsRestart(false)
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

	const pluginData = data[plugin]

	if (!pluginData) {
		return <p className="text-xs text-muted-foreground">No data available for this plugin.</p>
	}

	const settings = pluginData.file.settings

	const TitleRenderer = (data:string) => {
		return <h3 className="font-medium">{translate(data)}</h3>
	}

	const DescriptionRenderer = (data:string) => {
		return <p className="text-sm text-muted-foreground">{translate(data)}</p>
	}

	const SeparatorRenderer = () => {
		return <>
			<div className="h-5"></div>
			<Separator />
			<div className="h-1"></div>
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

	const SpecialsRenderer = (data:any) => {
		return <div>
			{data.map((special:any, index:number) => (
				<div key={index}>
					{special.special == "Title" && TitleRenderer(special.special_data)}
					{special.special == "Description" && DescriptionRenderer(special.special_data)}
					{special.special == "Separator" && SeparatorRenderer()}
					{special.special == "Space" && SpaceRenderer(special.special_data)}
				</div>
			))}
		</div>
	}

	const SettingsRenderer = (data:any) => {
		// string, number, boolean, array, object, enum
		if (data.type.type == "string") {
			return <div className="flex flex-col gap-2">
				<h4>{translate(data.name)}</h4>
				<Input type="text" placeholder={pluginSettings[data.key]} onChange={(e) => {
					SetSettingByKey(plugin, data.key, e.target.value, ip).then(() => {
						if (data.requires_restart)
							setNeedsRestart(true)
						mutate("settings")
						toast.success("Updated setting.", {
							duration: 500
						})
					})
				}} />
				<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
			</div>
		}

		if (data.type.type == "number") {
			const value = pluginSettings[data.key] && parseFloat(pluginSettings[data.key]) || 0
			if (data.type.min !== undefined && data.type.max !== undefined && value != 0) { // Ensure min and max are not undefined
				const step = data.type.step && data.type.step || 1
				const suffix = data.type.suffix && data.type.suffix || ""
				return ( // Add return statement here
					<div className="flex flex-col gap-2">
						<h4>{translate(data.name)}  —  {value}{suffix}</h4>
						<Slider min={data.type.min} max={data.type.max} defaultValue={[value]} step={step} onValueCommit={(value) => {
							SetSettingByKey(plugin, data.key, value[0], ip).then(() => {
								if (data.requires_restart)
									setNeedsRestart(true)
								mutate("settings")
								toast.success("Updated setting.", {
									duration: 500
								})
							})
						}} />
						<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
					</div>
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
								toast.success("Updated setting.", {
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
						toast.success("Updated setting.", {
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
									toast.success("Updated array element.", {
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
								if (!pluginSettings[data.key] || pluginSettings[data.key].length == 0) {
									SetSettingByKey(plugin, data.key, [0], ip).then(() => {
										if (data.requires_restart)
											setNeedsRestart(true)
										mutate("settings")
										toast.success("Added new element to array.", {
											duration: 500
										})
									})
								}
								else {
										SetSettingByKey(plugin, data.key, [...pluginSettings[data.key], 0], ip).then(() => {
										if (data.requires_restart)
											setNeedsRestart(true)
										mutate("settings")
										toast.success("Added new element to array.", {
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
										toast.success("Added new element to array.", {
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
										toast.success("Added new element to array.", {
											duration: 500
										})
									})
								}
							}
						}
					}> 
						Add Element
					</Button>
				</div>
			</div>
		}

		if (data.type.type == "object") {
			return <p className="text-xs text-muted-foreground">Tried to show object [ {translate(data.name)} ] but objects are not yet supported!</p>
		}

		if (data.type.type == "enum") {
			if (!data.type.options) {
				return <p className="text-xs text-muted-foreground">No enum values provided.</p>
			}
			return <div className="flex flex-col gap-2">
				<h4>{translate(data.name)}</h4>
				<Select defaultValue={pluginSettings[data.key]} onValueChange={(value) => {
					SetSettingByKey(plugin, data.key, value, ip).then(() => {
						if (data.requires_restart)
							setNeedsRestart(true)
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
				<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
			</div>
		}

		return <p className="text-xs text-muted-foreground">Unknown data type: {data.type.type}</p>
	}


	return (
		<TooltipProvider delayDuration={0}>
			<div className="text-left flex flex-col w-full max-w-[calc(60vw-64px)] gap-6 relative">
				{settings.map((setting:any, index:number) => (
					<div key={index}>
						{setting.specials && SpecialsRenderer(setting.specials)}
						{!setting.specials && SettingsRenderer(setting)}
					</div>
				))}
				<div className="h-12"></div>
			</div>
			{needsRestart && data[plugin]["enabled"] && 
				<div className="absolute top-4 left-0 right-0 max-w-[calc(60vw-64px)] h-12 bg-red-950 rounded-md text-sm font-customSans justify-center text-center flex">
					<Button className="w-full h-full" variant="destructive" onClick={() => {
						setNeedsRestart(false)
						DisablePlugin(plugin, ip).then(() => {
							EnablePlugin(plugin, ip).then(() => {
								toast.success("Restart Successful", {
									duration: 1000
								})
							})
						})
					}
					}>Plugin needs a restart to update settings.</Button>
				</div>
			}
		</TooltipProvider>
	)
}
