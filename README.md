# TITAN - NRL Tipping Machine Learning Project

## How it Works

1. **Fetches match data** (dummy for now, real data later).
2. **Predicts winners** (home team tipped for now).
3. **Saves tips to Excel file** (`outputs/titan_tips.xlsx`).

## How to Run

- Open a terminal.
- Navigate to the TITAN project folder.
- Run the command:  
python titan_main.py
- Check the `outputs/` folder for the tips file!

## Next Steps

- Upgrade `titan_fetch.py` to scrape live NRL data.
- Build a smarter ML model in `titan_model.py`.
- Add a basic Flask web dashboard (`titan_webapp.py`).
