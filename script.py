import requests
import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
import time

PROFILE_FILE = 'roblox_profiles.json'
GAME_IDS_FILE = 'roblox_game_ids.json'

def load_profiles():
    return json.load(open(PROFILE_FILE)) if os.path.exists(PROFILE_FILE) else {}

def save_profiles(profiles):
    json.dump(profiles, open(PROFILE_FILE, 'w'), indent=4)

def load_game_ids():
    return json.load(open(GAME_IDS_FILE)) if os.path.exists(GAME_IDS_FILE) else {}

def save_game_ids(game_ids):
    json.dump(game_ids, open(GAME_IDS_FILE, 'w'), indent=4)

def join_game_with_cookie(cookie, game_id):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--incognito")
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.roblox.com")
        time.sleep(3)  # Allow time for the site to load

        driver.add_cookie({
            'name': '.ROBLOSECURITY',
            'value': cookie,
            'domain': '.roblox.com',
            'path': '/',
            'httpOnly': True,
            'secure': True
        })

        driver.refresh()  # Apply cookie
        driver.get(f'https://www.roblox.com/games/{game_id}')
        print("Waiting for Play button...")

        # Wait for the page to load completely
        time.sleep(5)

        # Use JavaScript to find elements with the exact color #335fff
        target_color = "#335fff"  # The exact color you provided
        elements_with_color = driver.execute_script(f"""
            return Array.from(document.querySelectorAll('*')).filter(element => {{
                const color = window.getComputedStyle(element).backgroundColor;
                return color === 'rgb(51, 95, 255)' || color === 'rgba(51, 95, 255, 1)'; // Convert #335fff to RGB
            }});
        """)

        if elements_with_color:
            print(f"Found {len(elements_with_color)} elements with color {target_color}.")
            # Click the first element with the target color (you can add more logic to choose the correct one)
            driver.execute_script("arguments[0].click();", elements_with_color[0])
            print(f"Clicked the element with color {target_color}.")
        else:
            print(f"No elements with color {target_color} found.")

    except NoSuchWindowException:
        print("The browser window was closed before the action completed.")
    except WebDriverException as e:
        print(f"Browser was closed or element click error: {e}")
    except Exception as e:
        messagebox.showerror('Error', f'Failed to click the element: {e}')
    finally:
        time.sleep(10)  # Keep the browser open for a while to observe
        driver.quit()
def add_new_profile():
    new_cookie = simpledialog.askstring("New Profile", "Enter your Roblox .ROBLOSECURITY cookie:")
    if new_cookie:
        profile_name = simpledialog.askstring("Profile Name", "Enter a name for this profile:")
        if profile_name:
            profiles[profile_name] = new_cookie
            save_profiles(profiles)
            update_profile_menu()
            messagebox.showinfo('Success', f'Saved profile for {profile_name}')

def update_profile_menu():
    menu = profile_menu["menu"]
    menu.delete(0, "end")
    for profile in profiles:
        menu.add_command(label=profile, command=tk._setit(profile_var, profile))
    menu.add_command(label="Add New Profile", command=add_new_profile)

def add_new_game():
    new_game_name = simpledialog.askstring("New Game", "Enter the name of the game:")
    new_game_id = simpledialog.askstring("New Game", "Enter the Game ID:")
    if new_game_name and new_game_id:
        game_ids[new_game_name] = new_game_id
        save_game_ids(game_ids)
        update_game_menu()
        messagebox.showinfo('Success', f'Saved game: {new_game_name}')

def update_game_menu():
    menu = game_menu["menu"]
    menu.delete(0, "end")
    for game in game_ids:
        menu.add_command(label=game, command=tk._setit(game_var, game))
    menu.add_command(label="Add New Game", command=add_new_game)

def login_and_join_game():
    selected_profile = profile_var.get()
    selected_game = game_var.get()

    if selected_profile == "Add New Profile":
        add_new_profile()
        return
    elif selected_game == "Add New Game":
        add_new_game()
        return

    cookie = profiles.get(selected_profile, "")
    game_id = game_ids.get(selected_game, "")
    if cookie and game_id:
        join_game_with_cookie(cookie, game_id)
    else:
        messagebox.showerror('Error', "Invalid profile or game selection.")

profiles = load_profiles()
game_ids = load_game_ids()

root = tk.Tk()
root.title("Roblox Game Joiner")

tk.Label(root, text="Select Profile:").grid(row=0, column=0, padx=10, pady=10)
profile_var = tk.StringVar(root, next(iter(profiles), "Add New Profile"))
profile_menu = tk.OptionMenu(root, profile_var, *profiles.keys(), "Add New Profile")
profile_menu.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Select Game:").grid(row=1, column=0, padx=10, pady=10)
game_var = tk.StringVar(root, next(iter(game_ids), "Add New Game"))
game_menu = tk.OptionMenu(root, game_var, *game_ids.keys(), "Add New Game")
game_menu.grid(row=1, column=1, padx=10, pady=10)

join_button = tk.Button(root, text="Join Game", command=login_and_join_game)
join_button.grid(row=2, columnspan=2, pady=20)

update_profile_menu()
update_game_menu()

root.mainloop()
