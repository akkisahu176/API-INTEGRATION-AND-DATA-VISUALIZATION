# 🌦️ Smart Weather Dashboard using OpenWeather API

A sleek, interactive weather dashboard built with **Python**, leveraging the **OpenWeatherMap API** to provide 5-day forecasts for cities across the globe. The application uses `customtkinter` for a modern GUI and `matplotlib/seaborn` for beautiful data visualizations.

**GitHub Repository Name:** `API-INTEGRATION-AND-DATA-VISUALIZATION`

---

## 🚀 Features

* 🔍 **Smart City Search**
  Autocomplete city suggestions with sorted dropdown list.

* 📈 **Data Visualization**
  Forecast data (temperature and humidity) displayed using **Matplotlib** and **Seaborn**.

* ⏳ **Loading Spinner**
  A simple loading indicator while data is being fetched.

* 📄 **Export to CSV**
  Weather forecast can be saved locally as a CSV file for further analysis.

* 🎛️ **Modern UI**
  Built using `customtkinter` for a stylish and responsive user interface.

---

## 🛠️ Tech Stack

* **Python**
* **Tkinter** & **CustomTkinter**
* **Matplotlib** / **Seaborn**
* **Requests**
* **OpenWeatherMap API**

---

## 📸 Screenshots

1. **Initial Interface**

    *Dark version*
  ![Screenshot 2025-05-21 002042](https://github.com/user-attachments/assets/c9561e5f-6348-4e5f-a17f-98155d62d078)


    *Light version*  
  ![Screenshot 2025-05-21 002051](https://github.com/user-attachments/assets/04bff5f6-1d77-4749-9f4b-1199f58f1114)

2. **Entering City Name**

    *Dark version*
![Screenshot 2025-05-21 002147](https://github.com/user-attachments/assets/2d5e5152-d31a-4be7-87a0-c948570efc22)

3. **Final fetching and result**

    *Dark version*
   ![Screenshot 2025-05-21 002159](https://github.com/user-attachments/assets/5f0e17e1-20f3-441d-a457-270a27f21602)
   
   *Light version*  
   ![image](https://github.com/user-attachments/assets/e6e33de0-7266-4fc7-a636-a93fc136ae85)




---
🎬 Demo

Below is a GIF demonstration of the application in action:

![Working](https://github.com/user-attachments/assets/d2ab39a7-3ca5-4502-9600-f5b79d87c34e)

---

## 📦 Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/API-INTEGRATION-AND-DATA-VISUALIZATION.git
cd API-INTEGRATION-AND-DATA-VISUALIZATION
```

2. **Set up virtual environment (recommended)**

```bash
python -m venv apienv
apienv\Scripts\activate  # On Windows
# OR
source apienv/bin/activate  # On Mac/Linux
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Create a .env file to store your API key (DO NOT hardcode) **

```text
# .env
OPENWEATHER_API_KEY=your_api_key_here
```

> ℹ️ **Note on .gitignore:** This project includes a `.gitignore` file that ensures sensitive files like `.env` and the virtual environment directory `apienv/` are excluded from version control. This is a professional practice to keep credentials secure and repositories lightweight.

5. Run the application

```bash
python weather_dashboard.py
```
> ⚠️ Note: city.list.json is downloaded automatically on first run from OpenWeatherMap’s sample file archive to avoid large file uploads in the repository.
---

## 📁 Project Structure

```
API-INTEGRATION-AND-DATA-VISUALIZATION/
├── city.list.json          # List of cities (from OpenWeatherMap)(will be downloaded automatiacally on first execution)
├── weather_dashboard.py    # Main application script
├── .env                    # Contains your API key (DO NOT UPLOAD)
├── .gitignore              # Includes .env and apienv/
├── requirements.txt        # List of required Python packages
├── README.md               # Project description
├── LICENSE.txt             # MIT License
```

---

## 📃 License

This project is licensed under the **MIT License** — feel free to use and modify.

---

## 🙌 Acknowledgements

* [OpenWeatherMap API](https://openweathermap.org/api)
* [Matplotlib](https://matplotlib.org/)
* [Seaborn](https://seaborn.pydata.org/)
* [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* [python-dotenv](https://pypi.org/project/python-dotenv/)

---

Made with ❤️ by Akhil Sahu
