python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller==6.10.0

# Ajuste o caminho se necessário
$ENTRY = "GAPP.py"

pyinstaller `
  --name "Horizon Setup" `
  --onefile `
  --windowed `
  --hidden-import lxml `
  --hidden-import html5lib `
  --hidden-import bs4 `
  --paths . `
  $ENTRY
