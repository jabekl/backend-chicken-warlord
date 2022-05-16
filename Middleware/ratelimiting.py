from piccolo_api.rate_limiting.middleware import (InMemoryLimitProvider,
                                                  RateLimitProvider, RateLimitError)
from starlette.middleware.base import (BaseHTTPMiddleware, Request,
                                       RequestResponseEndpoint)
from starlette.responses import Response
from starlette.types import ASGIApp


class RateLimiting(BaseHTTPMiddleware):
	"""
	Limits requests per client in a given time.
	
	limit = max limits in timespan
	timespan = time in seconds
	block_duration = blocking time after too many requests in second
	"""
	def __init__(self, app: ASGIApp, provider: RateLimitProvider = InMemoryLimitProvider(limit=2, timespan=1, block_duration=60)):
		super().__init__(app)
		self.rate_limit = provider

	async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
		identifier = request.client.host
		try: 
			self.rate_limit.increment(identifier)
		except RateLimitError:
			return Response(content="Too many requests", status_code=429)
		return await call_next(request)
