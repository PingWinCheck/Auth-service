from unittest.mock import patch
from uuid import uuid4

import pytest
from jwt import ExpiredSignatureError, InvalidSignatureError

from custom_auth.utils import JWT, TokenGenerator
from core.settings import settings
from freezegun import freeze_time
import pdb


class TestJWT:
    new_jwt = JWT(algorithm='RS256',
                  key=settings.jwt.private_key,
                  public_key=settings.jwt.public_key)
    payload = {'sub': '123',
               'email': 'zxc@asd.qwe'}

    def test_jwt_encode_decode(self):
        encode = self.new_jwt.encode(payload=self.payload,
                                expire_seconds=200)
        decode = self.new_jwt.decode(encode)
        assert all(item in decode.items() for item in self.payload.items())

    @freeze_time('2020-01-01 12:00:00')
    def test_jwt_encode_decode_expire(self):
        encode = self.new_jwt.encode(payload=self.payload,
                                expire_seconds=60)
        with freeze_time('2020-01-01 12:01:01'):
            with pytest.raises(ExpiredSignatureError, match="Signature has expired"):
                self.new_jwt.decode(encode)

    def test_jwt_invalid_signature_decode(self):
        with pytest.raises(InvalidSignatureError, match='Signature verification failed'):
            self.new_jwt.decode('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTc0NTYxNjk3N30.XW_R-rOZst0PoWo5VkFuTJ3Lt6SsJv8hZ3d4hY49bVBnCppkTfQDT5YH1RI4nzegXn_ogqMPRhapquG_MjVGw9tDeaXZAy1fXjvF9D4me-0DjLLJu1KoMi8ThOL2TmWXFbMtjbIN6o-4WGmLHbPeg-qgxjmgdveFuVToLJm9qvrYe_6vjEN7SWA2Iw8nsyLQxOcr0v96zSHSt2fK7PiZNd0jFknbg4yphPQw2daFqzkh9b_LEViOOPmyRs4O5T3950gS0Axi4ta4O_5GC7E_1LWdLv93HzBUDrXPx9gDIg979Qq-rErh9JBt9JNZcXLTJJzgIJrrNsfbbPT1aKb9Gg')


class TestTokenGenerator:
    uuid_str = str(uuid4())
    payload = {'sub': uuid_str,
               'email': 'zxc@asd.qwe'}
    token_gen = TokenGenerator()

    @freeze_time('1970-01-01 00:01:05')
    def test_create_access_token(self):
        access_token = self.token_gen.create_access_token(payload=self.payload)
        decode = self.token_gen.jwt_manager.decode(access_token)
        assert len(decode.keys()) == 5
        assert decode['sub'] == self.payload['sub']
        assert decode['email'] == self.payload['email']
        assert decode['iat'] == 65
        assert decode['exp'] == 65 + settings.jwt.expire_access_token_seconds
        assert decode['token_type'] == 'access'
        with pytest.raises(KeyError):
            a = decode['jti']

    @patch('custom_auth.utils.uuid4')
    @freeze_time('1970-01-01 00:01:05')
    def test_create_refresh_token(self, mock_uuid4):
        mock_uuid4.return_value = 'qwerty'  # мок для jti
        refresh_token = self.token_gen.create_refresh_token(payload=self.payload)
        decode = self.token_gen.jwt_manager.decode(refresh_token)
        assert len(decode) == 6
        assert decode['sub'] == self.payload['sub']
        assert decode['email'] == self.payload['email']
        assert decode['iat'] == 65
        assert decode['exp'] == 65 + settings.jwt.expire_refresh_token_seconds
        assert decode['jti'] == 'qwerty'
        assert decode['token_type'] == 'refresh'

    @patch('custom_auth.utils.uuid4')
    @freeze_time('1970-01-01 00:01:05')
    def test_create_access_refresh_tokens_pair(self, mock_uuid4):
        mock_uuid4.return_value = self.uuid_str
        token = self.token_gen.create_access_refresh_tokens_pair(self.payload)
        assert token.token_type == 'Bearer'
        decode_access = self.token_gen.jwt_manager.decode(token.access_token)
        assert len(decode_access.keys()) == 5
        assert decode_access['sub'] == self.payload['sub']
        assert decode_access['email'] == self.payload['email']
        assert decode_access['iat'] == 65
        assert decode_access['exp'] == 65 + settings.jwt.expire_access_token_seconds
        assert decode_access['token_type'] == 'access'
        with pytest.raises(KeyError):
            a = decode_access['jti']

        decode_refresh = self.token_gen.jwt_manager.decode(token.refresh_token)

        assert len(decode_refresh) == 6
        assert decode_refresh['sub'] == self.payload['sub']
        assert decode_refresh['email'] == self.payload['email']
        assert decode_refresh['iat'] == 65
        assert decode_refresh['exp'] == 65 + settings.jwt.expire_refresh_token_seconds
        assert decode_refresh['jti'] == self.uuid_str
        assert decode_refresh['token_type'] == 'refresh'
