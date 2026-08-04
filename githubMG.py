import os

print("Configurando email.")
comando_email = "git config user.email \"20241pvai0030018@estudantes.ifpr.edu.br\""  
os.system(comando_email)

comando1 = "git add *"
os.system(comando1)

mensagem = input("digite seu commit: ")
while(len(mensagem) < 5):
    print("⚠️digite um commit maior que 5 caracteres⚠️")
    mensagem = input("digite seu commit: ")

print("✅ registrando alterações")
comando2 = 'git commit -m "' + mensagem + '"'
os.system(comando2)

comando3 = "git push origin Arcadegarcia"
os.system(comando3)
