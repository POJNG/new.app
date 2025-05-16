import tkinter as tk
from tkinter import messagebox
import json
from PIL import Image, ImageTk

# Show the login screen window and handle login logic.
# Why: This function is the entry point for user authentication, ensuring only logged-in users can access the main app.
def show_login_screen():
    login_window = tk.Tk()
    login_window.title("Login Form")
    login_window.configure(bg="#FF5733")  # Set window color

    # Validate login credentials (accepts any input).
    # Why: For demonstration or testing purposes, any credentials are accepted to simplify access.
    def validate_login():
        messagebox.showinfo("Login Successful", "Welcome!")
        login_window.destroy()
        launch_main_app()

    # Exit the application from the login screen.
    # Why: Allows the user to close the app directly from the login menu.
    def exit_app():
        login_window.destroy()

    # Create a white background frame for the login menu
    menu_frame = tk.Frame(login_window, bg="white", padx=40, pady=40)
    menu_frame.pack(expand=True)

    username_label = tk.Label(menu_frame, text="STUDENT ID:", bg="white", fg="#FF5733", font=("Helvetica", 12))
    username_label.pack(pady=(30, 5))
    username_entry = tk.Entry(menu_frame, font=("Helvetica", 12))
    username_entry.pack(pady=5)
    password_label = tk.Label(menu_frame, text="Password:", bg="white", fg="#FF5733", font=("Helvetica", 12))
    password_label.pack(pady=5)
    password_entry = tk.Entry(menu_frame, show="*", font=("Helvetica", 12))
    password_entry.pack(pady=5)
    login_button = tk.Button(menu_frame, text="Login", command=validate_login, font=("Helvetica", 12), bg="#FF5733", fg="white", padx=20, pady=10)
    login_button.pack(pady=(15, 10))
    exit_button = tk.Button(menu_frame, text="Exit", command=exit_app, font=("Helvetica", 12), bg="#f44336", fg="white", padx=20, pady=10)
    exit_button.pack(pady=(0, 30))
    login_window.mainloop()

# Launch the main Book Tracker application window.
# Why: This function is called after a successful login to start the main app interface.
def launch_main_app():
    root = tk.Tk()
    root.configure(bg="#FF5733")
    app = BookTrackerApp(root)
    root.mainloop()

# Class to manage the book collection and wishlist, including saving/loading from file.
# Why: Encapsulates all book data and file operations, keeping data management separate from the UI logic.
class BookCollection:
    # Initialize the BookCollection, loading data from file.
    # Why: Loads existing data if available, so user data persists between sessions.
    def __init__(self, filename="books.json"):
        self._filename = filename
        self._my_books = []
        self._wishlist = []
        self.load_data()

    @property #<-- keeps the underlying data private
    # Return the list of books in 'My Books'.
    # Why: Provides read-only access to the book list, enforcing encapsulation.
    def my_books(self):
        return self._my_books

    @property
    # Return the list of books in the wishlist.
    # Why: Provides read-only access to the wishlist, enforcing encapsulation.
    def wishlist(self):
        return self._wishlist

    # Save the current book data to the JSON file.
    # Why: Ensures all changes to books and wishlist are persisted for future sessions.
    def save_data(self):
        with open(self._filename, "w") as file:
            json.dump({"my_books": self._my_books, "wishlist": self._wishlist}, file)

    # Load book data from the JSON file.
    # Why: Loads saved data so the user doesn't lose their books or wishlist when restarting the app.
    def load_data(self):
        try:
            with open(self._filename, "r") as file:
                data = json.load(file)
                self._my_books = data.get("my_books", [])
                self._wishlist = data.get("wishlist", [])
        except FileNotFoundError:
            pass

    # Add a book to either 'My Books' or 'Wishlist'.
    # Why: Centralizes logic for adding books, so both UI and other code can use the same method.
    def add_book(self, collection, book):
        if collection == "my_books":
            book["status"] = "To Read"
            self._my_books.append(book)
        elif collection == "wishlist":
            self._wishlist.append(book)
        self.save_data()

    # Delete a book from either 'My Books' or 'Wishlist' by index.
    # Why: Allows removal of books from either collection, keeping the UI and data in sync.
    def delete_book(self, collection, index):
        if collection == "my_books":
            self._my_books.pop(index)
        else:
            self._wishlist.pop(index)
        self.save_data()

