import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogFooter,
    DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import React, { useState, useEffect } from 'react';
import { toast } from "sonner"
import { token, setToken } from '@/pages/server';

export default function LoginPage() {
    // Handle login and signup inputs
    const [open, setOpen] = useState(true);
    const [SignupUsername, setSignupUsername] = useState('');
    const [SignupPassword, setSignupPassword] = useState('');
    const [LoginUsername, setLoginUsername] = useState('');
    const [LoginPassword, setLoginPassword] = useState('');
    const SignupUsernameHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSignupUsername(event.target.value);
    }
    const SignupPasswordHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSignupPassword(event.target.value);
    }
    const LoginUsernameHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
        setLoginUsername(event.target.value);
    }
    const LoginPasswordHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
        setLoginPassword(event.target.value);
    }

    const handleSignupSubmit = () => {
        // Display a toast if either username or password is empty
        if (SignupUsername === '' || SignupPassword === '') {
            return (
                toast("Password and Username cannot be empty", {
                    description: "Please enter a valid username and password",
                    action: {
                      label: "Close",
                      onClick: () => console.log("Undo"),
                    },
                  })
            )
        }

        // PLACE THE LOGIC FOR SIGNING UP HERE

        console.log('Signup Username:', SignupUsername);
        console.log('Signup Password:', SignupPassword);
        setOpen(false);
    };
    const handleLoginSubmit = () => {
        // Display a toast if either username or password is empty
        if (SignupUsername === '' || SignupPassword === '') {
            return (
                toast("Password and Username cannot be empty", {
                    description: "Please enter a valid username and password",
                    action: {
                      label: "Close",
                      onClick: () => console.log("Undo"),
                    },
                  })
            )
        }

        // PLACE THE LOGIC FOR LOGGING IN HERE

        console.log('Login Username:', LoginUsername);
        console.log('Login Password:', LoginPassword);
        setOpen(false);
      };

    // Handle dialog open and close (This will be opened automatically on page load, should be changed)
    useEffect(() => {
        setOpen(true);
    }, []);
    // Handle the closing of the dialog
    const handleClose = () => {
        setToken("guest"); // Set the token to guest
        toast("You are now signed in as a guest")
    };

    // Handle login and signup tab changes (For switching between the tabs with buttons)
    const [tab, setTab] = useState("Login");
    const handleTabChange = (value: string) => {
        destroyH2(); // Destroy the "You aren't signed in!" text when a tab is opened
        setTab(value); // Set the current tab
    }

    // Handle the destruction of the "You aren't signed in!" text
    const [showH2, setShowH2] = useState(true);
    const destroyH2 = () => {
      setShowH2(false);
    };

    return (
        <Dialog open={true}>
            <DialogContent className="sm:max-w-[375px]">  
                <Tabs className="w-full" onValueChange={value => handleTabChange(value)} value={tab}>
                    <TabsList className="w-full">
                        <TabsTrigger value="Login" className="w-1/2">Login</TabsTrigger>
                        <TabsTrigger value="Signup" className="w-1/2">Create Account</TabsTrigger>
                    </TabsList>
                    <TabsContent value="Signup" className="space-y-5">
                        <div className="space-y-1 mt-5">
                            <h2>Sign up</h2>
                            <p className="text-stone-500">Sign up for a new ETS2LA account</p>
                        </div>
                        <div className="flex-column space-y-4 pt-2">
                            <Input placeholder="Username" value={SignupUsername} onChange={SignupUsernameHandler}/>
                            <Input placeholder="Password" value={SignupPassword} onChange={SignupPasswordHandler}/>
                        </div>
                        <div className="grid grid-cols-2 w-full gap-5 pb-2">
                            <Button onClick={handleSignupSubmit}>Continue</Button>
                            <Button onClick={handleClose} variant={"secondary"}>Guest</Button>
                        </div>
                    </TabsContent>
                    <TabsContent value="Login" className="space-y-5">
                        <div className="space-y-1 mt-5">
                            <h2>Log in</h2>
                            <p className="text-stone-500">Log in to your existing ETS2LA account</p>
                        </div>
                        <div className="flex-column space-y-4 pt-2">
                            <Input placeholder="Username" value={LoginUsername} onChange={LoginUsernameHandler}/>
                            <Input placeholder="Password" value={LoginPassword} onChange={LoginPasswordHandler}/>
                        </div>
                        <div className="grid grid-cols-2 w-full gap-5 pb-2">
                            <Button onClick={handleLoginSubmit}>Log In</Button>
                            <Button onClick={handleClose} variant={"secondary"}>Guest</Button>
                        </div>
                    </TabsContent>
                </Tabs>
            </DialogContent>
        </Dialog>
    )
}

