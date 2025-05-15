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
        self._filename = filename  # encapsulation: private attribute
        self._my_books = []        # encapsulation: private attribute
        self._wishlist = []        # encapsulation: private attribute
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
        self.root.title("Cozy Book Tracker")
        self.root.minsize(600, 400)
        self.collection = BookCollection()

        # Load the original background image
        self.bg_image_original = Image.open("9285857.jpg")
        self.bg_photo = None
        self.bg_label = tk.Label(self.root)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Debounce variable for resize event
        self._resize_after_id = None
        self.root.bind('<Configure>', self._resize_bg)

        # Main frame on top of background, white background, with padding
        self.main_frame = tk.Frame(self.root, bg="white", highlightthickness=0, bd=0)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.show_home()

    def _resize_bg(self, event):
        # Debounce: only update after resizing has stopped for 100ms
        if hasattr(self, '_resize_after_id') and self._resize_after_id:
            self.root.after_cancel(self._resize_after_id)
        self._resize_after_id = self.root.after(100, lambda: self._do_resize_bg(event))

    def _do_resize_bg(self, event):
        if event.width > 1 and event.height > 1:
            resized = self.bg_image_original.resize((event.width, event.height), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized)
            self.bg_label.config(image=self.bg_photo)

    # Show the home screen with navigation buttons.
    # Why: Provides the main navigation for the app, letting users choose what to do next.
    def show_home(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.main_frame.grid_columnconfigure(0, weight=1)
        for i in range(6):
            self.main_frame.grid_rowconfigure(i, weight=1)
        title_label = tk.Label(self.main_frame, text="Welcome to Cozy Book Tracker",
                               font=("Helvetica", 16, "bold"), bg="#f0f0f0")
        title_label.grid(row=0, column=0, pady=20)
        button_style = {"font": ("Helvetica", 12), "padx": 20, "pady": 10, "width": 20}
        tk.Button(self.main_frame, text="Add to My Books",
                  command=lambda: self.add_book_gui("my_books"),
                  bg="#2196F3", fg="white", **button_style).grid(row=1, column=0, pady=5)
        tk.Button(self.main_frame, text="View My Books",
                  command=lambda: self.view_books_gui("my_books"),
                  bg="#4CAF50", fg="white", **button_style).grid(row=2, column=0, pady=5)
        tk.Button(self.main_frame, text="View Wishlist",
                  command=lambda: self.view_books_gui("wishlist"),
                  bg="#4CAF50", fg="white", **button_style).grid(row=3, column=0, pady=5)
        tk.Button(self.main_frame, text="Exit", command=self.root.quit,
                  bg="#f44336", fg="white", **button_style).grid(row=4, column=0, pady=5)
        # Add Log Out button
        tk.Button(self.main_frame, text="Log Out", command=self.logout,
                  bg="#9E9E9E", fg="white", **button_style).grid(row=5, column=0, pady=5)

    # Show the form to add a new book.
    # Why: Lets the user input details for a new book and add it to their collection.
    def add_book_gui(self, collection):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        container = tk.Frame(self.main_frame, bg="#f0f0f0", padx=20, pady=20)
        container.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        for i in range(5):
            container.grid_rowconfigure(i, weight=1)
        tk.Label(container, text="Title:", font=("Helvetica", 12), bg="#f0f0f0").grid(row=0, column=0, pady=10, sticky="w")
        title_entry = tk.Entry(container, font=("Helvetica", 12))
        title_entry.grid(row=1, column=0, pady=5, sticky="ew")
        tk.Label(container, text="Author:", font=("Helvetica", 12), bg="#f0f0f0").grid(row=2, column=0, pady=10, sticky="w")
        author_entry = tk.Entry(container, font=("Helvetica", 12))
        author_entry.grid(row=3, column=0, pady=5, sticky="ew")
        button_frame = tk.Frame(container, bg="#f0f0f0")
        button_frame.grid(row=4, column=0, pady=20)
        # Save the new book to the collection.
        # Why: This nested function is used as a callback for the Save button, keeping the logic close to the UI element.
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
        tk.Button(button_frame, text="Save", command=save_book,
                  font=("Helvetica", 12), bg="#4CAF50", fg="white",
                  padx=20, pady=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="Back", command=self.show_home,
                  font=("Helvetica", 12), bg="#f44336", fg="white",
                  padx=20, pady=10).pack(side="left", padx=5)

    # Show the list of books in either 'My Books' or 'Wishlist'.
    # Why: Displays the user's books or wishlist, allowing for management (delete, add to wishlist).
    def view_books_gui(self, collection):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        container = tk.Frame(self.main_frame, bg="#f0f0f0", padx=20, pady=20)
        container.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        canvas = tk.Canvas(container, bg="#f0f0f0")
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        books = self.collection.my_books if collection == "my_books" else self.collection.wishlist
        if not books:
            tk.Label(scrollable_frame, text="No books found.",
                     font=("Helvetica", 12), bg="#f0f0f0").pack(pady=10)
        else:
            for index, book in enumerate(books, start=1):
                status = book.get("status", "N/A")
                book_frame = tk.Frame(scrollable_frame, bg="#f0f0f0", pady=5)
                book_frame.pack(fill="x", padx=5)
                info_frame = tk.Frame(book_frame, bg="#f0f0f0")
                info_frame.pack(fill="x", expand=True)
                tk.Label(info_frame,
                         text=f"{index}. {book['title']} by {book['author']} (Status: {status})",
                         font=("Helvetica", 12), bg="#f0f0f0").pack(side="left", anchor="w")
                # Delete the selected book.
                # Why: This nested function is used as a callback for the Delete button, allowing the user to remove books.
                def delete_callback(idx=index-1):
                    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{books[idx]['title']}'?"):
                        self.collection.delete_book(collection, idx)
                        self.view_books_gui(collection)
                tk.Button(info_frame, text="Delete",
                          command=lambda idx=index-1: delete_callback(idx),
                          font=("Helvetica", 10), bg="#f44336", fg="white",
                          padx=10, pady=5).pack(side="right", padx=5)
                # Add to Wishlist button for 'My Books' view.
                # Why: Lets users move books from 'My Books' to their wishlist for future reading.
                if collection == "my_books":
                    def add_to_wishlist_callback(idx=index-1):
                        book_to_add = self.collection.my_books[idx]
                        if any(b['title'] == book_to_add['title'] and b['author'] == book_to_add['author'] for b in self.collection.wishlist):
                            messagebox.showinfo("Info", f"'{book_to_add['title']}' is already in your Wishlist.")
                        else:
                            self.collection.add_book("wishlist", {"title": book_to_add['title'], "author": book_to_add['author']})
                            messagebox.showinfo("Success", f"'{book_to_add['title']}' added to Wishlist!")
                    tk.Button(info_frame, text="Add to Wishlist",
                              command=lambda idx=index-1: add_to_wishlist_callback(idx),
                              font=("Helvetica", 10), bg="#2196F3", fg="white",
                          padx=10, pady=5).pack(side="right", padx=5)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        tk.Button(container, text="Back", command=self.show_home,
                  font=("Helvetica", 12), bg="#f44336", fg="white",
                  padx=20, pady=10).pack(pady=10)

    # Log out of the app and return to the login screen.
    # Why: Allows the user to end their session and return to the login screen for security or switching users.
    def logout(self):
        self.root.destroy()
        show_login_screen()

# Start the application by showing the login screen.
# Why: Ensures the user must log in before accessing the main app.
if __name__ == "__main__":
    show_login_screen()





