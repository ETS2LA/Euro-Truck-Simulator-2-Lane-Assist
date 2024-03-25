import * as React from "react"
import { ETS2LAMenubar } from "@/components/ets2la-menubar";
import { Frametimes } from "@/components/frametimes";
import { Frame } from "lucide-react";
import { ETS2LAImmediateServer } from "@/components/ets2la-immediate-server";
import { GetIP, GetPlugins } from "./server";

export default async function Home() {
  let ip:string = await GetIP()
  
  return (
    <main className="">
        <ETS2LAMenubar ip={ip} />
    </main>
  );
}
