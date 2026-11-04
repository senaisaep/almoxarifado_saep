# SIMULADO SAEP — API de Almoxarifado

## Como começar

### 1. Instale o ambiente virtual

```
python -m venv venv
```

### 2. Ative o ambiente virtual

```
source venv\Scripts\activate
```

### 3. Instale as dependências

```
pip install -r requirements.txt
```

### 4. Rode o servidor

```
uvicorn main:app --reload
```

### 5. Acesse o Swagger

## http://127.0.0.1:8000/docs

### Leia o enunciado completo antes de começar!

O arquivo do enunciado contém todas as instruções, tabelas, rotas e o checklist de testes.

<-----------------------------------------------------------------------------------------> 
Clone o repositório:
git clone https://github.com/MMVonnSeek/senai-simulado-saep.git


==========================================================================================
-- Leia o enunciado anexado --
==========================================================================================


CONFIGURAÇÃO DE AMBIENTE
Instale a venv:
python -m venv venv

Ative a venv:
source venv/Scripts/activate

Com o venv ativo instale as dependências: 
python -m pip install fastapi uvicorn sqlalchemy python-dotenv email-validator

Instale o requirements.txt 
python -m pip freeze > requirements.txt  

Habilite o servidor
uvicorn main:app --reload


SUBIR PROJETO PARA O GITHUB
⚠️Antes de executar os comando abaixo verifique se o terminal está na pasta principal do projeto.

git init

git add .

git commit -m "COMENTÁRIO DESCRITIVO"

git push origin main
