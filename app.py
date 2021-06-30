import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class TextEditor(tk.Tk):
    """
    A text editor allows users to edit multiple files at the same time.
    """

    def __init__(self, text_contents=None):
        super().__init__()

        # track text contents in each tab using dictionary
        if not text_contents:
            self.text_contents = {}
        else:
            self.text_contents = text_contents

        self.title('Text Editor')

        # Prevent menu from tearing off and becoming floating
        self.option_add('*tearOff', False)

        # Create main frame
        self.main = ttk.Frame(self)
        self.main.pack(side='top', fill='both', expand=True, padx=3, pady=3)

        # Create Notebook
        self.notebook = ttk.Notebook(self.main)
        self.notebook.pack(fill='both', expand=True)

        # Create menubar
        self.menubar = tk.Menu()
        self.config(menu=self.menubar)

        # Create menu options
        self.file_menu = tk.Menu(self.menubar)
        self.help_menu = tk.Menu(self.menubar)

        self.menubar.add_cascade(menu=self.file_menu, label='File')
        self.menubar.add_cascade(menu=self.help_menu, label='Help')

        # Add menu labels
        self.file_menu.add_command(
            label='New', command=self.create_file, accelerator='Ctrl+N')
        self.file_menu.add_command(
            label='Open', command=self.open_file, accelerator='Ctrl+O')
        self.file_menu.add_command(
            label='Save', command=self.save_file, accelerator='Ctrl+S')
        self.file_menu.add_command(
            label='Close Tab', command=self.close_current_tab, accelerator='Ctrl+Q')
        self.file_menu.add_command(label='Exit', command=self.confirm_quit)
        self.help_menu.add_command(label='About', command=self.show_about_info)

        # Bind events
        self.bind('<KeyPress>', lambda e: self.check_for_changes())
        self.bind('<Control-n>', lambda e: self.create_file())
        self.bind('<Control-o>', lambda e: self.open_file())
        self.bind('<Control-s>', lambda e: self.save_file())
        self.bind('<Control-q>', lambda e: self.close_current_tab())

        # Create first default tab
        self.create_file()

    def create_file(self, content='', title='Untitled'):
        """
        Create a new tab.
        """

        # Create a tab container
        tab_container = ttk.Frame(self.notebook)
        tab_container.pack()

        # Create text area (the left side in tab container)
        text_area = tk.Text(tab_container, font=(
            "Helvetica", 16), highlightthickness=0)  # without focus border

        # Insert previous content
        text_area.insert('end', content)
        text_area.pack(side='left', fill='both', expand=True)
        text_area.focus()

        # Create Scrollbar (the right side in tab container)
        # Set the Scrollbar widget's command option to the text's yview method
        text_scroll = ttk.Scrollbar(
            tab_container, orient='vertical', command=text_area.yview)
        text_scroll.pack(side='right', fill='y')
        # Set the text widget's yscrollcommand option to the Scrollbar's set method.
        text_area['yscrollcommand'] = text_scroll.set

        # Add a tab to the notebook and select the tab container
        self.notebook.add(tab_container, text=title)
        self.notebook.select(tab_container)

        # Compare if the content changed
        self.text_contents[str(text_area)] = hash(
            content)  # e.g., .!frame.!notebook.!frame.!text

    def get_text_area(self):
        """
        Find tab container (child Frame of notebook) and return text_area (child Text of tab container)
        """

        # notebook.select() is to return the current tab container name (string)
        tab_container_name = self.notebook.select()  # e.g., .!frame.!notebook.!frame

        # Find the tab container by name
        tab_container = self.nametowidget(tab_container_name)

        # Index 0 is text_area and index 1 is scrollbar
        text_area = tab_container.winfo_children()[0]

        return text_area

    def is_current_tab_unsaved(self):
        """
        Return True if current tab is unsaved.
        Return False if current tab is saved.
        """
        # Get text content
        text_area = self.get_text_area()
        content = text_area.get('1.0', 'end-1c')

        return hash(content) != self.text_contents[str(text_area)]

    def confirm_close(self):
        """
        Return True for 'Yes' and False for 'No'.
        """
        user_response = messagebox.askyesno(
            title='Unsaved Changes', icon='question', message='You have unsaved changes. Are you sure you want to close?')

        return user_response

    def close_current_tab(self):
        """
        Close the current tab.
        """
        tab_container_name = self.notebook.select()

        # If the current tab is unsaved and the user does not confirm to close, do nothing.
        if self.is_current_tab_unsaved() and not self.confirm_close():
            return None

        # Close the tab if the current tab is unsaved and the user confirm to close
        # Close the tab if the current tab is saved
        self.notebook.forget(tab_container_name)
        if len(self.notebook.tabs()) == 0:
            self.create_file()

    def check_for_changes(self):
        """
        Check file changes whenever a key is pressed
        """
        text_area = self.get_text_area()
        content = text_area.get('1.0', 'end-1c')

        # Get info of current tab info {'padding': [0], 'sticky': 'nsew', 'text': 'Untitled',... }
        tab_info = self.notebook.tab('current')
        tab_label = tab_info['text']

        if hash(content) != self.text_contents[str(text_area)]:
            if tab_label[-1] != '*':
                self.notebook.tab('current', text=tab_label + '*')
        else:
            if tab_label[-1] == '*':
                self.notebook.tab('current', text=tab_label[:-1])

    def save_file(self):
        """
        Save current file.
        """
        file_path = filedialog.asksaveasfilename(defaultextension='.txt')

        try:
            filename = os.path.basename(file_path)
            text_area = self.get_text_area()
            content = text_area.get('1.0', 'end-1c')

            # Write content in the file
            with open(file_path, 'w') as file:
                file.write(content)

        except (AttributeError, FileNotFoundError):
            print('Save Operation Cancelled.')
            return None

        # Change the current tab label
        self.notebook.tab('current', text=filename)

        # Update text contents
        self.text_contents[str(text_area)] = hash(content)

    def open_file(self):
        """
        Open an existing file.
        """
        file_path = filedialog.askopenfilename()

        try:
            # read the file content
            filename = os.path.basename(file_path)
            with open(file_path, 'r') as file:
                content = file.read()

        except (AttributeError, FileNotFoundError):
            print('Open Operation Cancelled.')
            return None

        self.create_file(content, filename)

    def confirm_quit(self):
        """
        Quit the text editor.
        """
        unsaved = False

        # Check if all the tabs are saved
        for tab_container_name in self.notebook.tabs():
            tab_container = self.nametowidget(tab_container_name)
            text_area = tab_container.winfo_children()[0]
            content = text_area.get('1.0', 'end-1c')

            # If any tab is not saved then breaks
            if hash(content) != self.text_contents[str(text_area)]:
                unsaved = True
                break

        # Confirm close when there is a unsaved file
        if unsaved and not self.confirm_close():
            return None

        self.destroy()

    def show_about_info(self):
        """
        Show About information.
        """
        messagebox.showinfo(
            title='About', message='This is a text editor created by Tkinter')


if __name__ == "__main__":
    editor = TextEditor()
    editor.mainloop()
