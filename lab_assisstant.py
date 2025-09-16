import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import pyttsx3, fitz, os, webbrowser
from pdf2image import convert_from_path
import pytesseract, numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

engine, extracted_text, steps, current_step = pyttsx3.init(), "", [], 0
a = tk.Tk(); a.title("AK Virtual Lab Assistant"); a.geometry("800x800")
selected_lab, action_choice = tk.StringVar(), tk.StringVar(value="video")

def speak(t): engine.say(t); engine.runAndWait()
def upload_pdf():
    global extracted_text, steps, current_step
    path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if not path: speak("No PDF uploaded."); return
    try: text = "".join([page.get_text() for page in fitz.open(path)])
    except: text = ""
    if not text.strip():
        speak("Trying OCR."); text = ""
        for img in convert_from_path(path):
            gray = img.convert('L').point(lambda x: 0 if x<128 else 255, '1')
            text += pytesseract.image_to_string(gray)
    if not text.strip(): messagebox.showerror("Error", "No readable content."); speak("No readable content."); return
    extracted_text, steps, current_step = text, [l.strip() for l in text.split('\n') if l.strip()], 0
    assistant_output.config(state="normal")
    assistant_output.delete("1.0", tk.END)
    assistant_output.insert(tk.END, f"{os.path.basename(path)} uploaded successfully.\n\n")
    assistant_output.config(state="disabled")
    speak("PDF uploaded successfully.")

def next_step():
    global current_step
    if current_step < len(steps):
        assistant_output.config(state="normal")
        assistant_output.insert(tk.END, f"Step {current_step+1}: {steps[current_step]}\n\n")
        assistant_output.config(state="disabled")
        speak(steps[current_step])
        current_step += 1
    else: speak("All steps completed."); messagebox.showinfo("Done", "All steps completed.")

def handle_action():
    lab, exp_name, action = selected_lab.get(), experiment_entry.get().strip().lower(), action_choice.get()
    if not lab: speak("Select lab."); messagebox.showwarning("Warning", "Select a lab!"); return
    if not exp_name: speak("Enter experiment name."); messagebox.showwarning("Warning", "Enter experiment name!"); return
    if action == "video": play_video(lab, exp_name)
    else: generate_graph(exp_name)

def play_video(lab, exp_name):
    links = {("BEE", "ohms law"): "https://drive.google.com/file/d/1TJ8GYr4jkghwH0iEZwmdcQrCf4avG2FI/view?usp=drivesdk",
             ("AP", "photo electric effect"): "https://drive.google.com/file/d/1uNq87E-s9w6oBrGu9vqO3x-BgIGhwAxn/view?usp=drivesdk"}
    if (lab, exp_name) in links: speak("Opening video."); webbrowser.open(links[(lab, exp_name)])
    else: speak("Video not available."); messagebox.showerror("Error", "Practical video not available!")

def generate_graph(exp_name):
    graphs = {"ohms law": 0, "single phase transformer":1, "photo electric effect":2, "numerical aperture and acceptance angle of an optical fibre":3}
    if exp_name in graphs: plot_graph(graphs[exp_name])
    else: speak("Graph not available."); messagebox.showerror("Error", "Graph not available!")

def plot_graph(option):
    fig = plt.figure(figsize=(5,4))
    if option == 0:
        ax, x, y = fig.add_subplot(), [], []; line, = ax.plot([], [], 'r-')
        ax.set_xlim(0,10); ax.set_ylim(0,20); ax.set_title("Ohm's Law"); ax.set_xlabel("Current (I)"); ax.set_ylabel("Voltage (V)")
        def update(f): x.append(f/10); y.append(2*f/10); line.set_data(x,y); return line,
        animation.FuncAnimation(fig, update, frames=np.linspace(0,10,50), interval=100, blit=True)
    elif option == 1:
        ax = fig.add_subplot(); x = np.linspace(0,10,100); y = np.sin(x)
        line, = ax.plot([], [], 'b-'); ax.set_xlim(0,10); ax.set_ylim(-1.5,1.5); ax.set_title("Transformer Signal")
        def update(f): line.set_data(x[:f], y[:f]); return line,
        animation.FuncAnimation(fig, update, frames=len(x), interval=50, blit=True)
    elif option == 2:
        ax = fig.add_subplot(); x = np.linspace(0,5,100); y = np.maximum(0,x-2)
        ax.plot(x,y,'g-'); ax.set_title("Photoelectric Effect"); ax.set_xlabel("Photon Energy"); ax.set_ylabel("Kinetic Energy")
    elif option == 3:
        ax = fig.add_subplot(projection='polar'); theta = np.linspace(0,2*np.pi,100); r = np.abs(np.sin(2*theta))
        ax.plot(theta,r); ax.set_title("Optical Fibre")
    new_win = tk.Toplevel(a); new_win.title("Graph/Animation")
    FigureCanvasTkAgg(fig, master=new_win).get_tk_widget().pack()
    tk.Button(new_win, text="Close", font=("Arial", 12), command=new_win.destroy).pack(pady=10)
    speak("Showing graph." if option>=2 else "Playing animation.")

tk.Button(a, text="Upload Lab Manual PDF", font=("Arial", 12), command=upload_pdf).pack(pady=10)
tk.Button(a, text="Next Step", font=("Arial", 12), command=next_step).pack(pady=10)
tk.Label(a, text="Select Lab:", font=("Arial", 12, "bold")).pack()
for lab,val in [("BEE Lab","BEE"),("Applied Physics Lab","AP")]: tk.Radiobutton(a, text=lab, variable=selected_lab, value=val, font=("Arial",11)).pack()
tk.Label(a, text="Enter Experiment Name:", font=("Arial", 12, "bold")).pack()
experiment_entry = tk.Entry(a, font=("Arial", 12), width=50); experiment_entry.pack(pady=5)
tk.Label(a, text="Choose Action:", font=("Arial", 12, "bold")).pack()
for text,val in [("Watch Practical Video","video"),("See Graph","graph")]: tk.Radiobutton(a, text=text, variable=action_choice, value=val, font=("Arial",11)).pack()
tk.Button(a, text="Start", font=("Arial", 12), command=handle_action).pack(pady=10)
tk.Label(a, text="Assistant Response:", font=("Arial", 12, "bold")).pack()
assistant_output = ScrolledText(a, height=15, width=90, state="disabled", wrap="word"); assistant_output.pack(pady=10)

def start_gui():
    speak("Welcome to AK Virtual Lab Assistant. Upload lab manual and select lab.")
    assistant_output.config(state="normal")
    assistant_output.insert(tk.END, "Welcome to AK Virtual Lab Assistant!\n\nUpload your lab manual and select a lab to begin.\n")
    assistant_output.config(state="disabled")

a.after(1000, start_gui)
a.mainloop()
