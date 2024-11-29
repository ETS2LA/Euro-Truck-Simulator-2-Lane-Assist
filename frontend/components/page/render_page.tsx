import { ETS2LAPage } from "@/components/page/page";
import { GetPages } from "@/apis/backend";
import useSWR from "swr";
import { motion } from "framer-motion";

export default function RenderPage({ url, className }: { url: string, className?: string }) {
    const {data: pages} = useSWR("pages", () => GetPages(), {refreshInterval: 1000});
    if (!pages) return null;
    if (!pages[url]) return null;
    console.log(pages[url]);
    return (
        <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6 }}
        >
            <ETS2LAPage plugin={pages[url][0]["settings"]} data={pages[url]} enabled={true} className={className} />
        </motion.div>
    )
}