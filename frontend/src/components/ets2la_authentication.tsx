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
import { toast } from "sonner"

export function Authentication({ onLogin } : { onLogin: (token:string) => void }) {

	const handleGuestLogin = () => {
		toast.success("Logged in as a guest")
		onLogin("guest")
	}

	return (
	<div className="w-full lg:grid lg:grid-cols-2 h-full">
		<div className="flex items-center justify-center h-[calc(100vh-75px)]">
			<div className="mx-auto grid w-[350px] gap-6">
				<div className="grid gap-2 text-center">
					<h1 className="text-3xl font-bold">Login</h1>
					<p className="text-balance text-muted-foreground">
						Enter your credentials to login to your account
					</p>
				</div>
				<div className="grid gap-4">
					<div className="grid gap-2">
						<Label htmlFor="email">Username</Label>
						<Input
							id="email"
							type="text"
							placeholder="Tumppi066"
							required
						/>
					</div>
					<div className="grid gap-2">
						<div className="flex items-center">
							<Label htmlFor="password">Password</Label>
							<p
								className="ml-auto inline-block text-sm text-zinc-500"
							>
								Please come up with a new one.
							</p>
						</div>
						<Input id="password" type="password" placeholder="•••••••••••••" required />
					</div>
					<Button type="submit" className="w-full">
					Login
					</Button>
					<Button variant="outline" className="w-full" onClick={handleGuestLogin}>
						Use a Guest account
					</Button>
				</div>
				<div className="mt-4 text-center text-sm">
					Don&apos;t have an account?{" "}
					<Link href="#" className="underline">
						Sign up
					</Link>
				</div>
			</div>
		</div>
		<div className="hidden rounded-xl h-full lg:flex w-full">
			<Separator orientation='vertical' />
			<div className="w-full h-full p-20">
				<Accordion type="single" collapsible className="place-self-center">
					<AccordionItem value="item-1">
						<AccordionTrigger className="w-[400px]">Is it free?</AccordionTrigger>
						<AccordionContent>
							<p>Yes, all features are free to use.</p> 
							<p>With, or without an account.</p>
						</AccordionContent>
					</AccordionItem>
					<AccordionItem value="item-2">
						<AccordionTrigger className="w-[400px]">Do you collect private data?</AccordionTrigger>
						<AccordionContent>
							<p>No, we do not collect any private data out of principle. I do not want to handle any private data of users, that is too big of a responsibility for me.</p>
						</AccordionContent>
					</AccordionItem>
					<AccordionItem value="item-3">
						<AccordionTrigger className="w-[400px]">Why do I need an account?</AccordionTrigger>
						<AccordionContent>
							<p>You do not need an account to use the app. An account is only needed for the following <p className="font-bold inline">free</p> features.</p>
							<ul className="pt-2">
								<li>• Cloud settings saving</li>
								<li>• Developer comments on feedback and support requests</li>
								<li>• Personal data portal for ETS2 data (see past deliveries etc...)</li>
							</ul>
							<p className="pt-2">The app will still collect the ETS2 data without an account. But it will be appended to the public anonymous data portal instead of being tied to your account.</p>
						</AccordionContent>
					</AccordionItem>
					<AccordionItem value="item-4">
						<AccordionTrigger className="w-[400px]">How do I delete my account?</AccordionTrigger>
						<AccordionContent>
							<p>This has not yet been implemented in app, for now please contact me on discord @Tumppi066 or email to <a href="mailto:contact@tumppi066.fi" className="underline">contact@tumppi066.fi</a></p>
						</AccordionContent>
					</AccordionItem>
					<AccordionItem value="item-5">
						<AccordionTrigger className="w-[400px]">What data do you collect then?</AccordionTrigger>
						<AccordionContent>
							<p>We the following. Please note that this list includes everything that the app will collect "in the worst case". Most of these can be turned off in the settings!</p>
							<ul className="pt-2">
								<li>• Ping to the central server every 60s</li>
								<li>• App settings</li>
								<li>• App logs (on crash)</li>
								<li>• ETS2 API data (see <a href="https://github.com/RenCloud/scs-sdk-plugin?tab=readme-ov-file#telemetry-fields-and-the-c-object" target="_blank" className="underline"> the github repo</a>)</li>
							</ul>
							<p className="pt-2">None of the data we collect can be traced back to you. The server doesn't log IPs, ETS2 usernames etc...</p>
						</AccordionContent>
					</AccordionItem>
				</Accordion>
			</div>
		</div>
	</div>
)
}
