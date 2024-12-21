import flet as ft
from agent_llm import AgentLLM

async def main(page: ft.Page):

    def send_message(e):
        query = chat_input.value
        process(True)
        if len(query) > 0:
            human_chat_message_text = ft.Text(
                expand=True,
                text_align=ft.TextAlign.START,
                selectable=True
            )
            human_chat_message = ft.Row(
                alignment=ft.MainAxisAlignment.START,
                expand=True,
                controls = [
                    ft.CircleAvatar(
                        content=ft.Text("U"),
                    ),
                    ft.ResponsiveRow(
                        alignment=ft.MainAxisAlignment.START,
                        expand=True,
                        controls = [
                            ft.Card(
                                col = min(len(max(query.split("\n"), key=len))/10 + 0.5, 5),
                                content = ft.Container(
                                    expand=True,
                                    alignment=ft.alignment.center_left,
                                    padding=10,
                                    content=human_chat_message_text
                                )   
                            )
                        ]
                    )
                ]
            )
            human_chat_message_text.value = query
            chat.controls.append(human_chat_message)
            chat_input.value = ""
            page.update()
            response = llm_agent.conversation(query)
            on_response(response)
    
    def on_response(response):
        ai_chat_message_text = ft.Text(
            expand=True,
            value=response,
            text_align=ft.TextAlign.START,
            selectable=True
        )
        ai_chat_message = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            expand=True,
            controls = [
                ft.ResponsiveRow(
                    alignment=ft.MainAxisAlignment.END,
                    expand=True,
                    controls = [
                        ft.Card(
                            col = min(len(max(response.split("\n"), key=len))/10 + 0.5, 5),
                            content = ft.Container(
                                expand=True,
                                alignment=ft.alignment.center_right,
                                padding=10,
                                content=ai_chat_message_text
                            )
                        )
                    ]
                ),
                ft.CircleAvatar(
                    content=ft.Text("AI"),
                    )
            ]
        )
        chat.controls.append(ai_chat_message)
        process(False)
        page.update()
    
    def get_file_path(e):
        if e.files:
            file_path = e.files[0].path.replace("\\", "/")
            process(True)
            page.update()
            llm_agent.RAG(file_path)
            update_filename(e.files[0].name)
    
    def update_filename(filename):
        process(False)
        upload_button.text = filename
        page.update()
    
    def change_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            e.control.icon = ft.cupertino_icons.MOON_FILL
        elif page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            e.control.icon = ft.cupertino_icons.SUN_MIN_FILL
        page.update()
    
    def clear_chat(e):
        chat.controls.clear()
        page.update()
    
    def clear_upload(e):
        llm_agent.RAG()
        upload_button.text = "Upload file"
        page.update()
    
    def process(hide):
        if hide:
            process_indicator.visible = True
            chat_input.disabled = True
            send_button.disabled = True
            upload_button.disabled = True
            clear_upload_button.disabled = True
        else:
            process_indicator.visible = False
            chat_input.disabled = False
            send_button.disabled = False
            upload_button.disabled = False
            clear_upload_button.disabled = False

    page.appbar = ft.CupertinoAppBar(
        bgcolor=ft.colors.SURFACE_VARIANT,
        padding=-10,
        leading=ft.CupertinoButton(icon=ft.cupertino_icons.SUN_MIN_FILL, on_click=change_theme),
        middle=ft.Text("Agent LLM"),
        trailing=ft.CupertinoButton(icon=ft.cupertino_icons.REFRESH_BOLD, on_click=clear_chat)
    )
    chat = ft.ListView(
        expand=True,
        auto_scroll=True,
        padding=20,
        spacing=10,
    )
    chat_input = ft.CupertinoTextField(
        col = {"xs": 6, "sm": 8, "md": 10},
        height=75,
        multiline=True,
        shift_enter=True,
        placeholder_text="Type your query",
        on_submit=send_message
    )
    file_dialog = ft.FilePicker(on_result=get_file_path)
    upload_button = ft.CupertinoButton(
        icon=ft.cupertino_icons.UPLOAD_CIRCLE,
        text="Upload file",
        on_click=lambda _:file_dialog.pick_files(
            allowed_extensions=["pdf", "jpg", "png", "jpeg", "svg", "tif"],
            allow_multiple=False
        )
    )
    clear_upload_button = ft.CupertinoButton(
        icon = ft.cupertino_icons.CLEAR_THICK,
        on_click=clear_upload
    )
    send_button = ft.CupertinoFilledButton(
        col = {"xs": 6, "sm": 4, "md": 2},
        text="Send",
        on_click=send_message
    )
    input_area = ft.ResponsiveRow(
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            chat_input,
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    upload_button,
                    clear_upload_button,
                ]
            ),
            send_button
        ]
    )
    chat_area = ft.Container(
        expand=True,
        content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls = [
                chat
            ]
        )
    )
    process_indicator = ft.ProgressBar(visible=False)
    llm_agent = AgentLLM()
    llm_agent.RAG()
    page.title = "AgentLLM"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.overlay.append(file_dialog)
    page.add(process_indicator)
    page.add(chat_area)
    page.add(input_area)

ft.app(port = 8001, target = main, host="0.0.0.0", route_url_strategy = "hash", assets_dir = "assets", view=ft.AppView.WEB_BROWSER)