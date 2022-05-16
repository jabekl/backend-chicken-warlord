import gzip
import io
import typing

from starlette.datastructures import URL, Headers, MutableHeaders
from starlette.responses import PlainTextResponse, RedirectResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class CheckHost:
	def __init__(self, app: ASGIApp, allowed_hosts: typing.Optional[typing.Sequence[str]] = None, www_redirect: bool = True):
		if allowed_hosts is None:
			allowed_hosts = ["*"]

		for pattern in allowed_hosts:
			assert "*" not in pattern[1:], "Domain wildcard patterns must be like '*example.com'."
			if pattern.startswith("*") and pattern != "*":
				assert pattern.startswith(
				    "*."), "Domain wildcard patterns must be like '*example.com'."

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
				www_redirect_found = True

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


class GZipHandler:
	def __init__(
        self, app: ASGIApp, minimum_size: int = 500, compresslevel: int = 9):
		self.app = app
		self.minimum_size = minimum_size
		self.compresslevel = compresslevel

	async def __call__(self, scope: Scope, receive: Receive, send: Send):
		if scope["type"] == "http":
			headers = Headers(scope=scope)
			if "gzip" in headers.get("Accept-Encoding", ""):
				responder = _GZipResponder(
                    self.app, self.minimum_size, compresslevel=self.compresslevel
                )
				await responder(scope, receive, send)
				return
		await self.app(scope, receive, send)

class _GZipResponder:
	def __init__(self, app: ASGIApp, minimum_size: int, compresslevel: int = 9):
		self.app = app
		self.minimum_size = minimum_size
		self.send: Send = unattached_send
		self.inital_message: Message = {}
		self.started = False
		self.gzip_buffer = io.BytesIO()
		self.gzip_file = gzip.GzipFile(
			mode="wb", fileobj=self.gzip_buffer, compresslevel=compresslevel
		)

	async def __call__(self, scope: Scope, receive: Receive, send: Send):
		self.send = send
		await self.app(scope, receive, self.send_gzip)
	
	async def send_gzip(self, message: Message = Message):
		message_type = message["type"]
		if message_type == "http.response.start":
			self.inital_message = message
		
		elif message_type == "http.response.body" and not self.started:
			self.started = True
			body = message.get("body", b"")
			m_body = message.get("more_body", False)

			if len(body) < self.minimum_size and not m_body:
				await self.send(self.inital_message)
				await self.send(message)
			
			elif not m_body:
				self.gzip_file.write(body)
				self.gzip_file.close()
				body = self.gzip_buffer.getvalue()

				headers = MutableHeaders(raw=self.inital_message["headers"])
				headers["Content-Encoding"] = "gzip"
				headers["Content-Length"] = str(len(body))
				headers.add_vary_header("Accept-Encoding")
				message["body"] = body

				await self.send(self.inital_message)
				await self.send(message)
			
			else:
				headers = MutableHeaders(raw=self.inital_message["headers"])
				headers["Content-Encoding"] = "gzip"
				headers.add_vary_header("Accept-Encoding")
				del headers["Content-Length"]

				self.gzip_file.write(body)
				message["body"] = self.gzip_buffer.getvalue()
				self.gzip_buffer.seek(0)
				self.gzip_buffer.truncate()

				await self.send(self.inital_message)
				await self.send(message)
		
		elif message_type == "http.response.body":
			body = message.get("body", b"")
			m_body = message.get("m_body", False)

			self.gzip_file.write(body)
			if not m_body:
				self.gzip_file.close()

			message["body"] = self.gzip_buffer.getvalue()
			self.gzipbuffer.seek(0)
			self.gzip_buffer.truncate()

			await self.send(message)

async def unattached_send(message: Message):
	raise RuntimeError("send awaitable not set")
