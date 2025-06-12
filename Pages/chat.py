from ETS2LA.Networking.cloud import GetUsername, GetCredentials
from ETS2LA.UI.utils import SendPopup
from ETS2LA.UI import *

from typing import TypedDict, Optional
import websockets
import logging
import asyncio
import json

# Constants
UUID = GetCredentials()[0]
USERNAME = GetUsername()
WS_URL = f"ws://localhost:8001/ws/client/{UUID}"

class MessageDict(TypedDict):
    id: int
    user: str
    text: str
    reply: Optional[int]

class EventDict(TypedDict):
    event: str

class ConversationDict(TypedDict):
    id: int
    name: str
    members: list[str]
    messages: list[MessageDict | EventDict]
    tags: list[str]

class Events:
    @staticmethod
    def Create(user: str) -> EventDict:
        return {"event": f"{user} started a new conversation"}

    @staticmethod
    def Join(user: str) -> EventDict:
        return {"event": f"{user} joined the conversation"}

    @staticmethod
    def AddTags(user: str, tags: list[str]) -> EventDict:
        return {"event": f"{user} added the following tag(s): {', '.join(tags)}"}

    @staticmethod
    def RemoveTags(user: str, tags: list[str]) -> EventDict:
        return {"event": f"{user} removed the following tag(s): {', '.join(tags)}"}

    @staticmethod
    def ChangeName(user: str, name: str) -> EventDict:
        return {"event": f"{user} changed the conversation name to {name}"}

    @staticmethod
    def Fixing(user: str) -> EventDict:
        return {"event": f"{user} is fixing the issue"}

    @staticmethod
    def Close(user: str) -> EventDict:
        return {"event": f"{user} closed the conversation"}

    @staticmethod
    def Reopen(user: str) -> EventDict:
        return {"event": f"{user} reopened the conversation"}

    @staticmethod
    def Message(id: int, user: str, message: str, reply: Optional[int] = None) -> dict[str, MessageDict]:
        return {"message": {"id": id, "user": user, "text": message, "reply": reply}}

def Conversation(id: str, name: str, members: list[str], messages: list[MessageDict | EventDict], tags: list[str]) -> ConversationDict:
    return {"id": id, "name": name, "members": members, "messages": messages, "tags": tags}

# 2 example conversations as placeholders before the backend is implemented
conv1_messages : list[MessageDict | EventDict] = [
    Events.Create(USERNAME),
    Events.Join("Developer"),
    Events.Message(0, "Developer", "Hello! How can I help you?"),
    Events.Message(1, USERNAME, "Hi! The steering won't work in ETS2LA."),
    Events.Message(2, "Developer", "Did you do the First Time Setup?"),
    Events.Message(3, USERNAME, "No, let me try that out."),
    Events.Message(4, USERNAME, "I did it now"),
    Events.Message(5, "Developer", "And is it working now?", 4),
    Events.Message(6, USERNAME, "Yes, it's working now"),
    Events.Message(7, "Developer", "Ok good!"),
    Events.Message(8, "Developer", "Have a nice day!"),
    Events.Message(9, USERNAME, "Goodbye!", 8),
    Events.Close(USERNAME)
]
conv2_messages : list[MessageDict | EventDict] = [
    Events.Create(USERNAME),
    Events.Message(0, USERNAME, "Hello! I would like to suggest you a feature. Would it be possible to make a button that would allow us to upload images to this support chat?"),
    Events.Message(1, "Developer", "Great suggestion!"),
    Events.Message(2, "Developer", "I'll get to work on adding this."),
    Events.Fixing("Developer"),
    Events.Message(3, USERNAME, "Any updates?"),
    Events.Message(4, "Developer", "Almost done!"),
    Events.Message(5, USERNAME, "Nice!"),
]

