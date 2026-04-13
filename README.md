# LifeSpanAI

A predictive maintenance dashboard for turbofan engine Remaining Useful Life (RUL) prediction using advanced deep learning models.

##  Features

- **Interactive Dashboard**: Streamlit-based web interface for real-time RUL predictions
- **Multiple Datasets**: Support for NASA C-MAPSS FD001-FD004 datasets with different operational conditions
- **Advanced Models**: Hybrid Transformer-LSTM and pure Transformer architectures
- **Feature Importance**: Permutation-based feature importance analysis
- **Q&A Engine**: Natural language interface for model and dataset queries
- **Real-time Visualization**: Sensor degradation trends and prediction comparisons

##  Dataset

This project uses the NASA C-MAPSS (Commercial Modular Aero-Propulsion System Simulation) dataset, which contains simulated turbofan engine degradation data under various operational conditions:

- **FD001**: One operational condition, one fault mode
- **FD002**: Six operational conditions, one fault mode
- **FD003**: One operational condition, two fault modes
- **FD004**: Six operational conditions, two fault modes

Each dataset includes:
- Training data: Run-to-failure trajectories
- Test data: Partial trajectories with unknown RUL
- Ground truth RUL values for evaluation

##  Architecture

### Models
- **Transformer-only**: Pure attention-based architecture for sequence modeling
- **Hybrid Transformer-LSTM**: Combines self-attention with temporal dependencies

### Key Components
- **Data Loader**: Preprocesses C-MAPSS data with sliding window approach (30 cycles)
- **Model Engine**: TensorFlow/Keras-based prediction models
- **Dashboard**: Streamlit web application with interactive visualizations
- **Q&A Engine**: Context-aware question answering system

##  Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/LifeSpanAI.git
cd LifeSpanAI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download the NASA C-MAPSS dataset and place it in `dashboard/data/CMaps/`

4. Place trained model files in `dashboard/assets/` directory

##  Usage

### Running the Dashboard

```bash
cd dashboard
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

### Dashboard Features

1. **Dataset Selection**: Choose from FD001-FD004 subsets
2. **Engine Analysis**: Select specific engines for detailed analysis
3. **Sensor Monitoring**: Visualize sensor degradation over time
4. **RUL Prediction**: View predicted vs. actual remaining useful life
5. **Feature Importance**: Understand which sensors contribute most to predictions
6. **Q&A Interface**: Ask questions about the model and dataset

##  Project Structure

```
LifeSpanAI/
├── README.md
├── requirements.txt
├── dashboard/
│   ├── app.py                 # Main Streamlit application
│   ├── data_loader.py         # Data preprocessing utilities
│   ├── model.py              # Model loading and prediction functions
│   ├── qa_engine.py          # Question-answering system
│   ├── check.py              # Validation utilities
│   ├── assets/               # Trained model files (.h5)
│   └── data/
│       └── CMaps/            # NASA C-MAPSS dataset files
└── models/                   # Model training scripts (if available)
```

##  Dependencies

- **streamlit**: Web application framework
- **tensorflow**: Deep learning framework
- **numpy**: Numerical computing
- **pandas**: Data manipulation
- **scikit-learn**: Machine learning utilities
- **matplotlib**: Data visualization
- **seaborn**: Statistical visualization
- **shap**: Model interpretability (optional)

##  Model Performance

The models are trained to predict RUL with a cap of 125 cycles. Performance metrics include:

- Root Mean Square Error (RMSE)
- Mean Absolute Error (MAE)
- Score function (asymmetric penalty for late predictions)

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Acknowledgments

- NASA for providing the C-MAPSS dataset
- The turbofan engine simulation community for benchmark datasets
- TensorFlow and Keras for deep learning frameworks

##  Contact

For questions or support, please open an issue on GitHub.