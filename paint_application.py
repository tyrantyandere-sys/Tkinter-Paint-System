import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk

PEACH_BG = "#FFE8D6"
PEACH_PANEL = "#FFD7BA"
PEACH_BUTTON = "#FFBE98"
PEACH_HOVER = "#FFA877"
TEXT_COLOR = "#5C3D2E"
FONT_MAIN = ("Arial", 10, "bold")

CANVAS_WIDTH = 900
CANVAS_HEIGHT = 550

root = tk.Tk()
root.title("My Paint Application")
root.geometry("1000x750")
root.configure(bg=PEACH_BG)

image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")
draw = ImageDraw.Draw(image)
canvas_image = None

current_color = "#000000"
brush_size = 5
tool = "brush"
start_x = start_y = None
last_x = last_y = None
preview_shape = None
undo_list = []


def choose_color():
    """Open the color chooser and update the drawing color."""
    selected = colorchooser.askcolor(title="Choose a color")
    if selected[1] is not None:
        set_color(selected[1])


def set_color(color):
    global current_color, tool
    current_color = color
    if tool == "eraser":
        tool = "brush"
    color_box.config(bg=current_color)


def set_tool(selected_tool):
    """Change the active drawing tool."""
    global tool
    tool = selected_tool


def change_brush_size(value):
    """Update the brush size using the slider."""
    global brush_size
    brush_size = int(float(value))


def save_for_undo():
    undo_list.append(image.copy())
    if len(undo_list) > 20:
        undo_list.pop(0)


def undo():
    global image, draw
    if len(undo_list) == 0:
        return
    image = undo_list.pop()
    draw = ImageDraw.Draw(image)
    refresh_canvas()


def start_drawing(event):
    """Remember the mouse position when drawing starts."""
    global last_x, last_y, start_x, start_y
    save_for_undo()
    last_x, last_y = event.x, event.y
    start_x, start_y = event.x, event.y


def draw_motion(event):
    """Draw while the left mouse button is held."""
    global last_x, last_y
    color = "white" if tool == "eraser" else current_color
    if tool in ("brush", "eraser"):
        canvas.create_line(last_x, last_y, event.x, event.y,
                           fill=color, width=brush_size,
                           capstyle=tk.ROUND, smooth=True)
        draw.line((last_x, last_y, event.x, event.y),
                  fill=color, width=brush_size)
        r = brush_size / 2
        draw.ellipse((event.x - r, event.y - r, event.x + r, event.y + r),
                     fill=color)
        last_x, last_y = event.x, event.y
    else:
        preview_shape_drawing(event)


def preview_shape_drawing(event):
    """Show a temporary shape while the mouse is dragged."""
    global preview_shape
    if preview_shape is not None:
        canvas.delete(preview_shape)

    if fill_on.get() == 1:
        fill_color = current_color
    else:
        fill_color = ""

    if tool == "line":
        preview_shape = canvas.create_line(
            start_x, start_y, event.x, event.y,
            fill=current_color, width=brush_size)
    elif tool == "rectangle":
        preview_shape = canvas.create_rectangle(
            start_x, start_y, event.x, event.y,
            outline=current_color, fill=fill_color, width=brush_size)
    elif tool == "oval":
        preview_shape = canvas.create_oval(
            start_x, start_y, event.x, event.y,
            outline=current_color, fill=fill_color, width=brush_size)
    elif tool == "triangle":
        preview_shape = canvas.create_polygon(
            (start_x + event.x) / 2, start_y,
            start_x, event.y,
            event.x, event.y,
            outline=current_color, fill=fill_color, width=brush_size)


def finish_drawing(event):
    """Store the selected shape in the Pillow image."""
    global preview_shape

    if fill_on.get() == 1:
        fill_color = current_color
    else:
        fill_color = None

    x1 = min(start_x, event.x)
    x2 = max(start_x, event.x)
    y1 = min(start_y, event.y)
    y2 = max(start_y, event.y)

    if tool == "line":
        draw.line((start_x, start_y, event.x, event.y),
                  fill=current_color, width=brush_size)
    elif tool == "rectangle":
        draw.rectangle((x1, y1, x2, y2), outline=current_color,
                       fill=fill_color, width=brush_size)
    elif tool == "oval":
        draw.ellipse((x1, y1, x2, y2), outline=current_color,
                     fill=fill_color, width=brush_size)
    elif tool == "triangle":
        points = [((start_x + event.x) / 2, start_y),
                  (start_x, event.y),
                  (event.x, event.y)]
        draw.polygon(points, outline=current_color, fill=fill_color,
                     width=brush_size)

    preview_shape = None
    refresh_canvas()


def refresh_canvas():
    """Display the current Pillow image on the Tkinter canvas."""
    global canvas_image
    canvas.delete("all")
    canvas_image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor="nw", image=canvas_image)


def clear_canvas():
    """Replace the current drawing with a blank white image."""
    global image, draw, preview_shape
    answer = messagebox.askyesno("Clear", "Are you sure you want to clear the canvas?")
    if answer == False:
        return
    save_for_undo()
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")
    draw = ImageDraw.Draw(image)
    preview_shape = None
    refresh_canvas()


