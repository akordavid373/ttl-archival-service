"""
API Gateway Authentication Proxy Module

Handles authentication delegation, token validation, and
identity management for the gateway.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import httpx
import jwt
import hashlib
import hmac
import base64
from urllib.parse import urlparse, parse_qs
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class AuthType(Enum):
    """Authentication types"""
    JWT = "jwt"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC = "basic"
    OPAQUE = "opaque"
    NONE = "none"


class AuthStrategy(Enum):
    """Authentication strategies"""
    FORWARD = "forward"  # Forward auth headers to backend
    VALIDATE = "validate"  # Validate and replace with internal auth
    DELEGATE = "delegate"  # Delegate to external auth service
    HYBRID = "hybrid"  # Combination of strategies


@dataclass
class AuthProvider:
    """Authentication provider configuration"""
    name: str
    auth_type: AuthType
    strategy: AuthStrategy
    endpoint: Optional[str] = None  # For delegation
    public_key: Optional[str] = None  # For JWT validation
    secret_key: Optional[str] = None  # For token generation/validation
    issuer: Optional[str] = None  # For JWT validation
    audience: Optional[str] = None  # For JWT validation
    algorithm: str = "HS256"  # For JWT
    token_header: str = "Authorization"  # Header name for token
    token_prefix: str = "Bearer "  # Token prefix
    api_key_header: str = "X-API-Key"  # Header name for API keys
    cache_ttl: int = 300  # Cache TTL for auth results
    timeout: int = 10  # Request timeout
    retries: int = 3  # Retry attempts
    enabled: bool = True


@dataclass
class AuthRule:
    """Authentication rule configuration"""
    name: str
    provider: str
    paths: List[str] = field(default_factory=lambda: ["/*"])
    methods: List[str] = field(default_factory=lambda: ["*"])
    headers: Dict[str, str] = field(default_factory=dict)
    required_scopes: List[str] = field(default_factory=list)
    required_roles: List[str] = field(default_factory=list)
    anonymous_allowed: bool = False
    priority: int = 0
    enabled: bool = True


@dataclass
class AuthContext:
    """Authentication context"""
    authenticated: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    token: Optional[str] = None
    expires_at: Optional[float] = None
    provider: Optional[str] = None


class JWTValidator:
    """JWT token validator"""
    
    def __init__(self, provider: AuthProvider):
        self.provider = provider
        self.public_key = provider.public_key
        self.algorithm = provider.algorithm
        self.issuer = provider.issuer
        self.audience = provider.audience
    
    def validate_token(self, token: str) -> AuthContext:
        """Validate JWT token"""
        try:
            # Decode and validate token
            payload = jwt.decode(
                token,
                self.public_key or self.provider.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience
            )
            
            # Create auth context
            context = AuthContext(
                authenticated=True,
                user_id=payload.get('sub'),
                username=payload.get('preferred_username') or payload.get('name'),
                email=payload.get('email'),
                roles=payload.get('roles', []),
                scopes=payload.get('scope', '').split() if payload.get('scope') else [],
                metadata={k: v for k, v in payload.items() 
                         if k not in ['sub', 'preferred_username', 'name', 'email', 'roles', 'scope', 'exp', 'iat', 'iss', 'aud']},
                token=token,
                expires_at=payload.get('exp'),
                provider=self.provider.name
            )
            
            return context
        
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return AuthContext(authenticated=False)
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return AuthContext(authenticated=False)
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            return AuthContext(authenticated=False)


class APIKeyValidator:
    """API key validator"""
    
    def __init__(self, provider: AuthProvider):
        self.provider = provider
        # In production, this would be stored in a database or secure store
        self.api_keys = {}  # key -> user_info
    
    def add_api_key(self, key: str, user_info: Dict[str, Any]):
        """Add an API key"""
        hashed_key = hashlib.sha256(key.encode()).hexdigest()
        self.api_keys[hashed_key] = user_info
    
    def validate_api_key(self, api_key: str) -> AuthContext:
        """Validate API key"""
        try:
            hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
            
            if hashed_key not in self.api_keys:
                return AuthContext(authenticated=False)
            
            user_info = self.api_keys[hashed_key]
            
            return AuthContext(
                authenticated=True,
                user_id=user_info.get('user_id'),
                username=user_info.get('username'),
                email=user_info.get('email'),
                roles=user_info.get('roles', []),
                scopes=user_info.get('scopes', []),
                metadata=user_info.get('metadata', {}),
                token=api_key,
                provider=self.provider.name
            )
        
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return AuthContext(authenticated=False)


class BasicAuthValidator:
    """Basic authentication validator"""
    
    def __init__(self, provider: AuthProvider):
        self.provider = provider
        # In production, this would validate against a user database
        self.users = {}  # username -> password_hash
    
    def add_user(self, username: str, password: str, user_info: Dict[str, Any]):
        """Add a user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.users[username] = {
            'password_hash': password_hash,
            'user_info': user_info
        }
    
    def validate_basic_auth(self, auth_header: str) -> AuthContext:
        """Validate basic authentication"""
        try:
            # Extract credentials
            if not auth_header.startswith('Basic '):
                return AuthContext(authenticated=False)
            
            credentials = base64.b64decode(auth_header[6:]).decode()
            username, password = credentials.split(':', 1)
            
            # Validate credentials
            if username not in self.users:
                return AuthContext(authenticated=False)
            
            user_data = self.users[username]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if password_hash != user_data['password_hash']:
                return AuthContext(authenticated=False)
            
            user_info = user_data['user_info']
            
            return AuthContext(
                authenticated=True,
                user_id=user_info.get('user_id', username),
                username=username,
                email=user_info.get('email'),
                roles=user_info.get('roles', []),
                scopes=user_info.get('scopes', []),
                metadata=user_info.get('metadata', {}),
                provider=self.provider.name
            )
        
        except Exception as e:
            logger.error(f"Basic auth validation error: {e}")
            return AuthContext(authenticated=False)


