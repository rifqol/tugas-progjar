import flet as ft
from chat_cli import ChatClient  # pastikan chat_client.py berada di direktori yang sama atau diatur dalam PYTHONPATH

class AuthPage:
    def __init__(self, page, navigate_to_main):
        self.page = page
        self.navigate_to_main = navigate_to_main
        self.chat_client = None
        self.token = ""
        
        self.create_ui()
        
    def create_ui(self):
        self.server_ip = ft.TextField(label="Server IP", value="127.0.0.1")
        self.server_port = ft.TextField(label="Server Port", value="8000")
        self.username = ft.TextField(label="Username")
        self.password = ft.TextField(label="Password", password=True)
        self.connect_button = ft.ElevatedButton("Connect", on_click=self.connect)
        self.login_button = ft.ElevatedButton("Login", on_click=self.login)
        self.output = ft.Text()
        
        self.page.add(
            ft.Column([
                self.server_ip,
                self.server_port,
                self.username,
                self.password,
                self.connect_button,
                self.login_button,
                self.output
            ])
        )
        
    def connect(self, e):
        try:
            server_ip = self.server_ip.value
            server_port = int(self.server_port.value)
            self.chat_client = ChatClient(server_ip, server_port)
            self.output.value = f"Connected to server {server_ip}:{server_port}"
            self.page.update()
        except Exception as ex:
            self.output.value = f"Error connecting to server: {str(ex)}"
            self.page.update()
            
    def login(self, e):
        if not self.chat_client:
            self.output.value = "Not connected to server."
            self.page.update()
            return
            
        username = self.username.value
        password = self.password.value
        result = self.chat_client.login(username, password)
        self.output.value = result
        self.token = self.chat_client.tokenid
        
        if self.token:
            self.navigate_to_main(self.chat_client)
        self.page.update()


class ChoosePage:
    def __init__(self, page, chat_client):
        self.page = page
        self.chat_client = chat_client
        self.create_ui()
    
    def create_ui(self):
        self.private = ft.ElevatedButton("Private Chat", on_click=self.private_chat)
        self.group = ft.ElevatedButton("Group Chat", on_click=self.group_chat)

        self.page.add(
            ft.Column([
                self.private,
                self.group
            ])
        )
    def private_chat(self, e):
        self.page.controls.clear()
        PrivatePage(self.page, self.chat_client)

    def group_chat(self, e):
        self.page.controls.clear()
        GrupPage(self.page, self.chat_client)


class GrupPage:
    def __init__(self, page, chat_client):
        self.page = page
        self.chat_client = chat_client
        self.selected_file_path = ""
        self.create_ui()
    
    def create_ui(self):
        self.message = ft.TextField(label="Message")
        self.grupname = ft.TextField(label="Group Name")
        self.addgroup = ft.ElevatedButton("Add Group", on_click=self.add_group)
        self.passgroup = ft.TextField(label="Password Group")
        self.join_group = ft.ElevatedButton("Join Group", on_click=self.join_group)
        self.inbox_grup = ft.ElevatedButton("Check Inbox Group", on_click=self.check_inbox_group)
        self.send_grup = ft.ElevatedButton("Send Message Group", on_click=self.send_message_group)
        self.file_picker = ft.FilePicker(on_result=self.file_selected)
        self.file_button = ft.ElevatedButton("Pick File", on_click=lambda _: self.file_picker.pick_files(allow_multiple=False))
        self.send_file_button = ft.ElevatedButton("Send File", on_click=self.send_file)
        self.selected_file_text = ft.Text()  
        self.id_file = ft.TextField(label="ID File")
        self.filename = ft.TextField(label="File Name")
        self.downloadfile = ft.ElevatedButton("Download File", on_click=self.download_file)
        self.output = ft.Text()

        self.page.add(
            ft.Column([
                self.message,
                self.grupname,
                self.addgroup,
                self.passgroup,
                self.join_group,
                self.inbox_grup,
                self.send_grup,
                self.file_picker,
                self.file_button,
                self.send_file_button,
                self.selected_file_text,
                self.id_file,
                self.filename,
                self.downloadfile,
                self.output
            ])
        )

    def send_message_group(self, e):
        if not self.chat_client:
            self.output.value = "Not connected to server."
            self.page.update()
            return
            
        groupname = self.grupname.value
        message = self.message.value
        result = self.chat_client.sendgroup(groupname, message)
        self.output.value = result
        self.page.update()
    
    def check_inbox_group(self, e):
        if not self.chat_client:
            self.output.value = "Not connected to server."
            self.page.update()
            return
            
        groupname = self.grupname.value
        result = self.chat_client.inboxgroup(groupname)
        self.output.value = result
        self.page.update()

    def join_group(self, e):
        if not self.chat_client:
            self.output.value = "Not connected to server."
            self.page.update()
            return
            
        groupname = self.grupname.value
        password = self.passgroup.value
        result = self.chat_client.joingroup(groupname, password)
        self.output.value = result
        self.page.update()

    def add_group(self, e):
        if not self.chat_client:
            self.output.value = "Not connected to server."
            self.page.update()
            return
            
        groupname = self.grupname.value
        password = self.passgroup.value
        result = self.chat_client.addgroup(groupname, password)
        self.output.value = result
        self.page.update()

    def download_file(self, e):
        if not self.chat_client:
            self.output.value = "Not connected to server."
            self.page.update()
            return

        grupname = self.grupname.value
        id_file = self.id_file.value
        filename = self.filename.value
        result = self.chat_client.downloadgroupfile(grupname,id_file,filename,".")
        self.output.value = result
        self.page.update()

    def file_selected(self, e):
        if e.files:
            self.selected_file_path = e.files[0].path
            self.selected_file_text.value = f"Selected file: {e.files[0].name}"
        else:
            self.selected_file_path = ""
            self.selected_file_text.value = "No file selected"
        self.page.update()

    def send_file(self, e):
        if not self.chat_client:
            self.output.value = "Not connected to server."
            self.page.update()
            return

        if not self.selected_file_path:
            self.output.value = "No file selected."
            self.page.update()
            return

        recipient = self.grupname.value
        try:
            with open(self.selected_file_path, 'rb') as f:
                file_data = f.read()
            result = self.chat_client.sendgroupfile(recipient, self.selected_file_path)
            self.output.value = result
        except Exception as ex:
            self.output.value = f"Error sending file: {str(ex)}"
        self.page.update()

