import type { AppProps } from 'next/app'
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider"
import { ETS2LAMenubar } from "@/components/ets2la-menubar";
import { ETS2LACommandMenu } from '@/components/ets2la-command-menu';
import { GetIP } from "./server";
import { Toaster } from "@/components/ui/sonner"
import { Badge } from '@/components/ui/badge';
import { Unplug, Ellipsis } from 'lucide-react';
import useSWR from 'swr';


const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ETS2LA - Euro Truck Simulator 2 Lane Assist",
  description: "",
  icons: ["favicon.ico"],
};
import { useState, useRef } from 'react';

export default function MyApp({ Component, pageProps }: AppProps) {
  const [inputValue, setInputValue] = useState('localhost');
  const ipRef = useRef('localhost');

  const handleIpChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
  };

  const { data, error, isLoading, mutate } = useSWR(ipRef.current, () => GetIP(ipRef.current));

  const retry = () => {
    ipRef.current = inputValue;
    mutate(ipRef.current);
  };

  if (isLoading) return <div className='p-4'>
    <Badge variant={"outline"} className='gap-1'><Ellipsis className='w-5 h-5' /> Loading...</Badge>
  </div>

  if (error) return <div className='p-4'>
    <Badge variant={"destructive"} className='gap-1'><Unplug className='w-5 h-5' /> Lost connection to the server.</Badge>
    <input type="text" value={inputValue} onChange={handleIpChange} placeholder="Enter IP address" />
    <button onClick={retry}>Retry</button>
  </div>
  
  let ip = ipRef.current;

  console.log(ip);

  // Add the ip to the pageProps
  const newPageProps = { ...pageProps, ip };

  return (
    <div className='overflow-hidden p-3'>
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        <ETS2LAMenubar ip={ip} />
        <div className='py-3'>
          <Component {...newPageProps} />
        </div>
        <ETS2LACommandMenu ip={ip} />
        <Toaster position='bottom-center'/>
      </ThemeProvider>
    </div>
  );
}