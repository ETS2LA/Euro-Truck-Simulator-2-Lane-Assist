import Image from "next/image"
import Link from "next/link"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import {
	Accordion,
	AccordionContent,
	AccordionItem,
	AccordionTrigger,
} from "@/components/ui/accordion"
import {
	AlertDialog,
	AlertDialogAction,
	AlertDialogCancel,
	AlertDialogContent,
	AlertDialogDescription,
	AlertDialogFooter,
	AlertDialogHeader,
	AlertDialogTitle,
	AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { toast } from "sonner"
import { useState } from "react"
import { CircleCheckBig, LogIn } from "lucide-react"
import darkPromo from "@/assets/promo_dark.png"
import lightPromo from "@/assets/promo_light.png"
import { useTheme } from "next-themes"
import { translate } from "@/pages/translation"
import { GetSettingByKey, SetSettingByKey } from "@/pages/settingsServer"
import { log } from "console"
import { DiscordLogoIcon } from "@radix-ui/react-icons"
import { CheckWindow } from "@/pages/backend"

export function Authentication({ onLogin, ip } : { onLogin: (token:string) => void, ip: string }) {
	const { theme, setTheme } = useTheme()

	const handleGuestLogin = () => {
		toast.success(translate("frontend.authentication.login_as_guest"))
		onLogin("guest")
	}

	const CheckServerConnection = async () => {
		const isConnected = await fetch("https://api.ets2la.com/heartbeat", {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
			},
		})
			.then((response) => response.ok)
			.catch((error) => {
				return false;
			});
		return isConnected;
	}

	const handleDiscordLogin = async function() {
		const isConnected = await CheckServerConnection();
		if (!isConnected) {
			toast.error("The ETS2LA server is currently unavailable! Please log in as a guest for now.");
			return;
		}
		let loginURL = await fetch("https://api.ets2la.com/auth/discord", {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
			}
		})
		.then(response => response.json())
		let discordOpen = await CheckWindow("Discord", ip)
		console.log(discordOpen)
		if(discordOpen) {
			window.open(loginURL.replace("https://", "discord://"), '_self');
			toast.info(translate("frontend.authentication.check_discord"))
		} else{
			window.open(loginURL, '_blank', 'width=800,height=600');
		}
		SetSettingByKey("global", "token", null, ip)
		SetSettingByKey("global", "user_id", null, ip)
		// Wait for the token to be set
		const interval = setInterval(async () => {
			const token = await GetSettingByKey("global", "token", ip)
			if (token) {
				toast.success(translate("frontend.authentication.logged_in"))
				clearInterval(interval)
				onLogin(token)
			}
		}, 1000)
	};

	const DiscordIcon = () => (
		<svg viewBox="0 -28.5 256 256" className="w-5 h-5">
			<path
				d="M216.856339,16.5966031 C200.285002,8.84328665 182.566144,3.2084988 164.041564,0 C161.766523,4.11318106 159.108624,9.64549908 157.276099,14.0464379 C137.583995,11.0849896 118.072967,11.0849896 98.7430163,14.0464379 C96.9108417,9.64549908 94.1925838,4.11318106 91.8971895,0 C73.3526068,3.2084988 55.6133949,8.86399117 39.0420583,16.6376612 C5.61752293,67.146514 -3.4433191,116.400813 1.08711069,164.955721 C23.2560196,181.510915 44.7403634,191.567697 65.8621325,198.148576 C71.0772151,190.971126 75.7283628,183.341335 79.7352139,175.300261 C72.104019,172.400575 64.7949724,168.822202 57.8887866,164.667963 C59.7209612,163.310589 61.5131304,161.891452 63.2445898,160.431257 C105.36741,180.133187 151.134928,180.133187 192.754523,160.431257 C194.506336,161.891452 196.298154,163.310589 198.110326,164.667963 C191.183787,168.842556 183.854737,172.420929 176.223542,175.320965 C180.230393,183.341335 184.861538,190.991831 190.096624,198.16893 C211.238746,191.588051 232.743023,181.531619 254.911949,164.955721 C260.227747,108.668201 245.831087,59.8662432 216.856339,16.5966031 Z M85.4738752,135.09489 C72.8290281,135.09489 62.4592217,123.290155 62.4592217,108.914901 C62.4592217,94.5396472 72.607595,82.7145587 85.4738752,82.7145587 C98.3405064,82.7145587 108.709962,94.5189427 108.488529,108.914901 C108.508531,123.290155 98.3405064,135.09489 85.4738752,135.09489 Z M170.525237,135.09489 C157.88039,135.09489 147.510584,123.290155 147.510584,108.914901 C147.510584,94.5396472 157.658606,82.7145587 170.525237,82.7145587 C183.391518,82.7145587 193.761324,94.5189427 193.539891,108.914901 C193.539891,123.290155 183.391518,135.09489 170.525237,135.09489 Z"
				fill="#5865F2"
			/>
		</svg>
	);

	return (
	<div className="w-full lg:grid lg:grid-cols-2 h-full">
		<div  className="flex items-center justify-center h-[calc(100vh-72px)]">
			<div className="mx-auto grid w-[350px] gap-6">
				<div className="grid gap-4">
					<Button onClick={handleDiscordLogin} variant={"outline"} className="flex gap-2 transition-all items-center content-center">
						<DiscordIcon />
						{translate("frontend.authentication.login_with_discord")}
					</Button>
					<Button variant="outline" className="w-full" onClick={handleGuestLogin}>
						{translate("frontend.authentication.use_guest")}
					</Button>
				</div>
				<p className="text-xs text-muted-foreground">
					{translate("frontend.authentication.login_info")} <a href="https://ets2la.github.io/documentation/privacy-policy/" target="_blank" className="text-accent-foreground">ets2la.com</a>
				</p>
				<p className="text-xs text-muted-foreground">
					{translate("frontend.authentication.register_info")} <a className="text-accent-foreground">(TODO)</a>
				</p>
			</div>
		</div>
		<div className="hidden rounded-xl h-full lg:flex w-full">
			<Image
				src={theme === "light" ? lightPromo : darkPromo}
				alt="ETS2LA Promo"
				className="rounded-xl h-full object-left object-cover animate-in fade-in-5 duration-500"
			/>
		</div>
	</div>
)
}
