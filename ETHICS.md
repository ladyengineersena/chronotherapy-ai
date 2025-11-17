# Ethics and Legal Guidelines

## âš ï¸ IMPORTANT WARNINGS

**This is a research prototype. NOT FOR CLINICAL USE.**

- Model outputs are for research and decision-support only
- Never use model recommendations to automatically change treatment plans
- All clinical decisions must be made by qualified healthcare providers
- Real patient data requires IRB approval before use

## Data Privacy and Protection

### Protected Health Information (PHI)

- **NEVER** upload PHI to GitHub or any public repository
- All example data in this repository is **synthetic only**
- Real patient data must be stored securely with encryption
- Follow HIPAA guidelines for data handling (if applicable)

## Consent Requirements

### For Wearable/Active Monitoring Data

If collecting wearable device data (actigraphy, HR, etc.), informed consent must include:

- **What data is collected**: Activity, sleep, heart rate, etc.
- **How it will be used**: Research purposes, model training
- **Storage duration**: How long data will be retained
- **Data sharing**: Whether data will be shared (anonymized) for research
- **Right to withdraw**: Patients can opt out at any time

## Clinical Constraints and Safety

### Model Limitations

- Models are trained on historical data and may not generalize
- Circadian patterns vary significantly between individuals
- Treatment timing is only one factor affecting outcomes
- Other clinical factors (drug interactions, comorbidities) must be considered

### Safety Guardrails

1. **Hard Constraints**
   - Never suggest dosing times outside clinic operating hours
   - Respect standard-of-care treatment windows
   - Consider patient schedules and preferences
   - Account for drug-specific timing requirements

2. **Uncertainty Handling**
   - High uncertainty predictions should trigger expert review
   - Model confidence scores must be displayed to clinicians
   - Fallback to standard scheduling when model is uncertain

3. **Exploration Limits**
   - Bandit exploration must be constrained to clinically acceptable shifts (Â±4 hours)
   - Require clinician opt-in for experimental timing
   - Monitor for adverse events closely during exploration

## Fairness and Equity

### Subgroup Analysis

Model performance must be evaluated across:

- **Age groups**: Young vs. elderly patients
- **Sex/Gender**: Male vs. female
- **Ethnicity/Race**: Ensure no bias
- **Work schedules**: Day workers vs. shift workers
- **Socioeconomic factors**: Access to care, adherence

## Regulatory Considerations

### Research Phase

- Current status: Research/proof-of-concept
- No regulatory approval required for research use
- IRB approval sufficient for data collection

### Clinical Deployment (Future)

If considering clinical deployment:

- **FDA (US)**: Medical device regulations may apply
- **CE Mark (EU)**: Medical device directive compliance
- **Clinical validation**: Prospective studies required
- **Post-market surveillance**: Ongoing monitoring

---

**Last Updated**: 2024
**Status**: Research Prototype
