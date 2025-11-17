"""
Synthetic data generator for chronotherapy AI project.
Simulates patient circadian profiles, treatment times, and outcomes.
"""
import numpy as np
import pandas as pd
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import json


class SyntheticCohortGenerator:
    """Generate synthetic patient cohort with circadian and treatment data."""
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)
    
    def generate_patient_demographics(self, n_patients: int) -> pd.DataFrame:
        """Generate patient demographic and clinical data."""
        patients = []
        
        for i in range(n_patients):
            age = self.rng.normal(60, 15)
            age = max(25, min(85, age))
            
            patient = {
                'patient_id': f'P{i:04d}',
                'age': int(age),
                'sex': self.rng.choice(['M', 'F']),
                'ecog_score': self.rng.choice([0, 1, 2], p=[0.4, 0.4, 0.2]),
                'bmi': self.rng.normal(25, 5),
                'cancer_type': self.rng.choice(['breast', 'lung', 'colorectal', 'prostate']),
                'stage': self.rng.choice(['II', 'III', 'IV']),
                'comorbidities': self.rng.choice([0, 1, 2], p=[0.5, 0.3, 0.2]),
            }
            patients.append(patient)
        
        return pd.DataFrame(patients)
    
    def generate_circadian_profile(self, patient_id: str, n_days: int = 30) -> Dict:
        """Generate circadian rhythm data for a patient."""
        # Sleep midpoint varies by patient (night owls vs early birds)
        sleep_midpoint = self.rng.normal(3.0, 1.5)  # Hours (0-24)
        sleep_midpoint = (sleep_midpoint % 24)
        
        # Sleep duration
        sleep_duration = self.rng.normal(7.5, 1.0)
        sleep_duration = max(5.0, min(10.0, sleep_duration))
        
        # Generate daily actigraphy data
        timestamps = []
        activities = []
        heart_rates = []
        sleep_starts = []
        sleep_ends = []
        
        base_date = pd.Timestamp('2024-01-01')
        
        for day in range(n_days):
            date = base_date + pd.Timedelta(days=day)
            
            # Sleep times
            sleep_start_hour = (sleep_midpoint - sleep_duration/2) % 24
            sleep_end_hour = (sleep_midpoint + sleep_duration/2) % 24
            
            sleep_start = date.replace(hour=int(sleep_start_hour), 
                                      minute=int((sleep_start_hour % 1) * 60))
            sleep_end = date.replace(hour=int(sleep_end_hour), 
                                    minute=int((sleep_end_hour % 1) * 60))
            
            if sleep_end < sleep_start:
                sleep_end += pd.Timedelta(days=1)
            
            sleep_starts.append(sleep_start)
            sleep_ends.append(sleep_end)
            
            # Hourly actigraphy (24 hours per day)
            for hour in range(24):
                ts = date.replace(hour=hour, minute=0)
                
                # Activity: low during sleep, higher during day
                hour_of_day = hour
                if sleep_start_hour < sleep_end_hour:
                    is_sleep = sleep_start_hour <= hour_of_day < sleep_end_hour
                else:
                    is_sleep = hour_of_day >= sleep_start_hour or hour_of_day < sleep_end_hour
                
                if is_sleep:
                    activity = self.rng.exponential(5)
                else:
                    # Circadian activity pattern (peak around afternoon)
                    phase = (hour_of_day - sleep_end_hour) % 24
                    activity_base = 50 + 30 * np.sin(2 * np.pi * phase / 24 + np.pi/2)
                    activity = max(0, self.rng.normal(activity_base, 10))
                
                # Heart rate: lower during sleep
                if is_sleep:
                    hr = self.rng.normal(55, 5)
                else:
                    hr = self.rng.normal(70, 10)
                
                timestamps.append(ts)
                activities.append(activity)
                heart_rates.append(hr)
        
        actigraphy = pd.DataFrame({
            'timestamp': timestamps,
            'activity': activities,
            'hr': heart_rates
        })
        
        sleep_data = pd.DataFrame({
            'timestamp': sleep_starts,
            'sleep_start': sleep_starts,
            'sleep_end': sleep_ends
        })
        
        return {
            'patient_id': patient_id,
            'sleep_midpoint': sleep_midpoint,
            'sleep_duration': sleep_duration,
            'actigraphy': actigraphy,
            'sleep_data': sleep_data
        }
    
    def generate_treatment_episodes(
        self, 
        patient_id: str,
        n_treatments: int,
        circadian_profile: Dict
    ) -> pd.DataFrame:
        """Generate treatment episodes with timing and outcomes."""
        treatments = []
        
        sleep_midpoint = circadian_profile['sleep_midpoint']
        
        for i in range(n_treatments):
            # Treatment time (clinician-chosen, may be suboptimal)
            # Bias: most treatments happen 9-17 (clinic hours)
            clinic_hour = self.rng.normal(13, 2)  # Peak around 1 PM
            clinic_hour = max(8, min(17, clinic_hour))
            
            # Some variation
            treatment_hour = self.rng.normal(clinic_hour, 1.5)
            treatment_hour = max(6, min(20, treatment_hour))
            
            treatment_date = pd.Timestamp('2024-01-15') + pd.Timedelta(days=i*21)  # ~3 week cycles
            
            # Drug type
            drug_type = self.rng.choice(['platinum', 'taxane', 'anthracycline'])
            dose = self.rng.uniform(0.8, 1.2)  # Relative to standard dose
            
            # Outcome depends on circadian timing relative to patient's rhythm
            # Optimal time is typically 4-6 hours after sleep midpoint
            optimal_time = (sleep_midpoint + 5) % 24
            time_offset = abs((treatment_hour - optimal_time + 12) % 24 - 12)  # Circular distance
            
            # Efficacy: higher when closer to optimal time
            efficacy_base = 0.5
            efficacy_boost = max(0, 1 - time_offset / 6) * 0.3  # Max 0.3 boost
            efficacy = min(1.0, efficacy_base + efficacy_boost + self.rng.normal(0, 0.1))
            
            # Toxicity: also depends on timing, but different pattern
            # Higher toxicity when treatment is during vulnerable phase
            vulnerable_phase = (sleep_midpoint + 2) % 24  # Early morning
            toxicity_offset = abs((treatment_hour - vulnerable_phase + 12) % 24 - 12)
            toxicity_base = 0.3
            toxicity_penalty = max(0, 1 - toxicity_offset / 4) * 0.4
            toxicity = min(1.0, toxicity_base + toxicity_penalty + self.rng.normal(0, 0.1))
            
            # Tumor response (binary)
            response = 1 if efficacy > 0.6 else 0
            
            # Toxicity grade (0-4)
            if toxicity < 0.3:
                grade = 0
            elif toxicity < 0.5:
                grade = 1
            elif toxicity < 0.7:
                grade = 2
            elif toxicity < 0.85:
                grade = 3
            else:
                grade = 4
            
            treatment = {
                'patient_id': patient_id,
                'treatment_id': f'{patient_id}_T{i+1}',
                'treatment_date': treatment_date,
                'treatment_hour': treatment_hour,
                'drug_type': drug_type,
                'dose': dose,
                'efficacy_score': efficacy,
                'toxicity_score': toxicity,
                'response': response,
                'toxicity_grade': grade,
                'tumor_shrinkage_pct': max(0, min(100, efficacy * 100 + self.rng.normal(0, 10)))
            }
            treatments.append(treatment)
        
        return pd.DataFrame(treatments)
    
    def generate_lab_data(
        self,
        patient_id: str,
        treatment_episodes: pd.DataFrame
    ) -> pd.DataFrame:
        """Generate laboratory time series data."""
        labs = []
        
        for _, treatment in treatment_episodes.iterrows():
            # Pre-treatment labs
            for days_before in [7, 3, 1]:
                lab_date = treatment['treatment_date'] - pd.Timedelta(days=days_before)
                labs.append({
                    'patient_id': patient_id,
                    'date': lab_date,
                    'wbc': self.rng.normal(6.0, 2.0),
                    'hemoglobin': self.rng.normal(12.0, 2.0),
                    'platelets': self.rng.normal(250, 80),
                    'creatinine': self.rng.normal(1.0, 0.3),
                    'alt': self.rng.normal(30, 15),
                })
            
            # Post-treatment labs (affected by toxicity)
            for days_after in [3, 7, 14]:
                lab_date = treatment['treatment_date'] + pd.Timedelta(days=days_after)
                toxicity = treatment['toxicity_score']
                
                # Labs worsen with toxicity
                wbc = max(2.0, self.rng.normal(6.0 - toxicity * 3, 1.5))
                hemoglobin = max(8.0, self.rng.normal(12.0 - toxicity * 2, 1.5))
                platelets = max(50, self.rng.normal(250 - toxicity * 100, 50))
                
                labs.append({
                    'patient_id': patient_id,
                    'date': lab_date,
                    'wbc': wbc,
                    'hemoglobin': hemoglobin,
                    'platelets': platelets,
                    'creatinine': self.rng.normal(1.0, 0.3),
                    'alt': self.rng.normal(30 + toxicity * 10, 15),
                })
        
        return pd.DataFrame(labs)
    
    def generate_cohort(
        self,
        n_patients: int,
        n_treatments_per_patient: int = 4,
        n_days_circadian: int = 30
    ) -> Dict:
        """Generate complete synthetic cohort."""
        print(f"Generating {n_patients} patients...")
        
        # Demographics
        demographics = self.generate_patient_demographics(n_patients)
        
        # Per-patient data
        circadian_profiles = []
        all_treatments = []
        all_labs = []
        
        for _, patient in demographics.iterrows():
            patient_id = patient['patient_id']
            
            # Circadian profile
            circadian = self.generate_circadian_profile(patient_id, n_days_circadian)
            circadian_profiles.append(circadian)
            
            # Treatments
            treatments = self.generate_treatment_episodes(
                patient_id,
                n_treatments_per_patient,
                circadian
            )
            all_treatments.append(treatments)
            
            # Labs
            labs = self.generate_lab_data(patient_id, treatments)
            all_labs.append(labs)
        
        # Combine
        all_treatments_df = pd.concat(all_treatments, ignore_index=True)
        all_labs_df = pd.concat(all_labs, ignore_index=True)
        
        return {
            'demographics': demographics,
            'circadian_profiles': circadian_profiles,
            'treatments': all_treatments_df,
            'labs': all_labs_df
        }
    
    def save_cohort(self, cohort: Dict, output_dir: Path):
        """Save cohort data to files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save demographics
        cohort['demographics'].to_csv(
            output_dir / 'demographics.csv',
            index=False
        )
        
        # Save treatments
        cohort['treatments'].to_csv(
            output_dir / 'treatments.csv',
            index=False
        )
        
        # Save labs
        cohort['labs'].to_csv(
            output_dir / 'labs.csv',
            index=False
        )
        
        # Save circadian profiles (as JSON for nested structure)
        circadian_data = []
        for profile in cohort['circadian_profiles']:
            circadian_data.append({
                'patient_id': profile['patient_id'],
                'sleep_midpoint': profile['sleep_midpoint'],
                'sleep_duration': profile['sleep_duration'],
                'actigraphy': profile['actigraphy'].to_dict('records'),
                'sleep_data': profile['sleep_data'].to_dict('records')
            })
        
        with open(output_dir / 'circadian_profiles.json', 'w') as f:
            json.dump(circadian_data, f, default=str, indent=2)
        
        # Save summary
        summary = {
            'n_patients': len(cohort['demographics']),
            'n_treatments': len(cohort['treatments']),
            'n_labs': len(cohort['labs']),
        }
        
        with open(output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Saved cohort to {output_dir}")
        print(f"  - {len(cohort['demographics'])} patients")
        print(f"  - {len(cohort['treatments'])} treatments")
        print(f"  - {len(cohort['labs'])} lab records")


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic chronotherapy cohort')
    parser.add_argument('--out', type=str, default='data/synthetic',
                       help='Output directory')
    parser.add_argument('--n_patients', type=int, default=200,
                       help='Number of patients')
    parser.add_argument('--n_treatments', type=int, default=4,
                       help='Number of treatments per patient')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed')
    
    args = parser.parse_args()
    
    generator = SyntheticCohortGenerator(seed=args.seed)
    cohort = generator.generate_cohort(
        n_patients=args.n_patients,
        n_treatments_per_patient=args.n_treatments
    )
    
    output_dir = Path(args.out)
    generator.save_cohort(cohort, output_dir)


if __name__ == '__main__':
    main()