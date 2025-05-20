import json
import tkinter as tk
from tkinter import messagebox
import requests
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import csv
import os
import customtkinter as ctk
from PIL import Image, ImageTk
import io
import time
import threading
import math
import gzip

# Set appearance mode and theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ModernWeatherDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Weather Dashboard")
        self.root.geometry("1000x800")
        self.root.minsize(800, 600)  # Set minimum size
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # API key from .env file (for safety and security of api keys)
        from dotenv import load_dotenv
        load_dotenv()
        
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        
        # Set initial theme
        self.current_theme = "dark"
        
        # Create UI elements first so status_bar is available for get_city_list
        self.create_ui()
        
        # Load city list
        try:
            self.cities = self.get_city_list()
            # Build sorted city list with country code
            self.city_names = [f"{city['name']}, {city['country']}" for city in self.cities]
            self.city_names.sort()
        except Exception as e:
            self.cities = []
            self.city_names = []
            messagebox.showwarning("Warning", f"Could not load city list: {str(e)}\nSearch functionality will be limited.")

        # Weather data
        self.weather_data = None
        self.selected_city = None
        
        # Weather icons
        self.weather_icons = {
            "Clear": "☀️",
            "Clouds": "☁️",
            "Rain": "🌧️",
            "Drizzle": "🌦️",
            "Thunderstorm": "⛈️",
            "Snow": "❄️",
            "Mist": "🌫️",
            "Fog": "🌫️",
            "Haze": "🌫️",
            "Smoke": "🌫️",
            "Dust": "🌫️",
            "Sand": "🌫️",
            "Ash": "🌫️",
            "Squall": "💨",
            "Tornado": "🌪️"
        }
        
        # Animation variables
        self.animation_running = False
        self.loading_angle = 0
        
    def get_city_list(self):
        """Get the list of cities from OpenWeatherMap"""
        file_path = 'city.list.json'
        if not os.path.exists(file_path):
            try:
                url = 'http://bulk.openweathermap.org/sample/city.list.json.gz'
                self.status_bar.configure(text="Downloading city list...")
                r = requests.get(url)
                with open("city.list.json.gz", 'wb') as f:
                    f.write(r.content)
                self.status_bar.configure(text="Extracting city list...")
                with gzip.open("city.list.json.gz", 'rb') as f_in:
                    with open(file_path, 'wb') as f_out:
                        f_out.write(f_in.read())
                # Clean up the compressed file
                if os.path.exists("city.list.json.gz"):
                    os.remove("city.list.json.gz")
                self.status_bar.configure(text="City list downloaded successfully")
            except Exception as e:
                self.status_bar.configure(text="Failed to download city list")
                messagebox.showerror("Error", f"Failed to download city list: {str(e)}")
                return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.status_bar.configure(text="Failed to load city list")
            messagebox.showerror("Error", f"Failed to load city list: {str(e)}")
            return []
        
    def create_ui(self):
        # Create main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create header with title
        self.header_frame = ctk.CTkFrame(self.main_container, corner_radius=0)
        self.header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Weather Dashboard", 
            font=ctk.CTkFont(size=24, weight="bold"),
            padx=20,
            pady=20
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Theme toggle button
        self.theme_button = ctk.CTkButton(
            self.header_frame,
            text="🌙 Dark",
            width=100,
            command=self.toggle_theme
        )
        self.theme_button.pack(side=tk.RIGHT, padx=20)
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self.main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Search section
        self.search_frame = ctk.CTkFrame(self.content_frame)
        self.search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.search_label = ctk.CTkLabel(
            self.search_frame, 
            text="Enter City Name:", 
            font=ctk.CTkFont(size=14)
        )
        self.search_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Search entry with auto-complete
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_suggestions)
        
        self.search_entry = ctk.CTkEntry(
            self.search_frame, 
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            textvariable=self.search_var
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Search button
        self.search_button = ctk.CTkButton(
            self.search_frame, 
            text="Get Weather",
            width=120,
            height=40,
            command=self.get_weather
        )
        self.search_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export button
        self.export_button = ctk.CTkButton(
            self.search_frame, 
            text="Export to CSV",
            width=120,
            height=40,
            command=self.export_to_csv
        )
        self.export_button.pack(side=tk.LEFT)
        
        # Suggestions frame
        self.suggestions_frame = ctk.CTkFrame(self.content_frame)
        self.suggestions_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Suggestions listbox (using normal Tkinter as CTk doesn't have listbox)
        self.suggestions_listbox = tk.Listbox(
            self.suggestions_frame, 
            height=5, 
            font=("Helvetica", 12),
            activestyle="none",
            bd=1,
            bg="#2b2b2b",
            fg="#ffffff",
            selectbackground="#1f538d"
        )
        self.suggestions_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.suggestions_listbox.bind("<<ListboxSelect>>", self.on_suggestion_select)
        
        # Loading indicator canvas - using standard tk.Canvas with appropriate color
        self.loading_canvas = tk.Canvas(
            self.content_frame,
            width=50,
            height=50,
            bg=self.content_frame._apply_appearance_mode(self.content_frame._fg_color),
            highlightthickness=0
        )
        self.loading_canvas.pack(pady=(0, 10))
        
        # Main content (split into two columns)
        self.main_content = ctk.CTkFrame(self.content_frame)
        self.main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(1, weight=2)
        self.main_content.grid_rowconfigure(0, weight=1)
        
        # Left column - Weather info
        self.info_frame = ctk.CTkFrame(self.main_content)
        self.info_frame.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        
        self.weather_header = ctk.CTkLabel(
            self.info_frame, 
            text="Current Weather", 
            font=ctk.CTkFont(size=18, weight="bold"),
            pady=10
        )
        self.weather_header.pack(fill=tk.X, padx=15)
        
        # Weather icon display
        self.weather_icon_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=64)
        )
        self.weather_icon_label.pack(pady=(0, 10))
        
        # Weather details
        self.weather_details = ctk.CTkTextbox(
            self.info_frame,
            width=250,
            font=ctk.CTkFont(size=14),
            wrap="word"
        )
        self.weather_details.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        self.weather_details.configure(state="disabled")
        
        # Right column - Chart
        self.chart_frame = ctk.CTkFrame(self.main_content)
        self.chart_frame.grid(row=0, column=1, padx=(0, 0), pady=0, sticky="nsew")
        
        # Create chart header
        ctk.CTkLabel(
            self.chart_frame, 
            text="Weather Forecast", 
            font=ctk.CTkFont(size=18, weight="bold"),
            pady=10
        ).pack(fill=tk.X, padx=15)
        
        # Create a placeholder for the plot
        self.plot_container = ctk.CTkFrame(self.chart_frame)
        self.plot_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.create_placeholder()
        
        # Status bar - created earlier so it can be used by get_city_list
        self.status_bar = ctk.CTkLabel(
            self.main_container,
            text="Ready",
            height=25,
            anchor="w",
            padx=10
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Set initial theme
        self.current_theme = "dark"
    
    def toggle_theme(self):
        if self.current_theme == "dark":
            ctk.set_appearance_mode("light")
            self.theme_button.configure(text="☀️ Light")
            self.current_theme = "light"
            # Update listbox colors for light theme
            self.suggestions_listbox.configure(bg="#f0f0f0", fg="#000000")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_button.configure(text="🌙 Dark")
            self.current_theme = "dark"
            # Update listbox colors for dark theme
            self.suggestions_listbox.configure(bg="#2b2b2b", fg="#ffffff")
    
    def create_placeholder(self):
        # Clear the plot container
        for widget in self.plot_container.winfo_children():
            widget.destroy()
            
        # Create a figure and place it in the plot frame
        fig = plt.Figure(figsize=(8, 6), dpi=100)
        # Set background color based on theme mode
        if self.current_theme == "dark":
            fig.patch.set_facecolor("#2b2b2b")
        else:
            fig.patch.set_facecolor("#f0f0f0")
            
        ax = fig.add_subplot(111)
        ax.set_title("Select a city to view forecast", color="white" if self.current_theme == "dark" else "black")
        ax.set_xlabel("Date & Time", color="white" if self.current_theme == "dark" else "black")
        ax.set_ylabel("Value", color="white" if self.current_theme == "dark" else "black")
        ax.text(0.5, 0.5, "No data to display", ha='center', va='center', transform=ax.transAxes, 
                color="white" if self.current_theme == "dark" else "black")
        ax.tick_params(colors="white" if self.current_theme == "dark" else "black")
        ax.spines['bottom'].set_color("white" if self.current_theme == "dark" else "black")
        ax.spines['top'].set_color("white" if self.current_theme == "dark" else "black")
        ax.spines['left'].set_color("white" if self.current_theme == "dark" else "black")
        ax.spines['right'].set_color("white" if self.current_theme == "dark" else "black")
        
        canvas = FigureCanvasTkAgg(fig, master=self.plot_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_suggestions(self, *args):
        search_term = self.search_var.get().lower()
        
        # Clear the listbox
        self.suggestions_listbox.delete(0, tk.END)
        
        if len(search_term) < 2:
            return
        
        # Find matching cities
        suggestions = [name for name in self.city_names if search_term in name.lower()]
        
        # Add up to 5 suggestions
        for name in suggestions[:5]:
            self.suggestions_listbox.insert(tk.END, name)
    
    def on_suggestion_select(self, event):
        if self.suggestions_listbox.curselection():
            selected_idx = self.suggestions_listbox.curselection()[0]
            selected_city = self.suggestions_listbox.get(selected_idx)
            self.search_var.set(selected_city)
            self.suggestions_listbox.delete(0, tk.END)
    
    def start_loading_animation(self):
        self.animation_running = True
        self.loading_angle = 0
        self.loading_canvas.delete("all")
        self.animate_loading()
    
    def stop_loading_animation(self):
        self.animation_running = False
        self.loading_canvas.delete("all")
    
    def animate_loading(self):
        if not self.animation_running:
            return
        
        self.loading_canvas.delete("all")
        
        # Draw loading spinner
        center_x, center_y = 25, 25
        radius = 15
        start_angle = self.loading_angle
        extent = 300  # Degrees of the arc
        
        # Convert angles to radians for calculations
        start_rad = math.radians(start_angle)
        extent_rad = math.radians(extent)
        
        # Draw arc
        self.loading_canvas.create_arc(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            start=start_angle, extent=extent,
            outline="#3b8ed0", width=3, style="arc"
        )
        
        # Update angle for next frame
        self.loading_angle = (self.loading_angle + 10) % 360
        
        # Schedule next animation frame
        self.root.after(50, self.animate_loading)
    
    def get_weather(self):
        city_name = self.search_var.get()
        if not city_name:
            messagebox.showerror("Error", "Please enter a city name")
            return
        
        # Update status
        self.status_bar.configure(text=f"Getting weather data for {city_name}...")
        
        # Start loading animation
        self.start_loading_animation()
        
        # Start a separate thread for API call
        threading.Thread(target=self._fetch_weather_data, args=(city_name,), daemon=True).start()
    
    def _fetch_weather_data(self, city_name):
        try:
            # Get city name (before the comma)
            city_part = city_name.split(",")[0].strip()
            
            # API call
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_part}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            data = response.json()
            
            if data.get("cod") != "200":
                # Stop loading animation
                self.root.after(0, self.stop_loading_animation)
                self.root.after(0, lambda: self.status_bar.configure(text="Ready"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Couldn't find weather data for {city_name}"))
                return
            
            # Store data and city name
            self.weather_data = data
            self.selected_city = city_name
            
            # Update UI in the main thread
            self.root.after(0, self.display_weather_info)
            self.root.after(0, self.visualize_weather)
            self.root.after(0, self.stop_loading_animation)
            self.root.after(0, lambda: self.status_bar.configure(text=f"Weather data loaded for {city_name}"))
            
        except Exception as e:
            # Stop loading animation
            self.root.after(0, self.stop_loading_animation)
            self.root.after(0, lambda: self.status_bar.configure(text="Error occurred"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
    
    def display_weather_info(self):
        if not self.weather_data:
            return
        
        # Enable text widget for editing
        self.weather_details.configure(state="normal")
        
        # Clear previous content
        self.weather_details.delete("0.0", "end")
        
        # Get current weather (first item in the list)
        current = self.weather_data["list"][0]
        city_info = self.weather_data["city"]
        
        # Get weather icon
        main_weather = current["weather"][0]["main"]
        icon = self.weather_icons.get(main_weather, "🌡️")
        self.weather_icon_label.configure(text=icon)
        
        # Format text with proper indentation for sections
        weather_desc = current["weather"][0]["description"].capitalize()
        temp = current["main"]["temp"]
        feels_like = current["main"]["feels_like"]
        
        # Add city and time info
        self.weather_details.insert("end", f"{city_info['name']}, {city_info['country']}\n", "city")
        self.weather_details.insert("end", f"{datetime.fromtimestamp(current['dt']).strftime('%A, %d %B %Y, %H:%M')}\n\n", "date")
        
        # Weather condition
        self.weather_details.insert("end", f"{weather_desc}\n\n", "desc")
        
        # Temperature
        self.weather_details.insert("end", f"Temperature: {temp:.1f}°C\n", "temp")
        self.weather_details.insert("end", f"Feels like: {feels_like:.1f}°C\n\n", "feels")
        
        # Other details
        self.weather_details.insert("end", f"Humidity: {current['main']['humidity']}%\n", "detail")
        self.weather_details.insert("end", f"Wind: {current['wind']['speed']} m/s\n", "detail")
        
        if "rain" in current and "3h" in current["rain"]:
            self.weather_details.insert("end", f"Rain (3h): {current['rain']['3h']} mm\n", "detail")
        
        pressure = current["main"]["pressure"]
        self.weather_details.insert("end", f"Pressure: {pressure} hPa\n\n", "detail")
        
        # 5-day forecast summary
        self.weather_details.insert("end", "5-Day Forecast:\n", "subtitle")
        
        # Get one forecast per day (noon)
        daily_forecasts = []
        forecast_days = set()
        
        for item in self.weather_data["list"]:
            forecast_date = datetime.fromtimestamp(item["dt"])
            day_key = forecast_date.strftime("%Y-%m-%d")
            forecast_hour = forecast_date.hour
            
            # Try to get forecasts around noon
            if day_key not in forecast_days and (11 <= forecast_hour <= 14):
                forecast_days.add(day_key)
                daily_forecasts.append(item)
            
            # Stop after getting 5 days
            if len(daily_forecasts) >= 5:
                break
        
        # If we couldn't get 5 days, just get the first forecast of each day
        if len(daily_forecasts) < 5:
            forecast_days = set()
            daily_forecasts = []
            
            for item in self.weather_data["list"]:
                forecast_date = datetime.fromtimestamp(item["dt"])
                day_key = forecast_date.strftime("%Y-%m-%d")
                
                if day_key not in forecast_days:
                    forecast_days.add(day_key)
                    daily_forecasts.append(item)
                
                if len(daily_forecasts) >= 5:
                    break
        
        # Display daily forecasts with weather icons
        for forecast in daily_forecasts:
            date = datetime.fromtimestamp(forecast["dt"]).strftime("%a, %d %b")
            temp = forecast["main"]["temp"]
            weather_main = forecast["weather"][0]["main"]
            weather_desc = forecast["weather"][0]["description"].capitalize()
            icon = self.weather_icons.get(weather_main, "🌡️")
            
            self.weather_details.insert("end", f"{date}: {icon} {temp:.1f}°C, {weather_desc}\n", "forecast")
        
        # Configure text tags
        self.weather_details.tag_config("city", font=ctk.CTkFont(size=18, weight="bold"))
        self.weather_details.tag_config("date", font=ctk.CTkFont(size=12))
        self.weather_details.tag_config("desc", font=ctk.CTkFont(size=16, weight="bold"))
        self.weather_details.tag_config("temp", font=ctk.CTkFont(size=14))
        self.weather_details.tag_config("feels", font=ctk.CTkFont(size=14))
        self.weather_details.tag_config("detail", font=ctk.CTkFont(size=14))
        self.weather_details.tag_config("subtitle", font=ctk.CTkFont(size=16, weight="bold"))
        self.weather_details.tag_config("forecast", font=ctk.CTkFont(size=14))
        
        # Disable editing
        self.weather_details.configure(state="disabled")
    
    def visualize_weather(self):
        if not self.weather_data:
            return
        
        # Extract data for visualization
        dates, temps, humidities = [], [], []
        for entry in self.weather_data["list"][:8]:  # Next 24 hours (8 data points, 3 hours apart)
            dt = datetime.fromtimestamp(entry["dt"])
            dates.append(dt)
            temps.append(entry["main"]["temp"])
            humidities.append(entry["main"]["humidity"])
        
        # Clear previous plot
        for widget in self.plot_container.winfo_children():
            widget.destroy()
        
        # Create a new figure
        fig = plt.Figure(figsize=(8, 6), dpi=100)
        # Set background color based on theme
        if self.current_theme == "dark":
            fig.patch.set_facecolor("#2b2b2b")
        else:
            fig.patch.set_facecolor("#f0f0f0")
            
        fig.subplots_adjust(bottom=0.2)
        
        # Set Seaborn style for plots
        sns.set_theme(style="darkgrid")
        
        # Create subplot
        ax = fig.add_subplot(111)
        
        # Set text color based on theme
        text_color = "white" if self.current_theme == "dark" else "black"
        
        # Plot temperature
        ax.plot(dates, temps, label="Temperature (°C)", marker='o', color="#3b8ed0", linewidth=2)
        
        # Plot humidity on secondary y-axis
        ax2 = ax.twinx()
        ax2.plot(dates, humidities, label="Humidity (%)", marker='s', color="#e74c3c", linewidth=2)
        ax2.set_ylabel("Humidity (%)", color="#e74c3c")
        ax2.tick_params(axis='y', labelcolor="#e74c3c")
        
        # Update colors based on theme
        ax.set_title(f"Weather Forecast for {self.selected_city}", fontsize=14, fontweight='bold', color=text_color)
        ax.set_xlabel("Date & Time", color=text_color)
        ax.set_ylabel("Temperature (°C)", color="#3b8ed0")
        ax.tick_params(axis='y', labelcolor="#3b8ed0")
        ax.tick_params(axis='x', labelcolor=text_color)
        
        # Format x-axis labels
        ax.set_xticks(dates)
        ax.set_xticklabels([dt.strftime("%H:%M\n%d %b") for dt in dates], rotation=45, ha='right')
        
        # Add weather icons to x-axis labels
        for i, date in enumerate(dates):
            weather_main = self.weather_data["list"][i]["weather"][0]["main"]
            icon = self.weather_icons.get(weather_main, "🌡️")
            ax.annotate(icon, (date, min(temps)), textcoords="offset points", 
                        xytext=(0, -30), ha='center', fontsize=12)
        
        # Combine legends
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper center', 
                  bbox_to_anchor=(0.5, -0.15), ncol=2, facecolor=fig.get_facecolor(), 
                  labelcolor=text_color)
        
        # Draw canvas with animation
        canvas = FigureCanvasTkAgg(fig, master=self.plot_container)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Animate the chart appearing
        canvas_widget.update()
        
        # Create a simple fade-in effect
        for alpha in range(0, 11):
            # Use a safe background color instead of _fg_color
            canvas_widget.update()
            time.sleep(0.03)
    
    def export_to_csv(self):
        if not self.weather_data or not self.selected_city:
            messagebox.showerror("Error", "No weather data to export")
            return
        
        try:
            # Create filename from city name
            safe_city_name = self.selected_city.replace(',', '').replace(' ', '_')
            filename = f"{safe_city_name}_forecast.csv"
            
            # Write to CSV
            with open(filename, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["DateTime", "Temperature (°C)", "Humidity (%)", "Weather", "Wind Speed (m/s)"])
                
                for entry in self.weather_data["list"]:
                    dt = datetime.fromtimestamp(entry["dt"])
                    temp = entry["main"]["temp"]
                    humidity = entry["main"]["humidity"]
                    weather = entry["weather"][0]["description"]
                    wind_speed = entry["wind"]["speed"]
                    
                    writer.writerow([dt, temp, humidity, weather, wind_speed])
            
            self.status_bar.configure(text=f"Weather data exported to {filename}")
            messagebox.showinfo("Success", f"Weather data exported to {filename}")
            
        except Exception as e:
            self.status_bar.configure(text="Export failed")
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")


if __name__ == "__main__":
    root = ctk.CTk()
    app = ModernWeatherDashboard(root)
    root.mainloop()