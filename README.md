# 🌿 Agro-Defender: Mission Rescue

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9.0-green?logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.30-orange)
![Pygame](https://img.shields.io/badge/Pygame-2.6.1-yellow)

**Agro-Defender: Mission Rescue** is an interactive, real-time Human-Computer Interaction (HCI) game powered by Computer Vision. Designed as a gamified spin-off of agricultural AI research (AgriScan AI), players must physically use their hands to crush falling pests and protect the virtual mother plant. 

This project was developed specifically to be showcased at the Yachay Tech University Open House, targeting a 6th-grade high school audience. It emphasizes zero-calibration gameplay, high-speed interaction, and educational engagement.

## ✨ Features

* **Controller-Free Interaction:** Utilizes `MediaPipe Hands` to track the player's palms in real-time, mapping their physical movements to the virtual game space.
* **High-Performance Architecture:** Implements a multi-threaded Producer-Consumer pattern. The Computer Vision inference runs on an asynchronous background Worker, allowing the Pygame engine (the Broker) to maintain a smooth 60 FPS rendering loop without stuttering.
* **Zero Calibration:** Instantly detects hands upon entering the frame, making it robust for continuous, fast-paced use by multiple users in an exhibition setting.

## ⚙️ Technical Architecture

To bypass the bottleneck of camera capture latency (typically ~30 FPS), the system decouples vision processing from the rendering engine:

1. **Vision Worker (Thread):** Captures frames via OpenCV, processes hand landmarks via MediaPipe, normalizes coordinates, and securely updates a shared state.
2. **Game Broker (Main Thread):** Runs the Pygame loop at a strict 60 FPS, managing sprites, collision detection (Euclidean distance/IoU), physics, and rendering.

## 🚀 Installation & Setup

**1. Clone the repository:**

```bash
git clone [https://github.com/ErickOlivo/agro_defender.git](https://github.com/ErickOlivo/agro_defender.git)
cd agro_defender
```

**2. Create and activate a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

**4. Run the game:**

```bash
python main.py
```
## 🎮 How to Play
1. Step in front of the webcam.

2. Raise your hands to control the on-screen virtual shields.

3. Move your hands quickly to crush the falling pests before they reach the plant at the bottom of the screen.

4. Survive for 60 seconds!

🛠️ Built With
* Python - Core logic

* Pygame - 2D Rendering and Audio Engine

* OpenCV - Video capture and image processing

* MediaPipe - Real-time pose and hand landmark estimation
