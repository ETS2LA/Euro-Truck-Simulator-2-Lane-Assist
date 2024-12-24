"use client";

import { open_login_window } from "@/apis/account";
import { GetSettingsJSON } from "@/apis/settings";
import { Button } from "@/components/ui/button";
import { translate } from "@/apis/translation";
import Loader from "@/components/loader";
import { useState } from "react";
import { toast } from "sonner";
import useSWR from "swr";

export default function LoginPage() {
    const { data: settings } = useSWR("global", GetSettingsJSON, { refreshInterval: 1000 });
    const [loading, setLoading] = useState(false);

    if (!settings) {
        return <div className="w-full h-full font-geist pl-28 pr-20 pt-20 flex flex-col gap-6">Loading...</div>;
    }

    const user_id = settings?.user_id;
    const token = settings?.token;

    if (user_id && token) {
        if (loading) {
            setLoading(false);
            toast.success(translate("frontend.login.successful"), { description: translate("frontend.login.successful_description") });
        }
    }

    return (
        <div className="w-full h-full font-geist pl-28 pr-20 pt-20 flex flex-col gap-6">
            <div className="flex flex-col gap-2">
                <p className="text-xl font-semibold">{translate("frontend.login")}</p>
                <p className="max-w-96 text-muted-foreground">{translate("frontend.login.disclaimer")}</p>
            </div>
            <Button className="max-w-96" variant={"outline"} onClick={() =>{
                open_login_window();
                setLoading(true);
            }}>
                {translate("frontend.login.discord")} {loading && <Loader className="ml-2" />}
            </Button>
            <div>
                <p className="max-w-96 text-muted-foreground text-xs cursor-pointer" onClick={() => {
                    window.open("https://ets2la.github.io/documentation/privacy-policy/", "_blank");
                }}>{translate("frontend.login.privacy_policy")}</p>
            </div>
            {user_id && token && (
                <div className="flex flex-col gap-1">
                    <p className="text-muted-foreground max-w-96">
                        {translate("frontend.login.already_logged_in")}
                    </p>
                    <p className="text-muted-foreground max-w-96">
                        {`User ID: ${user_id}`}
                    </p>
                </div>
            )}
        </div>
    );
}