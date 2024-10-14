from src.app import CalorieApp
import ttkbootstrap as ttk

def main():
    root = ttk.Window(themename="flatly")
    app = CalorieApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
