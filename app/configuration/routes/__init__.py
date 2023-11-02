from app.configuration.routes.routes import *
# from app.internal.routes import catalog
from app.internal.routes import users

__routes__ = Routes(routers=(users.router,))
