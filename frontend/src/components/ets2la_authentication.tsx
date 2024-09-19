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
import { log } from "console"

export function Authentication({ onLogin } : { onLogin: (token:string) => void }) {
	const { theme, setTheme } = useTheme()

	const handleGuestLogin = () => {
		toast.success(translate("frontend.authentication.login_as_guest"))
		onLogin("guest")
	}

	const handleDiscordLogin = async function() {
		let loginURL = await fetch("https://api.ets2la.com/auth/discord", {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
			}
		})
		.then(response => response.json())

		const loginWindow = window.open(loginURL, '_blank', 'width=800,height=600');
	};

	return (
	<div className="w-full lg:grid lg:grid-cols-2 h-full">
		<div  className="flex items-center justify-center h-[calc(100vh-72px)]">
			<div className="mx-auto grid w-[350px] gap-6">
				<div className="grid gap-4">
					<Button onClick={handleDiscordLogin} disabled={true}>
						Login using Discord (Coming soon)
					</Button>
					<Button variant="outline" className="w-full" onClick={handleGuestLogin}>
						{translate("frontend.authentication.use_guest")}
					</Button>
				</div>
			</div>
		</div>
		<div className="hidden rounded-xl h-full lg:flex w-full">
			<Image
				src={theme === "dark" ? darkPromo : lightPromo}
				alt="ETS2LA Promo"
				className="rounded-xl h-full object-left object-cover animate-in fade-in-5 duration-500"
			/>
		</div>
	</div>
)
}
