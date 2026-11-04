# 📦 StockFlow

### Sistema de Gerenciamento de Estoque

O **StockFlow** é um sistema web para gerenciamento de produtos e controle de estoque, desenvolvido com Python e Flask. O projeto utiliza arquitetura MVC combinada com Service Layer, buscando manter o código organizado, modular e de fácil manutenção.

---

## 🚀 Tecnologias

- **Python** — Linguagem principal.
- **Flask** — Framework web.
- **SQLite** — Banco de dados relacional.
- **HTML5** — Estrutura das páginas.
- **CSS3** — Estilização da interface.
- **Werkzeug** — Hash e verificação de senhas.

---

## ✨ Funcionalidades

- [x] Autenticação de usuários.
- [x] Gerenciamento de sessões.
- [x] Controle de acesso por perfil.
- [x] Listagem de produtos.
- [x] Cadastro de produtos para administradores.
- [x] Validação de dados na camada de serviço.
- [x] Persistência de dados com SQLite.
- [x] Proteção de rotas para usuários não autenticados.
- [ ] Atualização de produtos pela interface.
- [ ] Exclusão de produtos pela interface.
- [ ] Controle de movimentações de estoque.
- [ ] Gerenciamento de usuários pela interface.
- [ ] Relatórios de estoque.

---

## 🏗️ Arquitetura

O projeto utiliza uma organização baseada em **MVC + Service Layer**.

```text
sistema_estoque/
│
├── app.py
├── banco.py
│
├── controllers/
│   ├── auth_controller.py
│   └── produto_controller.py
│
├── models/
│   ├── auth_models.py
│   └── estoque_models.py
│
├── services/
│   ├── auth_service.py
│   └── produto_service.py
│
├── templates/
│   ├── login.html
│   └── produtos.html
│
├── static/
│   └── css/
│       └── style.css
│
├── testes/
│   └── test_sistema.py
│
├── requirements.txt
└── .gitignore
```

### Responsabilidades das camadas

| Camada | Responsabilidade |
|---|---|
| Controllers | Receber requisições HTTP e controlar respostas. |
| Services | Aplicar regras de negócio, validações e permissões. |
| Models | Executar operações de persistência no banco de dados. |
| Templates | Renderizar as interfaces HTML. |
| Static | Armazenar arquivos CSS e outros recursos estáticos. |
| Banco | Gerenciar conexões e inicialização do SQLite. |

---

## 🔐 Controle de acesso

O sistema trabalha com dois perfis:

**Administrador**
- Pode cadastrar produtos.
- Possui permissões administrativas sobre os produtos.

**Operador**
- Pode consultar os produtos cadastrados.
- Não possui permissões administrativas para cadastrar produtos.

As permissões são verificadas na camada de serviços, evitando depender apenas das restrições visuais da interface.

---

## ⚙️ Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/joabefg/sistema_estoque.git
```

### 2. Entre na pasta

```bash
cd sistema_estoque
```

### 3. Crie um ambiente virtual

```bash
python3 -m venv .venv
```

### 4. Ative o ambiente virtual

Linux:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

### 5. Instale as dependências

```bash
pip install -r requirements.txt
```

### 6. Inicialize o banco de dados

```bash
python3 banco.py
```

### 7. Execute a aplicação

```bash
python3 app.py
```

Acesse no navegador:

```text
http://127.0.0.1:5000
```

---

## 🗄️ Banco de dados

O projeto utiliza SQLite e possui três estruturas principais:

- `usuarios`: armazenamento dos usuários e seus respectivos perfis.
- `produtos`: informações dos produtos e quantidades disponíveis.
- `movimentacoes`: registro de entradas e saídas de produtos.

As senhas são armazenadas utilizando hash, em vez de texto puro.

---

## 🛠️ Desenvolvimento

Este projeto está em desenvolvimento e tem como objetivo aplicar conceitos de:

- Arquitetura MVC.
- Separação de responsabilidades.
- Programação orientada a objetos e modularização.
- Operações CRUD.
- Autenticação e autorização.
- Persistência de dados.
- Validação de regras de negócio.

---

## 📌 Status

**Em desenvolvimento.**

Novas funcionalidades e melhorias arquiteturais serão implementadas progressivamente.

---

## 👨‍💻 Autor

**Victor Merencio**

Desenvolvedor em formação, interessado em desenvolvimento de sistemas, engenharia de software e segurança de aplicações.

GitHub: [@victor-sysdev](https://github.com/victor-sysdev)

---

*StockFlow — Organização e controle para uma gestão de estoque mais eficiente.*
