python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller==6.10.0

pyinstaller `
  --name "Horizon Setup" `
  --onefile `
  --hidden-import lxml `
  --hidden-import html5lib `
  --hidden-import bs4 `
  --paths . `
  horizon_setup/main.py