class Page(ETS2LAPage):
    url = "/chat"

    conversation_index = -1
    conversations : list[ConversationDict] = [
        #Conversation(0, "Broken Steering", [USERNAME, "Developer"], conv1_messages, ["Closed", "Question"]),
        #Conversation(1, "Uploading Images", [USERNAME, "Developer"], conv2_messages, ["Open", "Suggestion"])
    ]
    textbox_text : str = ""
    replying_to: Optional[int] = None
    # If ws is None, a connection is being attempted
    # If ws is False, the connection has been closed or the connection failed
    # If ws is not None or False, the connection is open as a WebsocketClientProtocol
    ws : Optional[websockets.WebSocketClientProtocol] = None

    def open_event(self):
        asyncio.create_task(self.ws_loop())

    def close_event(self):
        if self.ws:
            asyncio.create_task(self.ws.close())

    def handle_message(self, msg: dict):
        if "event" in msg:
            return
        if "message" in msg:
            message = msg["message"]
            # Current conversations messages
            messages_to_append = self.conversations[self.conversation_index]["messages"]
            if message:
                messages_to_append.append(
                    Events.Message(len(messages_to_append), message["user"], message["text"], message["reply"])
                )

    async def ws_loop(self):
        self.ws = None
        try:
            async with websockets.connect(WS_URL) as self.ws:
                while True:
                    msg = await self.ws.recv()
                    print(f"Received support chat message: {msg}")
                    self.handle_message(msg)
        except websockets.ConnectionClosed or websockets.ConnectionClosedOK or websockets.ConnectionClosedError or websockets.Conne:
            logging.warning("The ETS2LA chat support servers closed the connection.")
            self.ws = False
        except ConnectionRefusedError:
            logging.warning("A connection could not be made with the ETS2LA chat support servers.")
            self.ws = False

    def NewConversation(self):
        self.conversations.append(Conversation(len(self.conversations), "New Conversation", [USERNAME], [], ["Open"]))
        self.conversations[-1]["messages"].append(Events.Create(USERNAME))
        self.conversation_index = len(self.conversations) - 1

    def SendMessage(self):
        message = self.textbox_text.strip()
        # Current conversations messages
        messages_to_append = self.conversations[self.conversation_index]["messages"]
        if message:
            messages_to_append.append(
                Events.Message(len(messages_to_append), USERNAME, message, self.replying_to)
            )

            asyncio.create_task(self.ws.send(json.dumps({"message" : {
                "text": message,
                "user": USERNAME,
                "reply": self.replying_to
            }})))

        self.textbox_text = ""
        self.replying_to = None

    def ChatEvent(self, event: EventDict):
        event = event["event"]
        with Container(styles.Classname("flex items-center w-full justify-center pb-4")):
            with Container(styles.Classname("flex-1 h-px border-b mx-2")):
                pass
            Text(event, styles.Classname("text-xs whitespace-nowrap text-muted-foreground"))
            with Container(styles.Classname("flex-1 h-px border-b mx-2")):
                pass

    def SelectConversation(self, id: str):
        '''`id` is passed by the button callback'''
        self.conversation_index = int(id)
    
    def Reply(self, id: str):
        '''`id` is passed by the button callback'''
        self.replying_to = int(id)
    
    def StopReply(self):
        self.replying_to = None

    def SetTextboxText(self, text: str):
        '''`text` is passed by the textarea `changed` callback'''
        self.textbox_text = text

    def ChatMessage(self, messages: list[MessageDict | EventDict], index : int):
        message : MessageDict = messages[index]["message"]
        is_right = message["user"] == USERNAME
        if index + 2 <= len(messages): # len is 1-indexed, so add 2 to the index instead of just 1
            if "event" in messages[index + 1]:
                is_same_next = False
            else:
                is_same_next = messages[index + 1]["message"]["user"] == message["user"]
        else:
            is_same_next = False

        rounded_message_box = "rounded-br-none" if is_right else "rounded-bl-none" if not is_same_next else ""
        message_container_class = f"flex gap-1 {'justify-end' if is_right else 'justify-start'} text-sm {'pb-2' if is_same_next else 'pb-4'} group"
        message_content_class = f"flex flex-col gap-1 max-w-96 p-3 rounded-lg relative group {rounded_message_box} bg-input/30 border shadow-sm" 
        message_reply = messages[message["reply"]]["message"]["text"] if message["reply"] else None

        with Container(styles.Classname(message_container_class)):
            with Container(styles.Classname(f"flex flex-col gap-1 {'items-end' if is_right else 'items-start'}")):
                with Container(styles.Classname("flex gap-1")):
                    if is_right:
                        with Button(self.Reply, str(message["id"]), "secondary", styles.Classname("hidden group-hover:block text-xs p-1 bg-transparent border-none")):
                            Icon("reply", styles.Classname("w-4 h-4"))
                    
                    with Container(styles.Classname(message_content_class)):
                        if message_reply:
                            with Container(styles.Classname("p-2 border-l-4 border-gray-400 dark:border-gray-600")):
                                Text(message_reply, styles.Classname("text-xs text-gray-600 dark:text-gray-300"))
                        Text(message["text"])

                    if not is_right:
                        with Button(self.Reply, str(message["id"]), "outline", styles.Classname("hidden group-hover:block text-xs p-1 bg-transparent border-none")):
                            Icon("reply", styles.Classname("w-4 h-4"))
                
                if not is_same_next:
                    Text(f"{message['user']} {'replied' if message_reply else ''}", styles.Classname(f"text-xs text-muted-foreground {'text-end' if is_right else ''}"))
        
    def render(self):
        with Container(styles.Classname("flex w-full h-max") + styles.Padding("12px")):
            if self.ws: # The websocket is connected
                with Container(styles.Classname("flex flex-col") + styles.Width("275px") + styles.Gap("8px")):
                    with Button(self.NewConversation, type="secondary", style=styles.Classname("justify-start w-full shadow-md")):
                        Text("New Conversation", styles.Classname("text-sm"))

                    Separator()
                    if self.conversations: # If there are conversations
                        for conversation in self.conversations:
                            conv_id = conversation["id"]
                            with TooltipContent(f"tags-{conv_id}"):
                                with Container(styles.Classname("flex text-start rounded-lg") + styles.Gap("8px")):
                                    for tag in conversation["tags"]:
                                        with Badge():
                                            Text(tag, styles.Classname("text-xs"))

                            with Tooltip(f"tags-{conv_id}"):
                                with Button(self.SelectConversation, str(conv_id), "secondary" if self.conversation_index == conv_id else "ghost", styles.Classname(f"justify-start w-full {'shadow-md' if self.conversation_index == conv_id else ''}")):
                                    Text(conversation["name"], styles.Classname("text-sm"))
                    else: # If there are no conversations
                        Text("No conversations", styles.Classname("text-sm text-muted-foreground text-center"))
                
                # "0px 12px" in CSS means "mx-[12px]" in Tailwind
                Separator(styles.Margin("0px 12px"), "vertical")

                if self.conversation_index >= 0: # If there is a conversation selected
                    with Container(styles.Classname("flex flex-col h-max w-full gap-1 p-2")):
                        with Container(styles.Classname("flex flex-col flex-grow w-full h-full") + styles.Style(overflow_y="auto", height="82vh")):
                            Space(styles.Height("12px"))
                            for i, message in enumerate(self.conversations[self.conversation_index]["messages"]):
                                if "message" in message: # Render a message
                                    self.ChatMessage(self.conversations[self.conversation_index]["messages"], i)
                                elif "event" in message: # Render an event
                                    self.ChatEvent(message)
                            
                            Space(styles.Height("12px"))

                        with Container(styles.Classname("relative w-full")):
                            if self.replying_to:
                                current_messages = self.conversations[self.conversation_index]["messages"]
                                for message in current_messages:
                                    if "message" not in message: continue # Skip events
                                    if message["message"]["id"] == self.replying_to:
                                        replying_to_message = message["message"]
                                
                                if not replying_to_message: return
                                replying_to_user = replying_to_message["user"]
                                replying_to_text = replying_to_message["text"]

                                with Container(styles.Classname("absolute p-2 rounded-md flex justify-between items-center border bg-background w-[calc(100%-101px)] top-[-80%] left-0 h-[60%]")):
                                    Text(f"Replying to {replying_to_user}: {replying_to_text}", styles.Classname("text-xs"))
                                    with Button(self.StopReply, type="ghost", style=styles.Classname("-mx-2")):
                                        Text("X")

                            with Container(styles.Classname("relative z-10 flex flex-row")):
                                TextArea("Type something...", self.SetTextboxText, style=styles.Classname("border rounded-lg w-full resize-none h-14 bg-background text-white"))
                                with Button(self.SendMessage, style=styles.Classname("w-1/12 h-15 ml-2 mr-1")):
                                    Icon("forward", style=styles.Classname("w-6 h-6"))
                else:
                    with Container(styles.Classname("flex flex-col w-full items-center justify-center gap-2 text-center") + styles.Height("94vh")):
                        Text("No support chat selected", styles.Classname("text-md"))
                        Text("Select one from the sidebar or start a new one..", styles.Classname("text-xs text-muted-foreground"))

            elif self.ws == False: # The websocket is not connected
                with Container(styles.Classname("flex flex-col w-full items-center justify-center gap-2 text-center") + styles.Height("94vh")):
                    Text("The webserver for sending and receiving messages is not running!", styles.Classname("text-md"))
                    Text("Please use the Discord support system, make a GitHub issue, or try again later.", styles.Classname("text-xs text-muted-foreground"))
                    with Button(self.open_event, type="outline", style=styles.Margin("12px")):
                        Text("Try again")
            elif self.ws == None: # The websocket is being connected
                with Container(styles.Classname("flex flex-col w-full items-center justify-center gap-2 text-center") + styles.Height("94vh")):
                    with Spinner():
                        Icon("loader-circle", style=styles.Classname("w-6 h-6"))
                    Text("Connecting to the ETS2LA server...", styles.Classname("text-sm text-muted-foreground"))
        return