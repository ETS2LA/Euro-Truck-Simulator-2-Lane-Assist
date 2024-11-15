import { ETS2LAPage } from "@/components/page/page";
import { GetPages } from "@/apis/backend";
import useSWR from "swr";

export default function RenderPage({ url, className }: { url: string, className?: string }) {
    const {data: pages} = useSWR("pages", () => GetPages(), {refreshInterval: 1000});
    if (!pages) return null;
    if (!pages[url]) return null;
    return (
        <ETS2LAPage plugin={pages[url][0]["settings"]} data={pages[url]} enabled={true} className={className} />
    )
}