class OAuth2Validator:
    """OAuth2 token validator"""
    
    def __init__(self, provider: AuthProvider):
        self.provider = provider
        self.introspection_endpoint = provider.endpoint
        self.client_id = provider.secret_key  # Using secret_key as client_id
    
    async def validate_oauth2_token(self, token: str) -> AuthContext:
        """Validate OAuth2 token via introspection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.introspection_endpoint,
                    data={
                        'token': token,
                        'client_id': self.client_id
                    },
                    timeout=self.provider.timeout
                )
                
                if response.status_code != 200:
                    return AuthContext(authenticated=False)
                
                introspection_result = response.json()
                
                if not introspection_result.get('active'):
                    return AuthContext(authenticated=False)
                
                return AuthContext(
                    authenticated=True,
                    user_id=introspection_result.get('sub'),
                    username=introspection_result.get('username'),
                    email=introspection_result.get('email'),
                    roles=introspection_result.get('roles', []),
                    scopes=introspection_result.get('scope', '').split() if introspection_result.get('scope') else [],
                    metadata={k: v for k, v in introspection_result.items() 
                             if k not in ['active', 'sub', 'username', 'email', 'roles', 'scope']},
                    token=token,
                    expires_at=introspection_result.get('exp'),
                    provider=self.provider.name
                )
        
        except Exception as e:
            logger.error(f"OAuth2 validation error: {e}")
            return AuthContext(authenticated=False)


class AuthDelegator:
    """External authentication delegator"""
    
    def __init__(self, provider: AuthProvider):
        self.provider = provider
        self.endpoint = provider.endpoint
    
    async def delegate_authentication(self, request: Request) -> AuthContext:
        """Delegate authentication to external service"""
        try:
            # Prepare request to auth service
            headers = dict(request.headers)
            headers['X-Forwarded-Host'] = request.headers.get('host', '')
            headers['X-Forwarded-For'] = request.client.host if request.client else ''
            headers['X-Forwarded-Proto'] = request.url.scheme
            headers['X-Original-URI'] = str(request.url)
            headers['X-Original-Method'] = request.method
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.endpoint,
                    headers=headers,
                    timeout=self.provider.timeout
                )
                
                if response.status_code == 200:
                    auth_data = response.json()
                    
                    return AuthContext(
                        authenticated=auth_data.get('authenticated', False),
                        user_id=auth_data.get('user_id'),
                        username=auth_data.get('username'),
                        email=auth_data.get('email'),
                        roles=auth_data.get('roles', []),
                        scopes=auth_data.get('scopes', []),
                        metadata=auth_data.get('metadata', {}),
                        token=auth_data.get('token'),
                        expires_at=auth_data.get('expires_at'),
                        provider=self.provider.name
                    )
                else:
                    return AuthContext(authenticated=False)
        
        except Exception as e:
            logger.error(f"Auth delegation error: {e}")
            return AuthContext(authenticated=False)


class AuthProxy:
    """
    Main authentication proxy class
    """
    
    def __init__(self):
        self.providers: Dict[str, AuthProvider] = {}
        self.rules: List[AuthRule] = []
        self.validators: Dict[str, Any] = {}
        self.delegators: Dict[str, AuthDelegator] = {}
        self.auth_cache: Dict[str, Tuple[AuthContext, float]] = {}
        self.cache_ttl = 300  # 5 minutes default
    
    def add_provider(self, provider: AuthProvider):
        """Add an authentication provider"""
        self.providers[provider.name] = provider
        
        # Initialize appropriate validator
        if provider.auth_type == AuthType.JWT:
            self.validators[provider.name] = JWTValidator(provider)
        elif provider.auth_type == AuthType.API_KEY:
            self.validators[provider.name] = APIKeyValidator(provider)
        elif provider.auth_type == AuthType.BASIC:
            self.validators[provider.name] = BasicAuthValidator(provider)
        elif provider.auth_type == AuthType.OAUTH2:
            self.validators[provider.name] = OAuth2Validator(provider)
        
        # Initialize delegator if needed
        if provider.strategy == AuthStrategy.DELEGATE and provider.endpoint:
            self.delegators[provider.name] = AuthDelegator(provider)
        
        logger.info(f"Auth provider added: {provider.name} ({provider.auth_type.value})")
    
    def remove_provider(self, provider_name: str):
        """Remove an authentication provider"""
        self.providers.pop(provider_name, None)
        self.validators.pop(provider_name, None)
        self.delegators.pop(provider_name, None)
        logger.info(f"Auth provider removed: {provider_name}")
    
    def add_rule(self, rule: AuthRule):
        """Add an authentication rule"""
        self.rules.append(rule)
        # Sort by priority
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"Auth rule added: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """Remove an authentication rule"""
        self.rules = [r for r in self.rules if r.name != rule_name]
        logger.info(f"Auth rule removed: {rule_name}")
    
    async def authenticate(self, request: Request) -> AuthContext:
        """
        Authenticate a request
        """
        # Find applicable rule
        rule = self._find_applicable_rule(request)
        if not rule:
            # No rule applies, allow anonymous
            return AuthContext(authenticated=True, anonymous=True)
        
        # Get provider
        provider = self.providers.get(rule.provider)
        if not provider or not provider.enabled:
            if rule.anonymous_allowed:
                return AuthContext(authenticated=True, anonymous=True)
            else:
                return AuthContext(authenticated=False)
        
        # Check cache
        cache_key = self._get_cache_key(request, provider)
        if cache_key in self.auth_cache:
            context, timestamp = self.auth_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return context
        
        # Authenticate based on strategy
        context = await self._authenticate_with_provider(request, provider, rule)
        
        # Cache result
        self.auth_cache[cache_key] = (context, time.time())
        
        return context
    
    def _find_applicable_rule(self, request: Request) -> Optional[AuthRule]:
        """Find the applicable authentication rule"""
        path = request.url.path
        method = request.method
        headers = dict(request.headers)
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            # Check path
            path_match = False
            for rule_path in rule.paths:
                if rule_path == "/*" or path.startswith(rule_path.rstrip('*')):
                    path_match = True
                    break
            
            if not path_match:
                continue
            
            # Check method
            if "*" not in rule.methods and method not in rule.methods:
                continue
            
            # Check headers
            header_match = True
            for key, value in rule.headers.items():
                if headers.get(key) != value:
                    header_match = False
                    break
            
            if header_match:
                return rule
        
        return None
    
    def _get_cache_key(self, request: Request, provider: AuthProvider) -> str:
        """Generate cache key for authentication"""
        # Extract token from request
        token = self._extract_token(request, provider)
        
        # Create cache key
        key_data = f"{provider.name}:{token}:{request.url.path}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _extract_token(self, request: Request, provider: AuthProvider) -> Optional[str]:
        """Extract authentication token from request"""
        headers = dict(request.headers)
        
        if provider.auth_type == AuthType.JWT or provider.auth_type == AuthType.OAUTH2:
            auth_header = headers.get(provider.token_header, '')
            if auth_header.startswith(provider.token_prefix):
                return auth_header[len(provider.token_prefix):]
        
        elif provider.auth_type == AuthType.API_KEY:
            return headers.get(provider.api_key_header)
        
        elif provider.auth_type == AuthType.BASIC:
            return headers.get(provider.token_header, '')
        
        return None
    
    async def _authenticate_with_provider(self, request: Request, provider: AuthProvider, rule: AuthRule) -> AuthContext:
        """Authenticate using a specific provider"""
        try:
            if provider.strategy == AuthStrategy.DELEGATE:
                delegator = self.delegators.get(provider.name)
                if delegator:
                    context = await delegator.delegate_authentication(request)
                else:
                    context = AuthContext(authenticated=False)
            
            elif provider.strategy in [AuthStrategy.VALIDATE, AuthStrategy.FORWARD, AuthStrategy.HYBRID]:
                validator = self.validators.get(provider.name)
                if not validator:
                    context = AuthContext(authenticated=False)
                elif provider.auth_type == AuthType.OAUTH2:
                    token = self._extract_token(request, provider)
                    if token:
                        context = await validator.validate_oauth2_token(token)
                    else:
                        context = AuthContext(authenticated=False)
                else:
                    context = self._validate_with_validator(request, validator, provider)
            
            else:
                context = AuthContext(authenticated=False)
            
            # Check required scopes and roles
            if context.authenticated:
                if rule.required_scopes and not any(scope in context.scopes for scope in rule.required_scopes):
                    context.authenticated = False
                
                if rule.required_roles and not any(role in context.roles for role in rule.required_roles):
                    context.authenticated = False
            
            return context
        
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return AuthContext(authenticated=False)
    
    def _validate_with_validator(self, request: Request, validator: Any, provider: AuthProvider) -> AuthContext:
        """Validate using appropriate validator"""
        if provider.auth_type == AuthType.JWT:
            token = self._extract_token(request, provider)
            return validator.validate_token(token) if token else AuthContext(authenticated=False)
        
        elif provider.auth_type == AuthType.API_KEY:
            api_key = self._extract_token(request, provider)
            return validator.validate_api_key(api_key) if api_key else AuthContext(authenticated=False)
        
        elif provider.auth_type == AuthType.BASIC:
            auth_header = request.headers.get(provider.token_header, '')
            return validator.validate_basic_auth(auth_header)
        
        return AuthContext(authenticated=False)
    
    async def forward_auth_headers(self, request: Request, context: AuthContext, headers: Dict[str, str]) -> Dict[str, str]:
        """Forward authentication headers to backend service"""
        if not context.authenticated:
            return headers
        
        # Get provider for context
        provider = self.providers.get(context.provider) if context.provider else None
        if not provider:
            return headers
        
        if provider.strategy == AuthStrategy.FORWARD:
            # Forward original auth headers
            for header_name in [provider.token_header, provider.api_key_header]:
                if header_name in request.headers:
                    headers[header_name] = request.headers[header_name]
        
        elif provider.strategy in [AuthStrategy.VALIDATE, AuthStrategy.HYBRID]:
            # Add internal auth headers
            headers['X-User-ID'] = context.user_id or ''
            headers['X-Username'] = context.username or ''
            headers['X-Email'] = context.email or ''
            headers['X-Roles'] = ','.join(context.roles)
            headers['X-Scopes'] = ','.join(context.scopes)
            headers['X-Auth-Provider'] = context.provider or ''
            
            # Add metadata as headers
            for key, value in context.metadata.items():
                if isinstance(value, (str, int, float)):
                    headers[f'X-User-{key.replace('-', '_').title()}'] = str(value)
        
        return headers
    
    def cleanup_cache(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.auth_cache.items()
            if current_time - timestamp > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.auth_cache[key]
    
    def get_auth_stats(self) -> Dict[str, Any]:
        """Get authentication statistics"""
        return {
            'total_providers': len(self.providers),
            'total_rules': len(self.rules),
            'cache_size': len(self.auth_cache),
            'providers': [
                {
                    'name': provider.name,
                    'type': provider.auth_type.value,
                    'strategy': provider.strategy.value,
                    'enabled': provider.enabled
                }
                for provider in self.providers.values()
            ],
            'rules': [
                {
                    'name': rule.name,
                    'provider': rule.provider,
                    'enabled': rule.enabled,
                    'priority': rule.priority,
                    'anonymous_allowed': rule.anonymous_allowed
                }
                for rule in self.rules
            ]
        }


class AuthMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for authentication"""
    
    def __init__(self, app, auth_proxy: AuthProxy):
        super().__init__(app)
        self.auth_proxy = auth_proxy
    
    async def dispatch(self, request: Request, call_next):
        """Process request through authentication"""
        # Authenticate request
        auth_context = await self.auth_proxy.authenticate(request)
        
        # Add auth context to request state
        request.state.auth_context = auth_context
        
        # Check if authentication is required
        if not auth_context.authenticated:
            return Response(
                content=json.dumps({
                    'error': 'Authentication required',
                    'message': 'Invalid or missing authentication credentials'
                }),
                status_code=401,
                media_type='application/json'
            )
        
        # Process the request
        response = await call_next(request)
        
        # Add auth headers to response
        if auth_context.authenticated and not getattr(auth_context, 'anonymous', False):
            response.headers['X-Authenticated-User'] = auth_context.user_id or ''
            response.headers['X-Auth-Provider'] = auth_context.provider or ''
        
        return response


# Global auth proxy instance
auth_proxy = AuthProxy()
