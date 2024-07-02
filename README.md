# COOPIS2024: Using Eye-tracking to Detect Search and Inference During Process Model Comprehension

### Overview

This directory contains the data collection and analysis material for the CoopIS paper entitled "Using Eye-tracking to Detect Search and Inference During Process Model Comprehension" (by Amine Abbad-Andaloussi, Clemens Schreiber, and Barbara Weber)

### Structure

- Folder [analysis](analysis): contains the Python notebooks for the inductive behavioral analysis and the machine learning (ML) training and validation

  - [Inductive Segmentation.ipynb](analysis/Inductive Segmentation.ipynb): Contains the procedure for the inductive behavioral analysis
  - [ML Training and Validation.ipynb](analysis/ML Training and Validation.ipynb): Contains the procedure for ML training and validation

  - Before running the code make sure the following libraries are installed

    - This project requires the following Python packages:

      - pandas
      - matplotlib
      - seaborn
      - numpy
      - scipy
      - sklearn
      - adjustText

    - You can install these packages using pip. Open your terminal and type the following commands:

      ```bash
      pip install pandas
      pip install matplotlib
      pip install seaborn
      pip install numpy
      pip install scipy
      pip install scikit-learn
      pip install adjustText
      ```
  
- Folder [demographics](demographics): contains demographic information about the participants.

- Folder [figures](figures): contains the figures used in the paper in a larger resolution.

- Folder [material](material): contains the material used for the data collection.

