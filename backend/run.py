from app import create_app  # type: ignore

app = create_app()  # type: ignore

if __name__ == '__main__':
    app.run(debug=True, port=8000)
