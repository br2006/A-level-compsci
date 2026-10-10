from app import create_app
from flask import redirect, url_for, flash

app = create_app()

@app.errorhandler(404)
def page_not_found(e):
    flash("page doesn't exist")
    return redirect(url_for('main.index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

