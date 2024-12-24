"use client"

import { useRouter } from "next/navigation";

export default function Home() {
    const { push } = useRouter();
    push("/about");
    return (
        <div>
            
        </div>
    );
}
