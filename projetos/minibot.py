from difflib import SequenceMatcher

palavra_chave = "amoxicilina"

usr = input("Digite a palavra: ")

score = SequenceMatcher(None, usr, palavra_chave).ratio()
print(f"O score é {score:.2f}")

# if usr.lower() == palavra_chave: -> muito mais difícil
if score >= 0.8:
    print("entendi")
else:
    print("não entendi")


####
# Frase: o seu serviço foi excelente! Muito obrigado por tudo.
#        - Positiva -> Nós que agredecemos pela escolha! Ficamos feliz pela satisfação.
# Frase: Estou desapontado com o serviço oferecido. Nada funcionou.
#        - Negativa -> Sentimos muito pela sua experiência! Nos contate para tentarmos uma solução.
####

pontuacao = 0

palavras = {
    "excelente": 1,
    "obrigado": 1,
    "agradecemos": 1,
    "desapontado": -1,
    "nada": -1,
    "falha": -1
}

# Olhar palavra por palavra, e identificar o sentimento

palavra = "excelente"
if palavra in palavras:
    pontuacao += palavras[palavra] # pontuacao = pontuacao + palavras["excelente"]