# Aerial GCP Pose Estimation

## Overview
This project implements a multi-task deep learning model to accurately localize Ground Control Points (GCPs) and classify their shapes from high-resolution aerial drone imagery. Given a top-down image, the model predicts the normalized `(x, y)` coordinates of the GCP and categorizes its shape into one of three classes: `Cross`, `Square`, or `L-Shape`.

## Project Structure
- `CV.ipynb`: The main Jupyter Notebook containing the end-to-end pipeline, including Data Loading, Exploratory Data Analysis (EDA), Model Definition (EfficientNetV2-S backbone), Training, Validation, and Test Inference.
- `Decision_Log.md`: A detailed log of the architectural decisions, loss function choices, and training strategies.
- `error_analysis.md`: A deep dive into the root causes of initial prediction errors, including double-scaling of keypoints and loss normalization mismatches.
- `predictions.json`: The final output of the model on the test dataset containing predicted coordinates and shapes.

## Installation

1. Create and activate a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage
1. Ensure the dataset is located in the `GCP_Assignment_Datasets` folder.
2. Run the `CV.ipynb` notebook to execute the full pipeline.
3. Model checkpoints will be saved to the `checkpoints/` directory.
4. Final test set predictions will be generated as `predictions.json` in the root directory.

## Model Architecture
- **Backbone**: EfficientNetV2 Tiny (`efficientnetv2_rw_t`) pretrained on ImageNet.
- **Regression Head**: Predicts continuous `(x, y)` coordinates normalized to a `[0, 1]` range.
- **Classification Head**: Predicts the shape category (`Cross`, `Square`, `L-Shape`).

## Evaluation
The model's localization performance is evaluated using the Percentage of Correct Keypoints (PCK) metric, while classification accuracy is evaluated using the Macro F1-Score.
