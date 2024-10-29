import Document, { Html, Head, Main, NextScript } from 'next/document';
import { GeistSans } from 'geist/font/sans';
import { GeistMono } from 'geist/font/mono';

class MyDocument extends Document {
    render() {
        return (
            <Html lang="en" className={`${GeistSans.variable} ${GeistMono.variable}`}>
                <Head>
                    
                </Head>
                <body>
                    <Main />
                    <NextScript />
                </body>
            </Html>
        );
    }
}

export default MyDocument;