import { Textarea } from '@/components/ui/textarea';
import { Avatar } from '@/components/ui/avatar';
import {
  ResizablePanel,
  ResizablePanelGroup,
  ResizableHandle,
} from '@/components/ui/resizable';
import { ScrollArea } from '@/components/ui/scroll-area';

class Message {
  id: number;
  username: string;
  text: string;
  side: 'left' | 'right';
  reference?: number;

  constructor(
    id: number,
    username: string,
    text: string,
    side: 'left' | 'right',
    reference?: number
  ) {
    this.id = id;
    this.username = username;
    this.text = text;
    this.side = side;
    this.reference = reference;
  }
}

const messages = [
  new Message(1, 'Developer', 'Hello! How can I help you?', 'left'),
  new Message(2, 'You', "Hi! The steering won't work in ETS2LA.", 'right'),
  new Message(3, 'Developer', 'Did you do the First Time Setup?', 'left'),
  new Message(4, 'You', 'No, let me try that out.', 'right'),
  new Message(
    5,
    'You',
    'Quis pariatur eiusmod minim mollit quis. Ea dolor aute magna ipsum eu consectetur et labore veniam sunt non. Incididunt do officia eu excepteur enim veniam incididunt.',
    'right'
  ),
  new Message(6, 'You', 'I did it now', 'right', 3),
  new Message(7, 'Developer', 'And is it working now?', 'left', 6),
  new Message(8, 'Developer', 'Also what the crap is this?', 'left', 5),
  new Message(9, 'You', "Yes, it's working now", 'right'),
  new Message(10, 'Developer', 'Ok good!', 'left'),
];

const ChatMessage = ({
  message,
}: {
  message: Message;
}) => {
  const isRight = message.side === 'right';

  const messageContainerClass = `flex ${
    isRight ? 'justify-end' : 'justify-start'
  } font-customSans text-sm pb-4`;

  const messageContentClass = `px-4 py-2 rounded-lg ${
    isRight ? 'rounded-br-none' : 'rounded-bl-none'
  } bg-gray-200 text-black dark:bg-[#303030] dark:text-foreground`;

  return (
    <div className={messageContainerClass}>
      <div
        className={`flex-col gap-1 flex max-w-96 ${
          isRight ? 'items-end' : 'items-start'
        }`}
      >
        <div className={messageContentClass}>
          {message.reference && (
            <div className="mb-2 p-2 border-l-4 border-gray-400 dark:border-gray-600">
              {/* Display the referenced message text */}
              <p className="text-xs text-gray-600 dark:text-gray-300">
                {messages.find((msg) => msg.id === message.reference)?.text}
              </p>
            </div>
          )}
          <p>{message.text}</p>
        </div>
        <p
          className={`text-xs text-muted-foreground ${
            isRight ? 'text-end' : ''
          }`}
        >
          {message.username} {message.reference && 'replied'}
        </p>
      </div>
    </div>
  );
};

export default function Home() {
  return (
    <div className="flex flex-col w-full h-full overflow-auto rounded-t-md justify-center items-center">
      <ResizablePanelGroup direction="horizontal" className="rounded-lg border">
        {/* Left panel content */}
        <ResizablePanel defaultSize={20}>
          <div className="flex flex-col mt-4 h-full w-full space-y-3 overflow-y-auto overflow-x-hidden max-h-full"></div>
        </ResizablePanel>
        <ResizableHandle withHandle />
        {/* Chat area */}
        <ResizablePanel defaultSize={80}>
          <div className="w-full h-full p-4 flex flex-col justify-between">
            <ScrollArea className="p-2 flex flex-col gap-1">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
            </ScrollArea>
            {/* Input area */}
            <Textarea
              className="p-2 border rounded-lg w-full bg-white text-black dark:bg-[#000000] dark:text-foreground"
              placeholder="Type a message..."
            />
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}