# Main application class for the Book Tracker GUI.
# Why: Handles all user interface logic, keeping it separate from data management for clarity and maintainability.
class BookTrackerApp:
    # Initialize the main app window and layout.
    # Why: Sets up the main window and prepares the UI for user interaction.
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.minsize(800, 600)
        self.root.configure(bg="#000000")  # Set window background to black
        self.collection = BookCollection()
        self._resize_after_id = None  # For debouncing resize events
        
        # Load the original background image
        try:
            self.bg_image_original = Image.open("teeee.jpg")
            self.bg_photo = None
            self.bg_label = tk.Label(self.root)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()  # Place it behind other widgets
            self._resize_bg_image()  # Initial resize
        except Exception as e:
            print(f"Error loading background image: {e}")
        
        self.current_widgets = []
        self.root.bind('<Configure>', self._on_resize)  # Bind only once here
        self.show_login_screen()

    def _on_resize(self, event=None):
        if self._resize_after_id:
            self.root.after_cancel(self._resize_after_id)
        self._resize_after_id = self.root.after(100, self._do_resize)

    def _do_resize(self):
        self._resize_bg_image()
        if hasattr(self, '_reposition_login_widgets') and hasattr(self, 'login_widgets') and self.login_widgets:
            self._reposition_login_widgets()
        if hasattr(self, '_reposition_home_widgets') and hasattr(self, 'home_widgets') and self.home_widgets:
            self._reposition_home_widgets()
        if hasattr(self, '_reposition_add_widgets') and hasattr(self, 'add_widgets') and self.add_widgets:
            self._reposition_add_widgets()
        self._resize_after_id = None

    def _resize_bg_image(self, event=None):
        if not hasattr(self, 'bg_image_original'):
            return
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        if w < 2 or h < 2:
            return

        # Calculate the new size preserving aspect ratio and cropping
        img_w, img_h = self.bg_image_original.size
        scale = max(w / img_w, h / img_h)
        new_size = (int(img_w * scale), int(img_h * scale))
        resized = self.bg_image_original.resize(new_size, Image.Resampling.LANCZOS)

        # Crop to fit the window exactly
        left = (resized.width - w) // 2
        top = (resized.height - h) // 2
        right = left + w
        bottom = top + h
        cropped = resized.crop((left, top, right, bottom))

        self.bg_photo = ImageTk.PhotoImage(cropped)
        self.bg_label.config(image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            if widget != self.bg_label:  # Don't destroy the background
                widget.destroy()
        self.current_widgets = []

    # Show the login screen in the main frame
    def show_login_screen(self):
        self.clear_widgets()
        self.login_widgets = []
        
        # Place widgets directly on the background for a cleaner look
        title_label = tk.Label(self.root, text="Login to Cozy Book Tracker", font=("Helvetica", 24, "bold"), fg="#fff", bg="#000000", highlightthickness=2)
        self.login_widgets.append(title_label)
        username_label = tk.Label(self.root, text="STUDENT ID:", fg="#FF5733", font=("Helvetica", 14, "bold"), bg="#000000")
        self.login_widgets.append(username_label)
        username_entry = tk.Entry(self.root, font=("Helvetica", 14), bg="#222", fg="#fff", insertbackground="#fff")
        self.login_widgets.append(username_entry)
        password_label = tk.Label(self.root, text="Password:", fg="#FF5733", font=("Helvetica", 14, "bold"), bg="#000000")
        self.login_widgets.append(password_label)
        password_entry = tk.Entry(self.root, show="*", font=("Helvetica", 14), bg="#222", fg="#fff", insertbackground="#fff")
        self.login_widgets.append(password_entry)
        
        def validate_login():
            messagebox.showinfo("Login Successful", "Welcome!")
            self.show_home()
            
        button_style = {
            "font": ("Helvetica", 14, "bold"),
            "width": 18,
            "height": 1,
            "bd": 3,
            "relief": "raised",
            "highlightthickness": 2
        }
        
        login_button = tk.Button(self.root, text="Login", command=validate_login, bg="#FF5733", fg="white", activebackground="#C63D0F", activeforeground="white", **button_style)
        exit_button = tk.Button(self.root, text="Exit", command=self.root.quit, bg="#f44336", fg="white", activebackground="#b71c1c", activeforeground="white", **button_style)
        
        self.login_widgets.append(login_button)
        self.login_widgets.append(exit_button)
        
        # Place widgets using place for custom layout
        w = self.root.winfo_width() if self.root.winfo_width() > 1 else 800
        h = self.root.winfo_height() if self.root.winfo_height() > 1 else 600
        y = h // 2 - 120
        spacing = 45
        title_label.place(x=w//2, y=y, anchor="center")
        username_label.place(x=w//2, y=y+spacing*1, anchor="center")
        username_entry.place(x=w//2, y=y+spacing*2, anchor="center", width=220)
        password_label.place(x=w//2, y=y+spacing*3, anchor="center")
        password_entry.place(x=w//2, y=y+spacing*4, anchor="center", width=220)
        login_button.place(x=w//2, y=y+spacing*5+10, anchor="center")
        exit_button.place(x=w//2, y=y+spacing*6+10, anchor="center")
        
        self.current_widgets = self.login_widgets
        self.root.update()

    def _reposition_login_widgets(self, event=None):
        if not hasattr(self, 'login_widgets') or not self.login_widgets:
            return
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        y = h // 2 - 120
        spacing = 45
        self.login_widgets[0].place(x=w//2, y=y, anchor="center")
        self.login_widgets[1].place(x=w//2, y=y+spacing*1, anchor="center")
        self.login_widgets[2].place(x=w//2, y=y+spacing*2, anchor="center", width=220)
        self.login_widgets[3].place(x=w//2, y=y+spacing*3, anchor="center")
        self.login_widgets[4].place(x=w//2, y=y+spacing*4, anchor="center", width=220)
        self.login_widgets[5].place(x=w//2, y=y+spacing*5+10, anchor="center")
        self.login_widgets[6].place(x=w//2, y=y+spacing*6+10, anchor="center")

    # Show the home screen with navigation buttons.
    # Why: Provides the main navigation for the app, letting users choose what to do next.
    def show_home(self):
        self.clear_widgets()
        self.home_widgets = []
        
        # Place widgets directly on the background for a cleaner look
        title_label = tk.Label(self.root, text="Welcome to Cozy Book Tracker", font=("Helvetica", 28, "bold"), fg="#fff", bg="#000000", highlightthickness=2)
        self.home_widgets.append(title_label)
        button_style = {
            "font": ("Helvetica", 18, "bold"),
            "width": 22,
            "height": 2,
            "bd": 3,
            "relief": "raised",
            "highlightthickness": 2
        }
        add_btn = tk.Button(self.root, text="Add to My Books", command=lambda: self.add_book_gui("my_books"), bg="#2196F3", fg="white", activebackground="#1976D2", activeforeground="white", **button_style)
        view_books_btn = tk.Button(self.root, text="View My Books", command=lambda: self.view_books_gui("my_books"), bg="#4CAF50", fg="white", activebackground="#388E3C", activeforeground="white", **button_style)
        view_wishlist_btn = tk.Button(self.root, text="View Wishlist", command=lambda: self.view_books_gui("wishlist"), bg="#4CAF50", fg="white", activebackground="#388E3C", activeforeground="white", **button_style)
        logout_btn = tk.Button(self.root, text="Log Out", command=self.logout, bg="#9E9E9E", fg="white", activebackground="#616161", activeforeground="white", **button_style)
        exit_btn = tk.Button(self.root, text="Exit", command=self.root.quit, bg="#f44336", fg="white", activebackground="#b71c1c", activeforeground="white", **button_style)
        self.home_widgets.extend([add_btn, view_books_btn, view_wishlist_btn, logout_btn, exit_btn])
        
        # Place widgets using place for custom layout
        w = self.root.winfo_width() if self.root.winfo_width() > 1 else 800
        h = self.root.winfo_height() if self.root.winfo_height() > 1 else 600
        y = h // 2 - 180
        spacing = 70
        title_label.place(x=w//2, y=y, anchor="center")
        add_btn.place(x=w//2, y=y+spacing*1, anchor="center")
        view_books_btn.place(x=w//2, y=y+spacing*2, anchor="center")
        view_wishlist_btn.place(x=w//2, y=y+spacing*3, anchor="center")
        logout_btn.place(x=w//2, y=y+spacing*4, anchor="center")
        exit_btn.place(x=w//2, y=y+spacing*5, anchor="center")
        
        self.current_widgets = self.home_widgets
        self.root.update()

    def _reposition_home_widgets(self, event=None):
        if not hasattr(self, 'home_widgets') or not self.home_widgets:
            return
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        y = h // 2 - 180
        spacing = 70
        self.home_widgets[0].place(x=w//2, y=y, anchor="center")
        self.home_widgets[1].place(x=w//2, y=y+spacing*1, anchor="center")
        self.home_widgets[2].place(x=w//2, y=y+spacing*2, anchor="center")
        self.home_widgets[3].place(x=w//2, y=y+spacing*3, anchor="center")
        self.home_widgets[4].place(x=w//2, y=y+spacing*4, anchor="center")
        self.home_widgets[5].place(x=w//2, y=y+spacing*5, anchor="center")

    # Show the form to add a new book.
    # Why: Lets the user input details for a new book and add it to their collection.
    def add_book_gui(self, collection):
        self.clear_widgets()
        self.add_widgets = []
        
        # Place widgets directly on the background for a cleaner look
        title_label = tk.Label(self.root, text="Add a Book", font=("Helvetica", 22, "bold"), fg="#fff", bg="#000000", highlightthickness=2)
        self.add_widgets.append(title_label)
        label_title = tk.Label(self.root, text="Title:", font=("Helvetica", 14), fg="#fff", bg="#000000")
        self.add_widgets.append(label_title)
        title_entry = tk.Entry(self.root, font=("Helvetica", 14), bg="#222", fg="#fff", insertbackground="#fff")
        self.add_widgets.append(title_entry)
        label_author = tk.Label(self.root, text="Author:", font=("Helvetica", 14), fg="#fff", bg="#000000")
        self.add_widgets.append(label_author)
        author_entry = tk.Entry(self.root, font=("Helvetica", 14), bg="#222", fg="#fff", insertbackground="#fff")
        self.add_widgets.append(author_entry)
        
        def save_book():
            title = title_entry.get()
            author = author_entry.get()
            if not title or not author:
                messagebox.showerror("Error", "Both title and author are required!")
                return
            book = {"title": title, "author": author}
            self.collection.add_book(collection, book)
            messagebox.showinfo("Success", f"Book '{title}' added to {'My Books' if collection == 'my_books' else 'Wishlist'}!")
            self.show_home()
        
        save_btn = tk.Button(self.root, text="Save", command=save_book, font=("Helvetica", 14, "bold"), bg="#4CAF50", fg="white", width=12, height=1)
        back_btn = tk.Button(self.root, text="Back", command=self.show_home, font=("Helvetica", 14, "bold"), bg="#f44336", fg="white", width=12, height=1)
        self.add_widgets.append(save_btn)
        self.add_widgets.append(back_btn)
        
        # Place widgets using place for custom layout
        w = self.root.winfo_width() if self.root.winfo_width() > 1 else 800
        h = self.root.winfo_height() if self.root.winfo_height() > 1 else 600
        y = h // 2 - 110
        spacing = 50
        title_label.place(x=w//2, y=y, anchor="center")
        label_title.place(x=w//2, y=y+spacing*1, anchor="center")
        title_entry.place(x=w//2, y=y+spacing*2, anchor="center", width=260)
        label_author.place(x=w//2, y=y+spacing*3, anchor="center")
        author_entry.place(x=w//2, y=y+spacing*4, anchor="center", width=260)
        save_btn.place(x=w//2, y=y+spacing*5+10, anchor="center")
        back_btn.place(x=w//2, y=y+spacing*6+10, anchor="center")
        
        self.current_widgets = self.add_widgets
        self.root.update()

    def _reposition_add_widgets(self, event=None):
        if not hasattr(self, 'add_widgets') or not self.add_widgets:
            return
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        y = h // 2 - 110
        spacing = 50
        self.add_widgets[0].place(x=w//2, y=y, anchor="center")
        self.add_widgets[1].place(x=w//2, y=y+spacing*1, anchor="center")
        self.add_widgets[2].place(x=w//2, y=y+spacing*2, anchor="center", width=260)
        self.add_widgets[3].place(x=w//2, y=y+spacing*3, anchor="center")
        self.add_widgets[4].place(x=w//2, y=y+spacing*4, anchor="center", width=260)
        self.add_widgets[5].place(x=w//2, y=y+spacing*5+10, anchor="center")
        self.add_widgets[6].place(x=w//2, y=y+spacing*6+10, anchor="center")

    # Show the list of books in either 'My Books' or 'Wishlist'.
    # Why: Displays the user's books or wishlist, allowing for management (delete, add to wishlist).
    def view_books_gui(self, collection):
        self.clear_widgets()
        title = "My Books" if collection == "my_books" else "Wishlist"
        title_label = tk.Label(self.root, text=title, font=("Helvetica", 16, "bold"), fg="#fff", bg="#000")
        title_label.place(relx=0.5, rely=0.1, anchor="center")
        books = self.collection.my_books if collection == "my_books" else self.collection.wishlist
        if not books:
            tk.Label(self.root, text="No books found.", font=("Helvetica", 12), fg="#fff", bg="#000").place(relx=0.5, rely=0.2, anchor="center")
        else:
            for i, book in enumerate(books):
                status = book.get("status", "N/A")
                book_text = f"{i+1}. {book['title']} by {book['author']} (Status: {status})"
                tk.Label(self.root, text=book_text, font=("Helvetica", 12), fg="#fff", bg="#000").place(relx=0.5, rely=0.2 + i*0.07, anchor="center")
                def delete_callback(idx=i):
                    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{books[idx]['title']}'?"):
                        self.collection.delete_book(collection, idx)
                        self.view_books_gui(collection)
                tk.Button(self.root, text="Delete", command=lambda idx=i: delete_callback(idx), font=("Helvetica", 10), bg="#f44336", fg="white").place(relx=0.7, rely=0.2 + i*0.07, anchor="center")
                if collection == "my_books":
                    def add_to_wishlist_callback(idx=i):
                        book_to_add = self.collection.my_books[idx]
                        if any(b['title'] == book_to_add['title'] and b['author'] == book_to_add['author'] for b in self.collection.wishlist):
                            messagebox.showinfo("Info", f"'{book_to_add['title']}' is already in your Wishlist.")
                        else:
                            self.collection.add_book("wishlist", {"title": book_to_add['title'], "author": book_to_add['author']})
                            messagebox.showinfo("Success", f"'{book_to_add['title']}' added to Wishlist!")
                    tk.Button(self.root, text="Add to Wishlist", command=lambda idx=i: add_to_wishlist_callback(idx), font=("Helvetica", 10), bg="#2196F3", fg="white").place(relx=0.85, rely=0.2 + i*0.07, anchor="center")
        back_btn = tk.Button(self.root, text="Back", command=self.show_home, font=("Helvetica", 12), bg="#f44336", fg="white", width=10)
        back_btn.place(relx=0.5, rely=0.9, anchor="center")

    # Log out of the app and return to the login screen.
    # Why: Allows the user to end their session and return to the login screen for security or switching users.
    def logout(self):
        self.show_login_screen()

# Start the application by showing the login screen in the same window
if __name__ == "__main__":
    root = tk.Tk()
    app = BookTrackerApp(root)
    root.mainloop()





