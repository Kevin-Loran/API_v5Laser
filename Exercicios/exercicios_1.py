print("Começou")

cursos = [
    {"nome": "Python Básico", "preco": 0, "categoria": "Programação"},
    {"nome": "AWS Practitioner", "preco": 150, "categoria": "Cloud"},
    {"nome": "SQL Completo", "preco": 0, "categoria": "Dados"},
    {"nome": "Java Avançado", "preco": 200, "categoria": "Programação"},
    {"nome": "Linux Essentials", "preco": 0, "categoria": "Infraestrutura"},
    {"nome": "Python Avançado", "preco": 0, "categoria": "Programação"}
]

contador = 0
for item in cursos:
    if item["preco"] == 0 and item["categoria"] == "Programação":
        contador += 1
        print(item["nome"])

print(f"Total de cursos: {contador}")