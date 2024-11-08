import RenderPage from "@/components/render_page"

export default function SDK({ ip }: { ip: string }) {
    return <RenderPage ip={ip} url="/setup/sdk" />;
}