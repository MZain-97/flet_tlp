import flet as ft
import pandas as pd
import time  # To simulate file upload progress


class CSVApp:
    def __init__(self):
        self.data = None

    def main(self, page: ft.Page):
        page.title = "CSV Viewer & Search"
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.padding = 20
        page.scroll = ft.ScrollMode.AUTO

        # Helper method to display SnackBar
        def show_snackbar(message, color=ft.colors.BLACK):
            snackbar = ft.SnackBar(ft.Text(message, color=color))
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()

        self.show_snackbar = lambda message, color=ft.colors.BLACK: show_snackbar(message, color)

        # Helper method to display Banner (notification)
        def show_notification(message, color=ft.colors.GREEN):
            banner = ft.Banner(
                leading=ft.Icon(ft.icons.CHECK_CIRCLE, color=color, size=40),
                content=ft.Text(message),
                actions=[
                    ft.TextButton(
                        "Close",
                        on_click=lambda _: (page.overlay.remove(banner), page.update()),
                    )
                ],
                bgcolor=ft.colors.LIGHT_GREEN_50,
            )
            page.overlay.append(banner)
            page.update()

        self.show_notification = lambda message, color=ft.colors.GREEN: show_notification(message, color)

        # Header
        title = ft.Text(
            "CSV Viewer & Search",
            size=30,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLUE_600,
        )

        # File Picker
        self.file_picker = ft.FilePicker(on_result=self.upload_file)
        page.overlay.append(self.file_picker)

        file_upload_button = ft.ElevatedButton(
            "Upload CSV",
            icon=ft.icons.UPLOAD_FILE,
            on_click=lambda e: self.file_picker.pick_files(allow_multiple=False),
        )

        # Delete File Button
        self.delete_file_button = ft.ElevatedButton(
            "Delete File",
            icon=ft.icons.DELETE,
            on_click=self.delete_file,
            disabled=True,  # Initially disabled
        )

        # Progress Bar
        self.progress_bar = ft.ProgressBar(width=400, visible=False)

        # Search Bar
        self.search_query = ft.TextField(
            label="Enter search query",
            hint_text="Search for text in your CSV data...",
            width=400,
        )

        search_button = ft.ElevatedButton(
            "Search", icon=ft.icons.SEARCH, on_click=self.perform_search
        )

        # Results Display
        self.results_container = ft.Column(scroll=ft.ScrollMode.AUTO)

        # Layout Organization
        page.add(
            title,
            file_upload_button,
            self.delete_file_button,
            self.progress_bar,
            self.search_query,
            search_button,
            self.results_container,
        )

    def upload_file(self, e: ft.FilePickerResultEvent):
        """
        Handle CSV file upload.
        """
        if not e.files:
            self.show_snackbar("No file selected.", color=ft.colors.RED)
            return

        file_path = e.files[0].path

        # Validate file extension
        if not file_path.endswith(".csv"):
            self.show_snackbar("Invalid file type. Please upload a CSV file.", color=ft.colors.RED)
            return

        # Simulate file upload progress
        self.progress_bar.visible = True
        self.progress_bar.value = 0
        self.progress_bar.update()

        for i in range(0, 101, 10):  # Simulate progress
            time.sleep(0.1)
            self.progress_bar.value = i / 100
            self.progress_bar.update()

        self.progress_bar.visible = False

        try:
            self.data = pd.read_csv(file_path)
            self.show_notification("File uploaded and loaded successfully!", color=ft.colors.GREEN)
            self.delete_file_button.disabled = False  # Enable delete button
            self.delete_file_button.update()
        except Exception as error:
            self.show_snackbar(f"Error loading CSV: {error}", color=ft.colors.RED)

    def delete_file(self, e):
        """
        Delete the currently uploaded file and clear the UI.
        """
        if self.data is None:
            self.show_snackbar("No file to delete!", color=ft.colors.RED)
            return

        # Clear the data and reset the UI
        self.data = None
        self.results_container.controls.clear()
        self.results_container.update()

        self.delete_file_button.disabled = True  # Disable delete button
        self.delete_file_button.update()

        self.search_query.value = ""
        self.search_query.update()

        self.show_notification("File removed successfully!", color=ft.colors.ORANGE)

    def perform_search(self, e):
        """
        Perform search operation on the loaded data.
        """
        if self.data is None:
            self.show_snackbar("Please upload a CSV file first!", color=ft.colors.RED)
            return

        query = self.search_query.value.strip()
        if not query:
            self.show_snackbar("Search query cannot be empty!", color=ft.colors.RED)
            return

        try:
            results = self.data[
                self.data.apply(
                    lambda row: row.astype(str).str.contains(query, case=False).any(),
                    axis=1,
                )
            ]

            # Clear previous results
            self.results_container.controls.clear()

            if results.empty:
                self.results_container.controls.append(
                    ft.Text("No results found!", size=16, color=ft.colors.RED)
                )
            else:
                for _, row in results.iterrows():
                    # Create formatted content for each row
                    result_texts = [
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f"{col}: ",
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.BLUE_600,
                                ),
                                ft.Text(str(val)),
                            ]
                        )
                        for col, val in row.items()
                    ]

                    # Wrap each row in a Card
                    self.results_container.controls.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column(result_texts, spacing=5),
                                padding=10,
                                bgcolor=ft.colors.LIGHT_GREEN_50,
                                border_radius=ft.border_radius.all(5),
                                margin=5,
                                width=500,
                            )
                        )
                    )

            # Update the UI
            self.results_container.update()
        except Exception as error:
            self.show_snackbar(f"Error during search: {error}", color=ft.colors.RED)


# Run the Flet app
if __name__ == "__main__":
    app = CSVApp()
    ft.app(target=app.main)
