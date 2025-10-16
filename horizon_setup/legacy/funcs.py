import re

import mechanize


# checkData
# This function will check to see if the user has selected "save credentials"
# If they have, it will store the credentials given in the data.dat file, otherwise it will erase that file
def checkData(filename, rememberCredentials, username, password):
	if (rememberCredentials == 1):
		try:
			file = open(filename, "w")
			file.write("1\n")
			file.write(username + "\n")
			file.write(password + "\n")
			file.close()
		except Exception:
			pass
	else:
		try:
			open(filename, "w").close()
		except:
			pass


# checkLogin
# Takes login details and confirms they are correct, warning the user if something is amiss
def checkLogin(username, password):
	# Best read the mechanize documentation for info on how mechanize works.
	# Create a new broser reference
	browser = mechanize.Browser()
	browser.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
	
	# Open the login page and select the login section
	browser.open("https://gpro.net/gb/Login.asp")
	
	# Debug: mostra todos os formulários
	print(f"Formulários encontrados: {len(browser.forms())}")
	for i, form in enumerate(browser.forms()):
		print(f"  Formulário {i}: id='{form.attrs.get('id', 'N/A')}', name='{form.attrs.get('name', 'N/A')}'")
	
	try:
		browser.select_form(id="Form1")
		print("Formulário Form1 encontrado!")
		print(f"browser.form é None? {browser.form is None}")
	except Exception as e:
		print(f"Erro ao selecionar formulário: {e}")
		# Tenta selecionar o primeiro formulário se Form1 não existir
		try:
			browser.select_form(nr=0)
			print("Selecionado primeiro formulário como fallback")
		except Exception as e2:
			print(f"Erro ao selecionar primeiro formulário: {e2}")
			return False
	
	# Verifica se o formulário foi selecionado
	if browser.form is None:
		print("ERRO: browser.form é None após select_form")
		return False
	
	# Debug: mostra todos os campos
	print("Campos do formulário:")
	for control in browser.form.controls:
		print(f"  - {control.name}: {control.value}")
	
	# Input the username and password
	try:
		browser.form["textLogin"] = username.strip()
		browser.form["textPassword"] = password.strip()
		print("Campos preenchidos com sucesso!")
	except Exception as e:
		print(f"Erro ao preencher campos: {e}")
		return False
	
	# Submit the completed page
	browser.submit()
	
	# Debug: verifica a URL após o submit
	current_url = browser.geturl()
	print(f"URL após submit: {current_url}")
	
	# Se ainda está na página de login, o login falhou
	if "Login.asp" in current_url:
		print("Login falhou - ainda na página de login")
		return False
	
	# Se chegou aqui, o login funcionou, mas vamos verificar se há links DriverProfile
	response = list(browser.links(url_regex=re.compile("DriverProfile\\.asp")))
	print(f"Links DriverProfile encontrados: {len(response)}")
	
	# Se não encontrou DriverProfile, vamos ver quais links existem
	if len(response) == 0:
		all_links = list(browser.links())
		print(f"Total de links na página: {len(all_links)}")
		for i, link in enumerate(all_links[:5]):  # Mostra os primeiros 5 links
			print(f"  Link {i}: {link.text} -> {link.url}")
	
	browser.close()

	# At this point, if the login was successful, there should be 1 links with "DriverProfile" in.
	# Mas vamos ser mais flexíveis: se não está na página de login, consideramos sucesso
	return True if "Login.asp" not in current_url else False
