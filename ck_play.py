import flask

from . import login
from .. import log, web, errors, message
from ..common import Level, Message, Container, int_to_device
import enum


class CKWalletClient(login.WalletClient, web.Repeater):
    _close_round_no_wait = True

    class Methods(enum.Enum):
        """CKPLay URL paths"""
        VALIDATE = '/wallet/validate'
        BALANCE = '/wallet/balance'
        BET = '/wallet/bet'
        WIN = '/wallet/win'
        ENDROUND = '/wallet/endround'
        ENDSESSION = '/wallet/endsession'
        # ROLLBACK = '/GATIntegrationService/CancelReserve'

        def url(self):
            """
            Constructs end point url for WalletClient._wallet_url.
            :rtype: str
            :return: url of method
            """
            return '{}{}'.format(CKWalletClient._wallet_url, self.value)


    @classmethod
    def rollback_bet(cls, transaction):
        pass



    @classmethod
    def regulation(cls, casino_id, player_id, session_key, legislation):
        """Mock response"""
        return {
            "urls": {
                "mobile": "https://dev.kajotgames.cz",
                "desktop": "https://wegas.dev.kajotgames.cz",
                "default": "https://en.kajotgames.cz/",
            }
        }

    @classmethod
    def validate(cls, session_key, game_id, player_id=None):
        url = CKWalletClient.Methods.VALIDATE.url()
        payload = {
            'player_id':player_id,
            'session_id':session_key,
            'game_id': game_id
        }
        return cls.ask(url, data=payload)

    @classmethod
    def bet(cls, player_id, game_id, session_key, transaction_id, amount, round_id, as_bonus=False, device=0):
        url = cls.Methods.BET.url()
        payload = {
            "player_id": player_id,
            "session_id": session_key,
            "game_id": game_id,
            "transaction_id":transaction_id,
            "amount": amount,
            "round_id": round_id
        }
        json_response = cls.ask(url, data=payload)
        ret = web.Transaction.from_dict(json_response)
        return ret

    @classmethod
    def win(cls, game_id, player_id, session_key, round_id, transaction_id, amount, close_round=True, as_bonus=False,
            device=0):
        url = cls.Methods.WIN.url()
        payload = {
            'player_id':player_id,
            'session_id': session_key,
            'round_id': round_id,
            'transaction_id': transaction_id,
            'amount': amount
        }
        json_response = cls.ask(url, data=payload)
        ret = web.Transaction.from_dict(json_response)
        return ret

    @classmethod
    def endround(cls, game_id, player_id, session_key, round_id, transaction_id, as_bonus=False, device=0):
        url = cls.Methods.ENDROUND.url()
        payload = {
            'player_id':player_id,
            'session_id': session_key,
            'game_id': game_id,
            'round_id': round_id,
            'transaction_id': transaction_id
        }
        json_response = cls.ask(url, data=payload)
        ret = web.Wallet.from_dict(json_response)
        return ret

    @classmethod
    def endsession(cls, player_id, session_key):
        url = cls.Methods.ENDSESSION.url()
        payload = {
            'player_id': player_id,
            'session_id': session_key
        }
        return cls.ask(url, data=payload)

    @classmethod
    def balance(cls, player_id, session_key):
        url = cls.Methods.BALANCE.url()
        payload = {
            'player_id': player_id,
            'session_id': session_key
        }
        json_response = cls.ask(url, data=payload)
        ret = web.Balance.from_dict(json_response)
        return ret
