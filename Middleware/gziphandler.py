import gzip
import io

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class GZipHandler:
	"""
	Handles GZip reponses for requests that include 'gzip' in their 'Accept-Encoding' header.
	"""
	def __init__(self, app: ASGIApp, minimum_size: int = 500, compresslevel: int = 9):
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
	"""
	Part of GZipHandler.
	"""
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
