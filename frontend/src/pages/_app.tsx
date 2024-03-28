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

export default function MyApp({ Component, pageProps }: AppProps) {
  const { data, error, isLoading } = useSWR("ip", GetIP, { refreshInterval: 1000 });
  if (isLoading) return <div className='p-4'>
    <Badge variant={"outline"} className='gap-1'><Ellipsis className='w-5 h-5' /> Loading...</Badge>
  </div>
  if (error) return <div className='p-4'>
    <Badge variant={"destructive"} className='gap-1'><Unplug className='w-5 h-5' /> Lost connection to the server.</Badge>
  </div>
  let ip = data as string;

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