# Chronotherapy-AI

Personalized treatment timing optimizer for cancer therapy using circadian and clinical data.

**Status:** Research prototype â€” Not for clinical use.

## Overview

Chronotherapy-AI is an AI-powered decision-support system designed to optimize drug/treatment timing for cancer patients based on their individual circadian profiles, clinical status, and treatment characteristics. The goal is to increase treatment efficacy while reducing toxicity by identifying the optimal time-of-day for treatment administration.

### Key Features

- **Personalized Timing Recommendations**: AI models predict optimal treatment times for individual patients
- **Circadian Rhythm Analysis**: Extracts features from wearable data (actigraphy, heart rate, sleep patterns)
- **Multiple Modeling Approaches**: 
  - Supervised learning (XGBoost/LightGBM) for baseline predictions
  - Contextual bandits (UCB, Thompson Sampling) for sequential personalization
- **Synthetic Data Generation**: Realistic patient cohort simulation for research and development
- **Comprehensive Evaluation**: Metrics and visualization tools for model performance assessment

## Quickstart

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/ladyengineersena/chronotherapy-ai.git
cd chronotherapy-ai

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Synthetic Data

```bash
python src/data/simulate_cohort.py --out data/synthetic --n_patients 200 --n_treatments 4
```

This will create:
- `data/synthetic/demographics.csv` - Patient demographics and clinical data
- `data/synthetic/treatments.csv` - Treatment episodes with timing and outcomes
- `data/synthetic/labs.csv` - Laboratory time series data
- `data/synthetic/circadian_profiles.json` - Circadian rhythm data

### 3. Run Notebooks

```bash
# Start Jupyter
jupyter notebook

# Open notebooks in order:
# 1. notebooks/01_simulate_data.ipynb - Generate and explore data
# 2. notebooks/02_feature_engineering.ipynb - Extract circadian features
# 3. notebooks/03_supervised_baseline.ipynb - Train supervised models
# 4. notebooks/04_bandit_simulation.ipynb - Simulate contextual bandits
```

## Project Structure

```
chronotherapy-ai/
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ synthetic/          # Generated synthetic data
â”‚   â””â”€â”€ README_DATA.md      # Data documentation
â”œâ”€â”€ notebooks/
â”‚   â”œâ”€â”€ 01_simulate_data.ipynb          # Data generation
â”‚   â”œâ”€â”€ 02_feature_engineering.ipynb    # Feature extraction
â”‚   â”œâ”€â”€ 03_supervised_baseline.ipynb    # Supervised models
â”‚   â””â”€â”€ 04_bandit_simulation.ipynb      # Bandit simulation
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ data/
â”‚   â”‚   â””â”€â”€ simulate_cohort.py          # Synthetic data generator
â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”œâ”€â”€ supervised.py               # XGBoost/LightGBM models
â”‚   â”‚   â””â”€â”€ bandit.py                    # Contextual bandit algorithms
â”‚   â”œâ”€â”€ train.py                         # Training script
â”‚   â”œâ”€â”€ evaluate.py                      # Evaluation script
â”‚   â””â”€â”€ utils.py                         # Utility functions
â”œâ”€â”€ requirements.txt                     # Python dependencies
â”œâ”€â”€ README.md                            # This file
â””â”€â”€ ETHICS.md                            # Ethical guidelines
```

## Usage

### Generate Synthetic Cohort

```bash
python src/data/simulate_cohort.py \
    --out data/synthetic \
    --n_patients 200 \
    --n_treatments 4 \
    --seed 42
```

### Train Supervised Model

```bash
python src/train.py \
    --data_dir data/synthetic \
    --output_dir models \
    --model_type xgboost \
    --target toxicity_grade \
    --n_bins 12
```

### Evaluate Model

```bash
python src/evaluate.py \
    --data_dir data/synthetic \
    --output_dir results \
    --model_type xgboost \
    --target toxicity_grade \
    --n_bins 12
```

## Model Details

### Supervised Models (`src/models/supervised.py`)

- **TimeBinClassifier**: Multi-output classifier predicting best time bin for treatment
  - Supports XGBoost and LightGBM
  - Trains separate models for each time bin (default: 12 bins = 2-hour intervals)
  - Predicts toxicity grade, response, or efficacy scores

