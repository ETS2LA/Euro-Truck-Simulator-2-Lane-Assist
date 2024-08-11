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
import { CheckUsernameAvailability, Register, Login } from "@/pages/account"
import { useState } from "react"
import { CircleCheckBig, LogIn } from "lucide-react"
import darkPromo from "@/assets/promo_dark.png"
import lightPromo from "@/assets/promo_light.png"
import { useTheme } from "next-themes"
import { translate } from "@/pages/translation"

export function Authentication({ onLogin } : { onLogin: (token:string) => void }) {
	const [username, setUsername] = useState("")
	const [usernameAvailable, setUsernameAvailable] = useState(false)
	const [password, setPassword] = useState("")
	const [passwordRepeat, setPasswordRepeat] = useState("")
	const [isDialogOpen, setIsDialogOpen] = useState(false);
	const { theme, setTheme } = useTheme()
	const [passwordState, setPasswordState] = useState({
		uppercase: false,
		lowercase: false,
		length: 0,
		eightCharsOrGreater: false,
	});


	const handleGuestLogin = () => {
		toast.success(translate("frontend.authentication.login_as_guest"))
		onLogin("guest")
	}

	const handleLogin = async () => {
		if (usernameAvailable) {
			setIsDialogOpen(true)
		} else {
			const token = await Login(username, password)
			if (token) {
				toast.success(translate("frontend.authentication.logged_in"))
				onLogin(token)
			} else {
				toast.error(translate("frontend.authentication.password_incorrect", username))
			}
		}
	}	

	const handleDialogClose = async (confirmed: boolean) => {
		setIsDialogOpen(false)
		if (confirmed) {
			if (password !== passwordRepeat) {
				toast.error(translate("frontend.authentication.passwords_dont_match"))
				return
			}
			if (!passwordState.uppercase || !passwordState.lowercase || !passwordState.eightCharsOrGreater) {
				toast.error(translate("frontend.authentication.password_requirements_not_met"))
				return
			}
			const token = await Register(username, password)
			if (token) {
				toast.success(translate("frontend.authentication.account_created"))
				onLogin(token)
			} else {
				toast.error(translate("frontend.authentication.account_creation_failed"))
			}
		}
	}

	const onUsernameChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
		const username = e.target.value
		setUsername(username)
		if (await CheckUsernameAvailability(username)) {
			setUsernameAvailable(true)
		} else if (username === "Username") {
			setUsernameAvailable(true)
		} else {
			setUsernameAvailable(false)
		}
	}

	const onPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const newPassword = e.target.value; // -> created const not to use 'e.target.value' two times
		setPassword(newPassword)
		
		// set the new password state
		setPasswordState(getPasswordStrength(newPassword))
	}

	const onPasswordRepeatChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		setPasswordRepeat(e.target.value)
	}

	function passwordsMatch() {
		if (passwordRepeat === "" || password === "") {
			return true;
		}
		return password === passwordRepeat;
	}

	function getPasswordStrength(password: string) {
		// Define regular expressions for different criteria
		const lowercaseRegex = /[a-z]/; // all lowercase chars
		const uppercaseRegex = /[A-Z]/; // all uppercase chars
		
		// Define passwordMeter to check which symbols/chars are in the password
		const passwordMeter = {
			uppercase: Boolean(password.match(uppercaseRegex)),
			lowercase: Boolean(password.match(lowercaseRegex)),
			length: password.length,
			eightCharsOrGreater: password.length >= 8,
		  }
		
		  // return it
		return passwordMeter
	}

	return (
	<div className="w-full lg:grid lg:grid-cols-2 h-full">
		<div  className="flex items-center justify-center h-[calc(100vh-72px)]">
			<div className="mx-auto grid w-[350px] gap-6">
				<div className="grid gap-2 text-center">
					<h1 className="text-3xl font-bold">{usernameAvailable ? translate("frontend.authentication.signup") : translate("frontend.authentication.login")}</h1>
					<p className="text-balance text-muted-foreground">
						{translate("frontend.authentication.login_prompt")}
					</p>
				</div>
				<div className="grid gap-4">
					<div className="grid gap-2">
						<div className="flex items-center">
							<Label htmlFor="email">{translate("frontend.authentication.username")}</Label>
							<p className="ml-auto text-sm flex gap-1 items-center text-zinc-500">
								{usernameAvailable ? (
									<CircleCheckBig className="w-4 h-4" />
								) : (
									<LogIn className="w-4 h-4" />
								)}
							</p>
						</div>
						<Input
							id="email"
							type="text"
							placeholder={translate("frontend.authentication.username")}
							required
							onChange={onUsernameChange}
						/>
					</div>
					<div className="grid gap-2">
						<div className="flex items-center">
							<Label htmlFor="password">{translate("frontend.authentication.password")}</Label>
						</div>
						<div className="flex gap-2">
							<Input id="password" type="password" placeholder={translate("frontend.authentication.password")} required onChange={onPasswordChange} />
							<Input id="passwordRepeat" type="password" placeholder={translate("frontend.authentication.repeat_password")} required onChange={onPasswordRepeatChange}
								className={passwordsMatch() ? (usernameAvailable ? "focus:border-2 transition-all" : "transition-all hidden") : "border-red-700 focus:border-2 transition-all"}
							/>
						</div>
					</div>
					{usernameAvailable ? (
						<>
							<AlertDialog>
								<AlertDialogTrigger>
									<Button type="submit" className="w-full" onClick={handleLogin}>
										{translate("frontend.authentication.signup_button")}
									</Button>
								</AlertDialogTrigger>
								<AlertDialogContent>
									<AlertDialogHeader>
										<AlertDialogTitle>{translate("confirm")}</AlertDialogTitle>
										<AlertDialogDescription>
											{translate("frontend.authentication.account_creation_confirmation")}
										</AlertDialogDescription>
									</AlertDialogHeader>
									<AlertDialogFooter>
										<AlertDialogCancel onClick={() => handleDialogClose(false)}>{translate("cancel")}</AlertDialogCancel>
										<AlertDialogAction onClick={() => handleDialogClose(true)}>{translate("continue")}</AlertDialogAction>
									</AlertDialogFooter>
								</AlertDialogContent>
							</AlertDialog>
						</>
					) : (
						<Button type="submit" className="w-full" onClick={handleLogin}>
							{usernameAvailable ? translate("frontend.authentication.signup_button") : translate("frontend.authentication.login_button")}
						</Button>
					)}
					<Button variant="outline" className="w-full" onClick={handleGuestLogin}>
						{translate("frontend.authentication.use_guest")}
					</Button>
					<Accordion type="single" collapsible className="w-[350px] place-self-center" value={usernameAvailable ? passwordState.uppercase && passwordState.lowercase && passwordState.eightCharsOrGreater ? "" : "item-1" : ""}>
						<AccordionItem value="item-1">
							<AccordionTrigger className="w-[400px]"><p
								className={!usernameAvailable ? "text-zinc-500 transition-colors ease-in-out duration-500" : passwordState.uppercase && passwordState.lowercase && passwordState.eightCharsOrGreater ? "text-green-400 transition-colors ease-in-out duration-500" : "text-red-400 transition-colors ease-in-out duration-500"}>
									{translate("frontend.authentication.password_requirements")}
								</p>
							</AccordionTrigger>
							<AccordionContent className="flex justify-between pr-0 w-full p-4 pt-0">
								<p style={{fontSize: '0.9em'}}
									className={passwordState.uppercase ? "text-green-400 transition-colors ease-in-out duration-500" : "text-red-400 transition-colors ease-in-out duration-500"}> 
									{translate("frontend.authentication.uppercase")} 
								</p>
								<p style={{fontSize: '0.9em'}}
									className={passwordState.lowercase ? "text-green-400 transition-colors ease-in-out duration-500" : "text-red-400 transition-colors ease-in-out duration-500"}> 
									{translate("frontend.authentication.lowercase")} 
								</p>
								<p style={{fontSize: '0.9em'}}
									className={passwordState.eightCharsOrGreater ? "text-green-400 transition-colors ease-in-out duration-500" : "text-red-400 transition-colors ease-in-out duration-500"}> 
									{translate("frontend.authentication.characters", passwordState.length)} 
								</p>
							</AccordionContent>
						</AccordionItem>
					</Accordion>
				</div>
				<div className="mt-4 text-center text-sm">
					<p className="text-muted-foreground">{translate("frontend.authentication.account_creation_prompt")}</p>
				</div>
			</div>
		</div>
		<div className="hidden rounded-xl h-full lg:flex w-full">
			{usernameAvailable ? (
			<>
				<Separator orientation='vertical' />
				<div className="w-full h-full p-20 animate-in fade-in-5 duration-500">
					<Accordion type="single" collapsible className="place-self-center">
						<AccordionItem value="item-1">
							<AccordionTrigger className="w-[400px]">{translate("frontend.authentication.first")}</AccordionTrigger>
							<AccordionContent>
								<p>{translate("frontend.authentication.first_line_1")}</p> 
								<p>{translate("frontend.authentication.first_line_2")}</p>
							</AccordionContent>
						</AccordionItem>
						<AccordionItem value="item-2">
							<AccordionTrigger className="w-[400px]">{translate("frontend.authentication.second")}</AccordionTrigger>
							<AccordionContent>
								<p>{translate("frontend.authentication.second_line_1")}</p>
							</AccordionContent>
						</AccordionItem>
						<AccordionItem value="item-3">
							<AccordionTrigger className="w-[400px]">{translate("frontend.authentication.third")}</AccordionTrigger>
							<AccordionContent>
								<p>{translate("frontend.authentication.third_line_1")}</p>
								<ul className="pt-2">
									<li>• {translate("frontend.authentication.third_line_1_1")}</li>
									<li>• {translate("frontend.authentication.third_line_1_2")}</li>
									<li>• {translate("frontend.authentication.third_line_1_3")}</li>
								</ul>
								<p className="pt-2">{translate("frontend.authentication.third_line_2")}</p>
							</AccordionContent>
						</AccordionItem>
						<AccordionItem value="item-4">
							<AccordionTrigger className="w-[400px]">{translate("frontend.authentication.fourth")}</AccordionTrigger>
							<AccordionContent>
								<p>{translate("frontend.authentication.fourth_line_1")}</p>
							</AccordionContent>
						</AccordionItem>
						<AccordionItem value="item-5">
							<AccordionTrigger className="w-[400px]">{translate("frontend.authentication.fifth")}</AccordionTrigger>
							<AccordionContent>
								<p>{translate("frontend.authentication.fifth_line_1")}</p>
								<ul className="pt-2">
									<li>• {translate("frontend.authentication.fifth_line_1_1")}</li>
									<li>• {translate("frontend.authentication.fifth_line_1_2")}</li>
									<li>• {translate("frontend.authentication.fifth_line_1_3")}</li>
									<li>• {translate("frontend.authentication.fifth_line_1_4")}</li>
									<li>  <a href="https://github.com/RenCloud/scs-sdk-plugin?tab=readme-ov-file#telemetry-fields-and-the-c-object" target="_blank" className="underline">https://github.com/RenCloud/scs-sdk-plugin</a></li>
								</ul>
								<p className="pt-2">{translate("frontend.authentication.fifth_line_2")}</p>
							</AccordionContent>
						</AccordionItem>
						<AccordionItem value="item-6">
							<AccordionTrigger className="w-[400px]">{translate("frontend.authentication.sixth")}</AccordionTrigger>
							<AccordionContent>
								<p>{translate("frontend.authentication.sixth_line_1")}</p>
								<p className="pt-1">{translate("frontend.authentication.sixth_line_2")}</p>
							</AccordionContent>
						</AccordionItem>
					</Accordion>
				</div>
			</>
			) : 
			(
				<Image
					src={theme === "dark" ? darkPromo : lightPromo}
					alt="ETS2LA Promo"
					className="rounded-xl h-full object-left object-cover animate-in fade-in-5 duration-500"
				/>
			)}
		</div>
	</div>
)
}
