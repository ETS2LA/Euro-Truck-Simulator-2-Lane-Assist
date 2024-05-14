import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/router";

export default function NotFound() {
    const { push } = useRouter();
    return (
        <div>
            <Card className="flex flex-col content-center text-center h-[calc(100vh-74px)] overflow-auto rounded-t-md">
                <div className="flex flex-col h-full items-center space-y-5 mt-40">
                    <h1 className="text-4xl font-bold">404</h1>
                    <h3 className="text-xl font-bold">You shouldn't be here</h3>
                    <p className="text-zinc-600">Click the button below to return to the home screen.</p>
                    <Button onClick={() => push("/")}>Main Menu</Button>    
                </div>
            </Card>
        </div>
    );
}