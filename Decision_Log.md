# Decision Log: Aerial GCP Pose Estimation

## 1. Network Architecture Choice & Rationale

**Architecture:** Multi-task EfficientNetV2-S (Pretrained on ImageNet)
*   **Shared Backbone:** `efficientnetv2_rw_t` (EfficientNetV2 Tiny) acts as the feature extractor.
*   **Regression Head:** Global average pooling followed by fully connected layers and a Sigmoid activation to predict normalized $(x, y)$ coordinates.
*   **Classification Head:** Fully connected layers to predict the shape class (`Cross`, `Square`, `L-Shape`).

**Rationale:**
*   **Multi-Task Learning:** Both tasks (localizing the marker and determining its shape) rely on the exact same visual features. A shared backbone is much more computationally efficient and allows the model to learn synergistic feature representations.
*   **EfficientNetV2:** Provided the best accuracy-to-efficiency trade-off. Given hardware constraints (4GB VRAM), I had to heavily downscale the images to 384x384. EfficientNetV2 learns rich features efficiently, allowing for a decent batch size without running out of memory.
*   **Regression over Heatmaps:** With exactly one keypoint per image, direct coordinate regression is simpler, faster, and avoids the heavy upsampling layers required by heatmap-based methods like HRNet or U-Net.

## 2. Training Strategy & Data Handling

**Data Augmentation:**
*   Applied to simulate drone flight variance: Horizontal/Vertical Flips, small rotations (±15°), and slight affine transformations.
*   Applied to simulate lighting/weather variance: Random brightness/contrast, Hue/Saturation shifts, Gaussian blur, and Gaussian noise.
*   *Excluded:* Aggressive cropping (which might crop out the marker entirely) and large rotations (which could make L-shapes ambiguous).

**Handling Dataset Characteristics:**
*   **Class Imbalance:** EDA showed an imbalance (~49% L-Shape, 33% Square, 18% Cross). This was mitigated using a PyTorch `WeightedRandomSampler` to ensure uniform class sampling during training.
*   **Image Resolutions:** Images were extremely large (4096x2730). Since I lacked the compute to train at full resolution or implement a sliding-window approach, images were resized to 384x384. The coordinates were normalized to a `[0, 1]` range relative to their original dimensions to maintain consistency regardless of aspect ratios.

**Loss Functions & Optimization:**
*   **Localization Loss:** Used **WingLoss** instead of standard L1/L2. Wing loss is highly robust to noisy annotations and performs exceptionally well for facial/keypoint landmark localization.
*   **Classification Loss:** Cross-Entropy Loss with label smoothing (0.1) to prevent overconfidence.
*   **Optimizer:** AdamW with OneCycleLR scheduler for fast convergence.

## 3. Challenges & Mitigations

1.  **Hardware Constraints & Resolution:** The 4096px images were too large to process natively on my GPU. Downscaling to 384px meant the GCP markers became just a few pixels wide, making precise localization difficult. *Mitigation:* Used WingLoss to aggressively penalize small localization errors and combined it with mixed-precision training to maximize batch size.
2.  **Dataset Noise:** 4 images were missing shape labels (`verified_shape`). These were programmatically filtered out during the dataset preparation phase.

## 4. Instructions for Inference

1.  Ensure you have the required dependencies installed (e.g., `torch`, `torchvision`, `timm`, `albumentations`, `opencv-python`).
2.  Place the raw test images in the `GCP_Assignment_Datasets/test_dataset/` directory.
3.  Place the best model weights (`best_model.pt`) in the `checkpoints/` directory.
4.  Run the final cells of the `CV.ipynb` notebook (under the "Test Inference & JSON Export" section).
5.  The script will iterate through the test dataset, generate predictions, scale them back to the original image dimensions, and save the result as `predictions.json` in the current directory.

*Note: Model weights can be downloaded from [INSERT_DRIVE_LINK_HERE]*

## 5. Error Analysis & Critical Fixes

Following the initial model training and evaluation, an extensive error analysis was conducted. We discovered and mitigated several critical issues causing inaccurate coordinate predictions:

*   **Double-Scaling of Keypoints:** The dataset class was manually scaling down the original `(x, y)` coordinates to match the 384x384 resized image. However, the Albumentations pipeline was automatically rescaling these already-scaled keypoints again, clustering the ground-truth targets into a tiny 36x24 pixel area in the top-left corner.
*   **Wing Loss Normalization Mismatch:** The default `WingLoss` parameters were designed for absolute pixel distances. Because we were operating in a normalized `[0, 1]` coordinate space, the loss effectively degenerated into a smooth L1 loss, neutralizing the intended benefits of WingLoss.
*   **Distorted Validation Metrics:** Validation metrics (like PCK) were originally validating against the incorrectly scaled coordinates. As the model only needed to predict within a small bounding box, it incorrectly appeared highly accurate during training, masking the underlying double-scaling bug.
*   **Taxonomy Fixes:** The classification output incorrectly remapped "L-Shape" to "L-Shaped", which would have caused formatting mismatches during final evaluations against the ground truth labels.

These findings resulted in correcting the dataset scaling behavior, adjusting the Wing Loss hyperparameters for `[0, 1]` domains, and fixing string formats for classification labels.