### Contextual Bandits (`src/models/bandit.py`)

- **LinearUCBBandit**: Upper Confidence Bound algorithm for explore-exploit
- **ThompsonSamplingBandit**: Bayesian Thompson Sampling for personalized timing
- Learns optimal treatment times through sequential interactions

### Feature Engineering (`src/utils.py`)

- **Circadian Features**: Sleep midpoint, duration, activity amplitude, HR variability
- **Time Normalization**: Aligns timestamps to biological day (anchored to sleep midpoint)
- **Time Binning**: Converts hours to discrete time bins for modeling

## Data Requirements

### Synthetic Data (Included)

The project includes a synthetic data generator that simulates:
- Patient demographics (age, sex, ECOG score, BMI, cancer type, stage)
- Circadian profiles (actigraphy, sleep patterns, heart rate)
- Treatment episodes (timing, drug type, dose, outcomes)
- Laboratory results (CBC, creatinine, liver enzymes)

### Real Data (For Production)

If using real patient data, you need:
- **Circadian/Temporal Data**: Wearable data (actigraphy, HR), sleep logs, time-tagged diaries
- **Clinical Data**: Diagnosis, stage, ECOG, comorbidities, drug type/dose/timing
- **Outcome Data**: Tumor response (RECIST), toxicity (CTCAE), patient-reported outcomes
- **IRB Approval**: Required before using real patient data

## Evaluation Metrics

- **Efficacy**: Probability of response, tumor shrinkage percentage
- **Safety**: Probability of gradeâ‰¥3 toxicity, days with severe adverse events
- **Composite Reward**: Weighted combination (efficacy âˆ’ Î» Ã— toxicity)
- **Bandit Metrics**: Cumulative regret, average reward over time

## Ethics & Legal

âš ï¸ **IMPORTANT**: This is a research prototype. Model outputs are for research purposes only and should NOT be used to direct clinical care.

### Key Requirements:

1. **IRB Approval**: Required before using real patient data
2. **Patient Consent**: Explicit consent needed for wearable/monitoring data
3. **Data Privacy**: No PHI (Protected Health Information) should be stored in this repository
4. **Clinical Constraints**: Model provides decision support only; clinicians make final decisions
5. **Fairness**: Performance should be evaluated across patient subgroups

See [ETHICS.md](ETHICS.md) for detailed guidelines.

## Technical Approach

### Problem Formulation

- **Task A (Classification)**: Predict which time bin yields lowest toxicity / highest efficacy
- **Task B (Regression)**: Predict side effect scores or tumor shrinkage by time
- **Task C (Policy)**: Recommend optimal time + alternatives + confidence intervals
- **Task D (Simulation)**: Simulate RCT outcomes comparing model-guided vs. clinician-chosen times

### Modeling Pipeline

1. **Data Ingestion**: Normalize timestamps to biological day (anchor to sleep midpoint)
2. **Feature Engineering**: Extract circadian features, HR variability, lab trends
3. **Model Training**: 
   - Supervised: Multi-output models per time bin
   - Bandit: Sequential learning with explore-exploit
4. **Uncertainty Quantification**: Bayesian methods, ensembles, MC-Dropout
5. **Explainability**: SHAP values, feature importance, policy explanations

## Dependencies

- Python 3.8+
- numpy >= 1.24.0
- pandas >= 2.0.0
- scikit-learn >= 1.3.0
- xgboost >= 2.0.0
- lightgbm >= 4.0.0
- torch >= 2.0.0 (optional, for future neural models)
- matplotlib >= 3.7.0
- seaborn >= 0.12.0
- jupyter >= 1.0.0
- shap >= 0.42.0

## Contributing

This is a research project. For questions or contributions, please:
1. Review ETHICS.md for ethical guidelines
2. Ensure all data is properly anonymized
3. Follow clinical safety constraints

## Citation

If you use this code in your research, please cite appropriately and acknowledge the ethical considerations outlined in ETHICS.md.

## License

This project is for research purposes only. See ETHICS.md for usage restrictions.

## Contact

For questions about ethical use or clinical deployment, please review ETHICS.md first.

---

**Disclaimer**: This software is provided "as is" for research purposes. The authors and contributors are not responsible for any clinical decisions made using this software. Always consult with qualified healthcare professionals for medical decisions.