def open_image():
    """Open an image and display it on the canvas."""
    global image, draw
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
    if file_path:
        try:
            opened_image = Image.open(file_path).convert("RGB")
            opened_image = opened_image.resize((CANVAS_WIDTH, CANVAS_HEIGHT))
            save_for_undo()
            image = opened_image
            draw = ImageDraw.Draw(image)
            refresh_canvas()
        except Exception as error:
            messagebox.showerror("Error", f"Could not open image:\n{error}")


def save_image():
    """Save the current drawing as an image file."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"),
                   ("JPEG Image", "*.jpg"),
                   ("Bitmap Image", "*.bmp")])
    if file_path:
        try:
            image.save(file_path)
            messagebox.showinfo("Saved", "Your drawing has been saved!")
        except Exception as error:
            messagebox.showerror("Error", f"Could not save image:\n{error}")


def make_button(parent, text, command):
    """Create one peach button so we do not repeat the styling."""
    return tk.Button(parent, text=text, command=command,
                     bg=PEACH_BUTTON, fg=TEXT_COLOR,
                     activebackground=PEACH_HOVER, activeforeground=TEXT_COLOR,
                     font=FONT_MAIN, relief="flat", padx=10, pady=4,
                     cursor="hand2")


toolbar = tk.Frame(root, bg=PEACH_PANEL, padx=10, pady=8)
toolbar.pack(pady=(10, 3))

make_button(toolbar, "Brush",
            lambda: set_tool("brush")).pack(side="left", padx=4)
make_button(toolbar, "Eraser",
            lambda: set_tool("eraser")).pack(side="left", padx=4)
make_button(toolbar, "Line",
            lambda: set_tool("line")).pack(side="left", padx=4)
make_button(toolbar, "Rectangle",
            lambda: set_tool("rectangle")).pack(side="left", padx=4)
make_button(toolbar, "Oval",
            lambda: set_tool("oval")).pack(side="left", padx=4)
make_button(toolbar, "Triangle",
            lambda: set_tool("triangle")).pack(side="left", padx=4)

fill_on = tk.IntVar()
tk.Checkbutton(toolbar, text="Fill", variable=fill_on,
               bg=PEACH_PANEL, fg=TEXT_COLOR, activebackground=PEACH_PANEL,
               font=FONT_MAIN).pack(side="left", padx=(10, 4))

tk.Label(toolbar, text="Brush Size:", bg=PEACH_PANEL,
         fg=TEXT_COLOR, font=FONT_MAIN).pack(side="left", padx=(10, 3))
size_slider = tk.Scale(toolbar, from_=1, to=30, orient="horizontal",
                       command=change_brush_size, length=150,
                       bg=PEACH_PANEL, fg=TEXT_COLOR,
                       troughcolor=PEACH_BUTTON, highlightthickness=0)
size_slider.set(5)
size_slider.pack(side="left", padx=3)

toolbar2 = tk.Frame(root, bg=PEACH_PANEL, padx=10, pady=8)
toolbar2.pack(pady=3)

color_button = make_button(toolbar2, "Choose Color", choose_color)
color_button.pack(side="left", padx=4)

color_box = tk.Label(toolbar2, bg=current_color, width=3, relief="sunken")
color_box.pack(side="left", padx=(0, 10))

tk.Button(toolbar2, bg="#000000", width=3, cursor="hand2",
          command=lambda: set_color("#000000")).pack(side="left", padx=2)
tk.Button(toolbar2, bg="#FF0000", width=3, cursor="hand2",
          command=lambda: set_color("#FF0000")).pack(side="left", padx=2)
tk.Button(toolbar2, bg="#0000FF", width=3, cursor="hand2",
          command=lambda: set_color("#0000FF")).pack(side="left", padx=2)
tk.Button(toolbar2, bg="#008000", width=3, cursor="hand2",
          command=lambda: set_color("#008000")).pack(side="left", padx=2)
tk.Button(toolbar2, bg="#FFFF00", width=3, cursor="hand2",
          command=lambda: set_color("#FFFF00")).pack(side="left", padx=2)
tk.Button(toolbar2, bg="#800080", width=3, cursor="hand2",
          command=lambda: set_color("#800080")).pack(side="left", padx=2)

make_button(toolbar2, "Undo", undo).pack(side="left", padx=(12, 4))
make_button(toolbar2, "Clear", clear_canvas).pack(side="left", padx=4)
make_button(toolbar2, "Open", open_image).pack(side="left", padx=4)
make_button(toolbar2, "Save", save_image).pack(side="left", padx=4)

canvas_frame = tk.Frame(root, bg=PEACH_BUTTON, padx=4, pady=4)
canvas_frame.pack(padx=20, pady=10)
canvas = tk.Canvas(canvas_frame, width=CANVAS_WIDTH,
                   height=CANVAS_HEIGHT,
                   bg="white", cursor="cross", highlightthickness=0)
canvas.pack()

canvas.bind("<Button-1>", start_drawing)
canvas.bind("<B1-Motion>", draw_motion)
canvas.bind("<ButtonRelease-1>", finish_drawing)

root.mainloop()