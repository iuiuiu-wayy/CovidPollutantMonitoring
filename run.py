from projectApp import create_app

server = create_app()
# server = app
if __name__ == '__main__':
    server.run(debug=True)