class PrivatePage:
    def __init__(self, page, chat_client):
        self.page = page
        self.chat_client = chat_client
        self.selected_file_path = ""
        self.create_ui()

        
    def create_ui(self):
        self.message = ft.TextField(label="Message")
        self.recipient = ft.TextField(label="Recipient")
        self.send_button = ft.ElevatedButton("Send Message", on_click=self.send_message)
        self.inbox_button = ft.ElevatedButton("Check Inbox", on_click=self.check_inbox)
        self.file_picker = ft.FilePicker(on_result=self.file_selected)
        self.file_button = ft.ElevatedButton("Pick File", on_click=lambda _: self.file_picker.pick_files(allow_multiple=False))
        self.send_file_button = ft.ElevatedButton("Send File", on_click=self.send_file)
        self.selected_file_text = ft.Text()  
        self.id_file = ft.TextField(label="ID File")
        self.filename = ft.TextField(label="File Name")
        self.downloadfile = ft.ElevatedButton("Download File", on_click=self.download_file)
        self.output = ft.Text()
        
        self.page.add(
            ft.Column([
                self.message,
                self.recipient,
                self.send_button,
                self.inbox_button,
                self.file_picker,
                self.file_button,
                self.send_file_button,
                self.selected_file_text,
                self.id_file,
                self.filename,
                self.downloadfile,
                self.output
            ])
        )

    def download_file(self, e):
        if not self.chat_client:
            self.output.value = "Not connected to server."
            self.page.update()
            return

        id_file = self.id_file.value
        filename = self.filename.value
        result = self.chat_client.downloadfile(id_file,filename,".")
        self.output.value = result
        self.page.update()

    def file_selected(self, e):
        if e.files:
            self.selected_file_path = e.files[0].path
            self.selected_file_text.value = f"Selected file: {e.files[0].name}"
        else:
            self.selected_file_path = ""
            self.selected_file_text.value = "No file selected"
        self.page.update()

    def send_file(self, e):
        if not self.chat_client:
            self.output.value = "Not connected to server."
            self.page.update()
            return

        if not self.selected_file_path:
            self.output.value = "No file selected."
            self.page.update()
            return

        recipient = self.recipient.value
        try:
            with open(self.selected_file_path, 'rb') as f:
                file_data = f.read()
            result = self.chat_client.sendfile(recipient, self.selected_file_path)
            self.output.value = result
        except Exception as ex:
            self.output.value = f"Error sending file: {str(ex)}"
        self.page.update()

    def send_message(self, e):
        if not self.chat_client:
            self.output.value = "Not connected to server."
            self.page.update()
            return
            
        recipient = self.recipient.value
        message = self.message.value
        result = self.chat_client.sendmessage(recipient, message)
        self.output.value = result
        self.page.update()
        
    def check_inbox(self, e):
        if not self.chat_client:
            self.output.value = "Not connected to server."
            self.page.update()
            return
            
        result = self.chat_client.inbox()
        self.output.value = result
        self.page.update()

def main(page: ft.Page):
    def navigate_to_main(chat_client):
        page.controls.clear()  # Clear the current UI
        ChoosePage(page, chat_client)  # Load the main page      
    AuthPage(page, navigate_to_main)  # Load the auth page first
    
ft.app(target=main)