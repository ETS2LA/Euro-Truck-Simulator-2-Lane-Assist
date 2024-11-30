import localFont from "next/font/local";
import "./globals.css";
import CSRLayout from "./csr_layout";
import { AuthProvider } from "@/apis/auth";

const geistSans = localFont({
    src: "./fonts/GeistVF.woff",
    variable: "--font-geist-sans",
    weight: "100 900",
});
const geistMono = localFont({
    src: "./fonts/GeistMonoVF.woff",
    variable: "--font-geist-mono",
    weight: "100 900",
});

export default function RootLayout({ children, } : Readonly<{ children: React.ReactNode; }>) {
    return (
        <html lang="en">
            <head>
                <meta charSet="UTF-8" />
                <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
                <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                <link rel="icon" href="/favicon.ico" />
            </head>
            <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-sidebarbg overflow-hidden`}>
                <AuthProvider>
                    <CSRLayout>{children}</CSRLayout>
                </AuthProvider>
            </body>
        </html>
    )
}
