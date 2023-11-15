from app.configuration.routes.routes import *
# from app.internal.routes import catalog
from app.internal.routes import users, leaderboards
from app.internal.utils import auth

__routes__ = Routes(routers=(users.router,leaderboards.router, auth.router))
