"use client"

import {
    Command,
    CommandDialog,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
    CommandSeparator,
    CommandShortcut,
} from "@/components/ui/command"

import { usePathname } from "next/navigation";
import * as React from "react"  
import { GetStates } from "@/pages/backend";
import { mutate } from "swr";
import useSWR from "swr";
import { useRouter } from "next/router";
import { toast } from "sonner";


export function ETS2LAStates({ip}: {ip: string}) {
    const { data, error } = useSWR("states", () => GetStates(ip), { refreshInterval: 1000, refreshWhenHidden: true })
    
    if (data) {
        console.log(data);
    } else if (error) {
        console.error(error);
    }
    
    return null;
}