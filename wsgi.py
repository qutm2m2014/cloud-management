from manager import create_app
# from werkzeug.contrib.profiler import ProfilerMiddleware

app = create_app()
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

if __name__ == '__main__':
    app.run()
