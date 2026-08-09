declare module '*.svelte' {
  import type { Component } from 'svelte';
  const component: Component;
  export default component;
}

interface External {
  sendMessage(message: string): void;
  receiveMessage(callback: (message: string) => void): void;
}