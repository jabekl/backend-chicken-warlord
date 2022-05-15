from email import header
import typing
from urllib import response
from django.shortcuts import redirect

from starlette.datastructures import URL, Headers
from starlette.responses import PlainTextResponse, RedirectResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

DOMAIN_WILDCARD = "Domain wildcard patterns must be like '*example.com'."


class CheckHost:
	def __init__(self, app: ASGIApp, allowed_hosts: typing.Optional[typing.Sequence[str]] = None, www_redirect: bool = True):
		if allowed_hosts is None:
			allowed_hosts = ["*"]

		for pattern in allowed_hosts:
			assert "*" not in pattern[1:], DOMAIN_WILDCARD
			if pattern.startswith("*") and pattern != "*":
				assert pattern.startswith("*."), DOMAIN_WILDCARD
        
		self.app = app
		self.allowed_hosts = list(allowed_hosts)
		self.allow_any = "*" in allowed_hosts
		self.www_redirect = www_redirect

	async def __call__(self, scope: Scope, recieve: Receive, send: Send):
		if self.allow_any or scope["type"] not in ["http", "websocket"]:
			await self.app(scope, recieve, send)
			return
		
		headers = Headers(scope=scope)
		host = headers.get("host", "").split(":")[0]
		is_valid_host = False
		www_redirect_found = False

		for pattern in self.allowed_hosts:
			if host == pattern or (pattern.startswith("*") and host.endswith(pattern[:1])):
				is_valid_host = True
				break
			elif f"www.{host}" == pattern:
				www_redirect_found  = True

			if is_valid_host:
				await self.app(scope, recieve, send)
			else:
				response = Response
				if www_redirect_found and self.www_redirect:
					url = URL(scope=scope)
					redirect_url = url.replace(netloc=f"www.{url.netloc}")
					response = RedirectResponse(url=str(redirect_url))
				else:
					response = PlainTextResponse("Invalid host header", status_code=400)

				await response(scope, recieve, send)

class HTTPSRedirect:
    def __ini__(self, app: ASGIApp):
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
