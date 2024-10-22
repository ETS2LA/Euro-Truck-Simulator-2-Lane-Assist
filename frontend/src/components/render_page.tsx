import { ETS2LAPage } from "./ets2la_page";
import { GetPages } from "@/pages/backend";
import useSWR from "swr";

export default function RenderPage({ ip, url }: { ip: string, url: string }) {
    const {data: pages, error: pagesError, isLoading: pagesIsLoading} = useSWR("pages", () => GetPages(ip), {refreshInterval: 1000});
    console.log(pages[url])
    return (
        <ETS2LAPage ip={ip} plugin={pages[url][0]["settings"]} data={pages[url]} enabled={true} />
    )
}