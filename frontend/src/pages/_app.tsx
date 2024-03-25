import type { AppProps } from 'next/app'
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider"
import { ETS2LAMenubar } from "@/components/ets2la-menubar";
import { ETS2LACommandMenu } from '@/components/ets2la-command-menu';
import { GetIP } from "./server";
import { Toaster } from "@/components/ui/sonner"
import useSWR from 'swr';

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ETS2LA - Euro Truck Simulator 2 Lane Assist",
  description: "",
  icons: ["favicon.ico"],
};

export default function MyApp({ Component, pageProps }: AppProps) {
  const { data, error, isLoading } = useSWR("ip", GetIP, { refreshInterval: 1000 });
  if (isLoading) return <p>Loading...</p>
  if (error) return <p>Error: {error.message}</p>
  let ip = data as string;
  return (
  <>
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
    <ETS2LAMenubar ip={ip} />
    <div className='py-3'>
      <Component {...pageProps} />
    </div>
    <ETS2LACommandMenu ip={ip} />
    <Toaster />
    </ThemeProvider>
  </>
  );
}