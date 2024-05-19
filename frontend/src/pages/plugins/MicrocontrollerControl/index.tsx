import { Card, CardContent, CardDescription, CardFooter, 
    CardHeader, CardTitle } from "@/components/ui/card"
import { Popover, PopoverContent, 
    PopoverTrigger } from "@/components/ui/popover"
import { Tabs, TabsList, TabsTrigger, 
    TabsContent } from "@/components/ui/tabs"
import { Label } from "@/components/ui/label"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button"
import { toast } from "sonner";

import { GetSettingsJSON } from "@/pages/settings"
import { PluginFunctionCall } from "@/pages/backend";

import useSWR from "swr";
import { useState } from "react";

export default function MicrocontrollerControl({ ip }: { ip: string }) {
    const {data, error, isLoading} = useSWR("MicrocontrollerControl", () => GetSettingsJSON("MicrocontrollerControl", ip));
    
    return (
        <Card className="flex flex-col items-center text-center space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto relative">
            <div className="flex flex-row w-[calc(100vw-44px)] gap-3 m-2">
                <Popover>
                    <PopoverTrigger asChild>
                        <Button variant="secondary" className="font-bold w-42">
                            Microcontroller Control
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-48 h-auto">
                        <h2 className="text-base">Created by</h2>
                        <Separator className="my-2" />
                        <div className="flex pt-2">
                            <Avatar className="w-8 h-8">
                                <AvatarImage src="https://avatars.githubusercontent.com/u/110776467?v=4" />
                            </Avatar>
                            <h2 className="ml-2 text-base">Dyldev</h2>
                        </div>
                    </PopoverContent>
                </Popover>
                <Tabs defaultValue="general" className="w-full">
                    <TabsList className="grid grid-cols-3 w-full">
                        <TabsTrigger value="general">General</TabsTrigger>
                        <TabsTrigger value="setup">Setup</TabsTrigger>
                        <TabsTrigger value="boards">Boards</TabsTrigger>
                    </TabsList>
                    <TabsContent value="general">
                        <CardContent>
                            <div className="flex flex-col justify-start pt-2 self-start -ml-56 md:-ml-68">
                                <h3>General</h3>
                            </div>
                        </CardContent>
                    </TabsContent>
                    <TabsContent value="setup">
                        <CardContent>
                            <div className="flex flex-col justify-start pt-2 self-start -ml-56 md:-ml-68">
                                <h3>Setup</h3>
                            </div>
                        </CardContent>
                    </TabsContent>
                    <TabsContent value="boards">
                        <CardContent>
                            <div className="flex flex-col justify-start pt-2 self-start -ml-56 md:-ml-68">
                                <h3>Boards</h3>
                            </div>
                        </CardContent>
                    </TabsContent>
                </Tabs>
            </div>
        </Card>
    );
}





/*
    Page Example

    const [page, setPage] = useState(1);

    function Page1() {
        return (       
            <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto">
                <p className="text-3xl font-bold">Page 1</p>
                <Button>Back</Button>
                <Button onClick={() => setPage(2)}>Continue</Button>
            </Card>
        )
    }

    function Page2() {
        return (
            <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto">
                <p className="text-3xl font-bold">Page 2</p>
                <Button onClick={() => setPage(1)}>Back</Button>
                <Button>Continue</Button>
            </Card>
        )
    }

    return (
        <div>
            {page === 1 && <Page1 />}
            {page === 2 && <Page2 />}
        </div>
    )
*/