from app import create_app
from flask_toastr import Toastr

app = create_app()
app.secret_key = 'd775576e42b85da57ae1a0c0bf288f57a7418da44b70af6f618b3292d9177d81'
toastr = Toastr(app)

if __name__ == '__main__':
    # from waitress import serve
    # serve(app)
    #app.run(debug=True)
    app.run(debug=True, host='localhost', port=5000)
