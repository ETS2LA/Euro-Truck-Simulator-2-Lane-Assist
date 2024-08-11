import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/router";
import { translate } from "./translation";

export default function NotFound() {
    const { push } = useRouter();
    return (
        <div>
            <Card className="flex flex-col content-center text-center h-[calc(100vh-74px)] overflow-auto rounded-t-md">
                <div className="flex flex-col h-full items-center space-y-5 mt-40">
                    <h1 className="text-4xl font-bold">404</h1>
                    <h3 className="text-xl font-bold">{translate("frontend.404.title")}</h3>
                    <p className="text-zinc-600">{translate("frontend.404.message")}</p>
                    <Button onClick={() => push("/")}>{translate("frontend.404.button")}</Button>    
                </div>
            </Card>
        </div>
    );
}