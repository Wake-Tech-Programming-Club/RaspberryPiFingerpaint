# 🎨 Finger Painting

Paint a masterpiece with nothing but your finger and a webcam!

---

## 🛠️ Tech Stack
- **Backend:** Python
- **Computer Vision:** OpenCV, MediaPipe

---

## 📥 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Wake-Tech-Programming-Club/RaspberryPiFingerpaint.git
   cd RaspberryPiFingerpaint
   ```

2. **Set up a virtual environment** *(recommended, but not required)*:
   ```bash
   python -m venv .venv
   source venv/bin/activate  # On macOS/Linux
   .\.venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create your configuration file**:
   Make a copy of `config-example.ini` called `config.ini`.

4. **Run the server**:
   ```bash
   python app.py
   ```

---

## 🖌️ How to Paint
1. Stand in front of the camera
2. Move your index finger around the camera frame to draw a picture
3. Press "C" to clear the drawing
4. Enjoy the challenge!

---

## 🛠️ Troubleshooting

- **Gesture sensitivity too high?**
  - Adjust the **min_detection** and **min_tracking** values in `config.ini`.

- **Wrong camera?**
  - Change the value of `camera_id` in `config.ini` and restart. Keep trying until you find the right camera.

- **Can't run the program at all?**
  - Check that there is an output folder and that the readme file's name is changed to z-readme.md

---


## 📜 License

This project is licensed under the **MIT License** – feel free to modify and enhance it!

---

## 🤝 Contributing

Have ideas or improvements? Fork the repository and submit a pull request! 🎉
