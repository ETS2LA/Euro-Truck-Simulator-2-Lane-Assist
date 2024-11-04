import { ETS2LAPage } from "@/components/page";
import { GetPages } from "@/apis/backend";
import useSWR from "swr";

export default function RenderPage({ url }: { url: string }) {
    const {data: pages} = useSWR("pages", () => GetPages(), {refreshInterval: 1000});
    if (!pages) return null;
    return (
        <ETS2LAPage plugin={pages[url][0]["settings"]} data={pages[url]} enabled={true} />
    )
}