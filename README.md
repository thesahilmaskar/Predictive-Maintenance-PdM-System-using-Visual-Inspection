Predictive Maintenance PdM System Using Visual Inspection

A hybrid predictive maintenance web application designed to help small and medium-scale industries transition from reactive or schedule-based upkeep to a proactive, data-driven approach—without requiring expensive sensor infrastructure.

🔍 Project Overview

This system integrates three input modes—manual parameters, vibration audio, and surface images—to evaluate machine health. It combines rule-based logic, a Random Forest classifier, and YOLOv8 object detection to flag early signs of wear, such as cracks, rust, and abnormal vibrations.

⚙️ Features

Manual Data Entry: Input temperature, humidity, vibration magnitude, power usage, and machine type.

Vibration Analysis: Upload MATLAB .mat vibration recordings; extract time- and frequency-domain features; classify with Random Forest.

Visual Defect Detection: Upload images of machine surfaces; detect cracks and corrosion using YOLOv8.

Unified Diagnostic Report: If any modality flags an anomaly, the system marks the equipment as “Needs Maintenance”; otherwise, it reports “Normal.”

User-Friendly Web Interface: Built with Flask, HTML, Bootstrap; compatible with desktops and mobile devices.

🏗️ Architecture

Data Input Layer

Manual parameter form

Image upload endpoint

Vibration file upload endpoint

Processing & Analysis Layer

Rule-Based Checker for manual inputs

Random Forest pipeline for audio features

YOLOv8 object detector for surface images

Output Layer

Aggregates results

Displays status and recommendations in the dashboard

📦 Project Structure

├── app/                     # Flask application package
│   ├── static/              # CSS, JS, images
│   ├── templates/           # HTML templates
│   ├── models/              # Pre-trained models (YOLOv8, RF scaler)
│   ├── utils/               # Data preprocessing and helpers
│   └── routes.py            # Flask routes (auth, predict, detect)
├── data/                    # Example datasets and sample inputs
├── notebooks/               # Development and training notebooks
├── requirements.txt         # Python dependencies
├── README.md                # Project overview (this file)
└── run.py                   # Entry point to launch the server

🚀 Installation

Clone the repository

git clone https://github.com/thesahilmaskar/Predictive-Maintenance-PdM-System-using-Visual-Inspection.git
cd Predictive-Maintenance-PdM-System-using-Visual-Inspection

Create a virtual environment

python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate    # Windows

Install dependencies

pip install -r requirements.txt

Prepare models

Place pretrained YOLOv8 weights and the Random Forest model (with scaler) under app/models/.

🖥️ Usage

Run the server

python run.py

Open your browser at http://localhost:5000.

Authenticate (Register/Login).

Select input mode:

Manual Entry: Fill out the form and submit.

Image Upload: Choose an image file and click Detect.

Vibration Upload: Upload .mat file and click Predict.

View results: The dashboard shows "Normal" (✅) or "Needs Maintenance" (⚠️) and detailed recommendations.

📚 Methodology

Data Collection: Supports CSV entries, images, and .mat files.

Preprocessing:

CSV: Clean and normalize values.

Images: Resize, normalize, augment for YOLOv8.

Audio: Extract RMS, FFT, spectral features.

Modeling:

Random Forest for vibration classification.

YOLOv8 for crack and corrosion detection.

Inference: Combine modality outputs for final status.



