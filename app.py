import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox

from db import init_db, get_next_new_lead, update_lead_status, get_remaining_count
from enricher import generate_pitch

# Ensure the schema exists before the UI queries it.
init_db()

# Maximum allowed length for a LinkedIn connection request pitch.
MAX_PITCH_LENGTH = 300

def set_buttons_enabled(enabled):
    """Enable or disable the action buttons."""
    state = tk.NORMAL if enabled else tk.DISABLED
    approve_btn.config(state=state)
    skip_btn.config(state=state)


def update_remaining_counter():
    """Refresh the remaining-leads counter label."""
    remaining = get_remaining_count()
    remaining_label.config(text=f"Remaining new leads: {remaining}")


def get_pitch_text():
    """Return the pitch text without Tk's implicit trailing newline."""
    # Tk always appends a newline to Text contents; strip it so the
    # character count and clipboard payload match what the user sees.
    return draft_text.get("1.0", "end-1c")


def update_char_counter(event=None):
    """Update the pitch length counter and warn when over the limit."""
    length = len(get_pitch_text().strip())
    over_limit = length > MAX_PITCH_LENGTH
    if over_limit:
        char_label.config(
            text=f"{length}/{MAX_PITCH_LENGTH} characters (too long!)",
            fg="red",
        )
    else:
        char_label.config(
            text=f"{length}/{MAX_PITCH_LENGTH} characters",
            fg="gray",
        )
    # Block approval while the pitch is empty or over the limit, but only
    # when a lead is actually loaded (skip_btn stays usable otherwise).
    if current_lead_id is not None:
        approve_btn.config(
            state=tk.DISABLED if (over_limit or length == 0) else tk.NORMAL
        )


def open_current_url(event=None):
    """Open the current LinkedIn URL in the default browser."""
    if not current_url:
        return
    try:
        webbrowser.open(current_url)
    except Exception as e:
        messagebox.showerror("Error", f"Could not open URL:\n{e}")

def on_pitch_generated(pitch, error):
    """Callback invoked on the main thread once generation finishes."""
    global current_lead_id

    if error:
        draft_text.delete("1.0", tk.END)
        draft_text.insert(tk.END, f"Error generating pitch: {error}")
        # Keep the lead loaded but block approval on failure.
        approve_btn.config(state=tk.DISABLED)
        skip_btn.config(state=tk.NORMAL)
        return

    draft_text.delete("1.0", tk.END)
    draft_text.insert(tk.END, pitch)
    update_char_counter()
    # update_char_counter already enables approve when the pitch is valid;
    # only force-enable skip here.
    skip_btn.config(state=tk.NORMAL)

def load_lead_into_ui():
    """Loads the next lead and generates the draft for the UI."""
    global current_lead_id, current_url
    
    lead = get_next_new_lead()
    if not lead:
        current_lead_id = None
        current_url = None
        url_label.config(text="URL: ")
        raw_data_text.delete("1.0", tk.END)
        draft_text.delete("1.0", tk.END)
        update_char_counter()
        update_remaining_counter()
        messagebox.showinfo("Done", "No more new leads in the database!")
        root.quit()
        return

    current_lead_id, url, title, body, _target_role = lead
    current_url = url

    # Update UI with raw data
    url_label.config(text=f"URL: {url}")
    raw_data_text.delete("1.0", tk.END)
    raw_data_text.insert(tk.END, f"TITLE:\n{title}\n\nSNIPPET:\n{body}")

    # Generate and display the AI pitch in a background thread
    draft_text.delete("1.0", tk.END)
    draft_text.insert(tk.END, "Generating a personalized pitch...")
    update_char_counter()
    set_buttons_enabled(False)
    update_remaining_counter()

    def worker():
        try:
            pitch = generate_pitch(title, body)
            error = None
        except Exception as e:
            pitch = None
            error = str(e)
        # Marshal the result back onto the Tkinter main thread.
        root.after(0, lambda: on_pitch_generated(pitch, error))

    threading.Thread(target=worker, daemon=True).start()

def approve_and_copy():
    """Copies the pitch to clipboard and marks the lead as processed."""
    if current_lead_id is None:
        messagebox.showwarning("No lead", "There is no active lead to approve.")
        return

    pitch = get_pitch_text().strip()

    if not pitch:
        messagebox.showwarning("Empty pitch", "The pitch is empty. Nothing to approve.")
        return
    if len(pitch) > MAX_PITCH_LENGTH:
        messagebox.showwarning(
            "Pitch too long",
            f"The pitch is {len(pitch)} characters, exceeding the "
            f"{MAX_PITCH_LENGTH}-character limit.",
        )
        return

    # Copy to clipboard
    root.clipboard_clear()
    root.clipboard_append(pitch)

    # Persist the (possibly manually edited) pitch and mark as processed.
    update_lead_status(current_lead_id, "Processed", ai_draft_pitch=pitch)

    # Move to next (load_lead_into_ui refreshes the remaining counter).
    load_lead_into_ui()

def skip_lead():
    """Marks the lead as skipped if it's irrelevant or low quality."""
    if current_lead_id is None:
        messagebox.showwarning("No lead", "There is no active lead to skip.")
        return

    update_lead_status(current_lead_id, "Skipped")
    # load_lead_into_ui refreshes the remaining counter after the status change.
    load_lead_into_ui()

# --- Build Tkinter GUI ---
root = tk.Tk()
root.title("DeepSeek Lead Sandbox - Cyprus Events")
root.geometry("700x550")
root.configure(padx=20, pady=20)

current_lead_id = None
current_url = None

header_frame = tk.Frame(root)
header_frame.pack(fill="x")

tk.Label(header_frame, text="Raw Search Snippet", font=("Arial", 12, "bold")).pack(side="left", anchor="w")
remaining_label = tk.Label(header_frame, text="Remaining new leads: 0", fg="gray")
remaining_label.pack(side="right", anchor="e")

url_label = tk.Label(root, text="URL: ", fg="blue", cursor="hand2")
url_label.pack(anchor="w", pady=(0, 5))
url_label.bind("<Button-1>", open_current_url)

raw_data_text = tk.Text(root, height=6, wrap=tk.WORD, bg="#f0f0f0")
raw_data_text.pack(fill="x", pady=(0, 15))

pitch_header_frame = tk.Frame(root)
pitch_header_frame.pack(fill="x")

tk.Label(pitch_header_frame, text="AI Draft Pitch", font=("Arial", 12, "bold")).pack(side="left", anchor="w")
char_label = tk.Label(pitch_header_frame, text=f"0/{MAX_PITCH_LENGTH} characters", fg="gray")
char_label.pack(side="right", anchor="e")

draft_text = tk.Text(root, height=6, wrap=tk.WORD, font=("Arial", 11))
draft_text.pack(fill="x", pady=(0, 20))
draft_text.bind("<KeyRelease>", update_char_counter)

btn_frame = tk.Frame(root)
btn_frame.pack(fill="x")

skip_btn = tk.Button(btn_frame, text="Reject / Skip", command=skip_lead, bg="#ffcccb", width=15, height=2)
skip_btn.pack(side="left", padx=10)
approve_btn = tk.Button(btn_frame, text="Approve & Copy", command=approve_and_copy, bg="#90ee90", font=("Arial", 10, "bold"), width=20, height=2)
approve_btn.pack(side="right", padx=10)

# Start the loop
load_lead_into_ui()
root.mainloop()
