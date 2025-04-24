import pytest
from jwt import ExpiredSignatureError, InvalidSignatureError

from custom_auth.utils import JWT
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
        pdb.set_trace()
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
