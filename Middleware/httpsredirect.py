from starlette.datastructures import URL
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class HTTPSRedirect:
	"""
	Enforces that all incoming requests must either be HTTPS or WSS.
	Redirects if necessary.
	"""

	def __init__(self, app: ASGIApp):
		self.app = app

	async def __call__(self, scope: Scope, recieve: Receive, send: Send):
		if scope["type"] in ["http", "websocket"] and scope["scheme"] in ["http", "ws"]:
			url = URL(scope=scope)
			redirect_scheme = {"http": "https", "ws": "wss"}[url.scheme]

			if url.port in ["80", "443"]:
				net = url.hostname
			else:
				net = url.netloc

			url = url.replace(scheme=redirect_scheme, netloc=net)

			response = RedirectResponse(url, status_code=307)
			await response(scope, recieve, send)
		else:
			await self.app(scope, recieve, send)

