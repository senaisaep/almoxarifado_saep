from flask import Flask, render_template
from controllers.sistema_controller import sistema
from controllers.auth_controller import auth


app = Flask(__name__)

app.secret_key = 'sua_chave_secreta_aqui'

app.register_blueprint(auth)
app.register_blueprint(sistema)

@app.errorhandler(403)
def erro_403(erro):
    return render_template(
        "erro403.html"
    ), 403


if __name__ == "__main__":
    app.run(debug=True)
