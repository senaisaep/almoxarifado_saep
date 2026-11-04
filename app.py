from flask import Flask, render_template
from controllers.auth_controller import auth

app = Flask(__name__)

app.secret_key ="chave_secreta"
app.register_blueprint(auth)
@app.errorhandler(403)
def erro_403(erro):
    return render_template(
        "error403.html"
    ),403


app.run(debug=True)


