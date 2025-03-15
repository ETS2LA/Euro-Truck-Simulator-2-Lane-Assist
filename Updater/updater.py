try:
    from textual.app import App, ComposeResult
    from textual.widgets import Header, Log, Label, Static, Button, Footer
except:
    from ETS2LA.Utils.shell import ExecuteCommand
    ExecuteCommand("pip install textual")
    from textual.app import App, ComposeResult
    from textual.widgets import Header, Log, Label, Static, Button, Footer

from importlib.metadata import version 
import asyncio
import time

steps = [
    {"name": "Save", "command": "git stash"},
    {"name": "Update", "command": "git pull"},
    {"name": "Requirements", "command": "pip install -r requirements.txt"},
    {"name": "Clear Cache", "command": 'RMDIR /S /Q "cache"'}
]

class Updater(App):
    CSS_PATH = "updater.tcss"

    def on_mount(self) -> None:
        self.title = "Updating"
        self.sub_title = "Please wait until the process is complete."

    async def on_ready(self) -> None:
        self.icon = "◐"
        self.frame = 0
        self.set_interval(0.25, self.update_icon)
        time.sleep(1)
        await self.run_steps()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon='')

        sidebar = Static(classes="sidebar")
        with sidebar:
            yield Label("--  Progress  --")
            for step in steps:
                yield Label(f"○ {step['name']}", classes="not-done")
            yield Label("")
            yield Button("Retry", id="retry-button", disabled=True)
            yield Button("Exit", id="exit-button", disabled=True)
        
        yield sidebar

        log = Static("Two", classes="box")
        with log:
            yield Log(auto_scroll=True, highlight=True, classes="log")
    
        yield log


    def update_icon(self):
        spinner = ["◐", "◓", "◑", "◒"]
        self.icon = spinner[self.frame % 4]
        self.frame += 1
        self.query_one(Header).icon = self.icon

    async def run_steps(self):
        log_widget = self.query_one(Log)
        for idx, step in enumerate(steps):
            sidebar = self.query_one(Static)
            label = sidebar.children[idx + 1]
            label.classes = ["doing"]

            log_widget.write(f"-- RUNNING {step['name']} --\n")
            process = await asyncio.create_subprocess_shell(
                step['command'],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )

            async def read_stream(stream, callback):
                while True:
                    line = await stream.readline()
                    if line:
                        try:
                            dimmed_line = f"{line.decode()}"
                            callback(dimmed_line)
                        except:
                            pass
                    else:
                        break

            await asyncio.gather(
                read_stream(process.stdout, log_widget.write),
                read_stream(process.stderr, log_widget.write)
            )

            await process.wait()
            return_code = process.returncode
            if return_code != 0 and step['name'] != "Clear Cache":
                log_widget.write(f"-- ERROR in {step['name']} (report this to the developers) --\n\n")
                label.classes = ["error"]
                label.update(f"X {step['name']}") #type: ignore
                
                # Enable Retry and Exit buttons
                retry_button = self.query_one("#retry-button", Button)
                exit_button = self.query_one("#exit-button", Button)
                retry_button.disabled = False
                exit_button.disabled = False

                # Disable further step execution
                self._paused = True
                break
            else:
                log_widget.write(f"-- COMPLETED {step['name']} --\n\n")
                label.classes = ["done"]
                label.update(f"● {step['name']}") #type: ignore

        if not getattr(self, '_paused', False):
            log_widget.write("-- Update complete! --\n")
            self.icon = "✔"
            self.refresh()
            time.sleep(3)
            self.exit()

    async def on_button_pressed(self, event) -> None:
        button = event.button
        if button.id == "retry-button":
            # Disable buttons
            button.disabled = True
            exit_button = self.query_one("#exit-button", Button)
            exit_button.disabled = True

            # Retry the failed step
            await self.run_steps()
        elif button.id == "exit-button":
            self.exit()

if __name__ == "__main__":
    app = Updater()
    app.run()