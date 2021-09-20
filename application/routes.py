from flask import request
from flask_restx import Resource, Namespace, reqparse, marshal_with, abort, fields
from . import db
from .models import Transaction, Player, C_Transaction, Wallet, Game, Session, Round
from sqlalchemy.sql import func
import string
import random
from datetime import datetime


wallet_ns = Namespace('wallet', descripton='Wallet operations')


balance_post_args = reqparse.RequestParser()
balance_post_args.add_argument("real_amount", type=int, required=True)
balance_post_args.add_argument("bonus_amount", type=int, required=True)


balance_fields = wallet_ns.model('Balance', {
    'real_balance': fields.Integer,
    'bonus_balance': fields.Integer})


@wallet_ns.route('/balance')
class WalletOperations(Resource):
    @wallet_ns.marshal_with(balance_fields, code=200)
    @wallet_ns.doc('Get balance')
    def get(self):
        player_id = request.args.get('playerid')
        if player_id is None:
            abort(404, message='Player not found')
        return get_current_balance(player_id), 200


deposit_fields = wallet_ns.model('Deposit', {
    'initial_balance': fields.Nested(balance_fields),
    'added_balance': fields.Nested(balance_fields),
    'final_balance': fields.Nested(balance_fields)
})

deposit_post_args = reqparse.RequestParser()
deposit_post_args.add_argument('player_nickname', type=str, required=True)
deposit_post_args.add_argument('deposit_amount', type=int, required=True)




@wallet_ns.route('/deposit')
class WalletDeposit(Resource):
    @wallet_ns.marshal_with(deposit_fields, code=201)
    @wallet_ns.expect(deposit_post_args)
    @wallet_ns.doc('Deposit credit to your account')
    def post(self):
        args = deposit_post_args.parse_args()
        player = Player.query.filter(Player.nickname == args['player_nickname']).one_or_none()
        if not player:
            abort(404, message="Player with given nickname not found")
        if args['deposit_amount'] <= 0:
            abort(403, message="Deposit amount has to be greater than 0")
        added_balance = {'real_balance': args['deposit_amount'], 'bonus_balance': 0, 'total_balance': args['deposit_amount'] }
        initial_balance = get_current_balance(player.player_id)
        transaction_type = C_Transaction.query.filter(C_Transaction.transaction_type == 'deposit').one()
        wallet = Wallet.query.filter(Wallet.player_id == player.player_id).one_or_none()
        id = get_string_id()
        now = datetime.now()
        deposit = Transaction(transaction_id=id, transaction_type=transaction_type.c_transaction_id, wallet_id=wallet.wallet_id,
                              amount_real=args['deposit_amount'], amount_bonus=0, occured_at=now)
        db.session.add(deposit)
        db.session.commit()
        final_balance = get_current_balance(player.player_id)
        return {'initial_balance':initial_balance, 'added_balance':added_balance, 'final_balance':final_balance}

session_start_fields = wallet_ns.model('Session_Start', {
    'success': fields.Integer,
    'session_id': fields.String,
    'player_id': fields.Integer,
    'game_id': fields.String,
})

session_start_args = reqparse.RequestParser()
session_start_args.add_argument('player_id', type=int, required=True)
session_start_args.add_argument('game_id', type=str, required=True)

@wallet_ns.route('/start')
class StartSession(Resource):
    @wallet_ns.marshal_with(session_start_fields)
    @wallet_ns.expect(session_start_args)
    @wallet_ns.doc('Start session on the wallet/platform side. Necessary before session can start on Wegas side.')
    def post(self):
        args = session_start_args.parse_args()
        player = Player.query.get(args['player_id'])
        if not player:
            abort(404, message="Player not found")
        game = Game.query.get(args['game_id'])
        if not game:
            abort(404, message="Game not found")
        session_id = get_string_id()
        now = datetime.now()
        new_session = Session(session_id=session_id, player_id=player.player_id, game_id=game.game_id, is_active=True,
                              start_date=now, validated=False)
        db.session.add(new_session)
        db.session.commit()
        return {'success': 1, 'session_id': session_id, 'player_id': player.player_id, 'game_id': game.game_id}

validation_args = reqparse.RequestParser()
validation_args.add_argument('player_id', type=int, required=True)
validation_args.add_argument('session_id', type=str, required=True)
validation_args.add_argument('credentials', type=dict, required=False)
validation_args.add_argument('game_id', type=str, required=True)

balance_args = reqparse.RequestParser()
balance_args.add_argument('player_id', type=int, required=True)
balance_args.add_argument('session_id', type=str, required=True)
balance_args.add_argument('credentials', type=dict, required=False)

transaction_args = reqparse.RequestParser()
transaction_args.add_argument('player_id', type=int, required=True)
transaction_args.add_argument('session_id', type=str, required=True)
transaction_args.add_argument('credentials', type=dict, required=False)
transaction_args.add_argument('game_id', type=str, required=False)
transaction_args.add_argument('round_id', type=int, required=True)
transaction_args.add_argument('transaction_id', type=str, required=True)
transaction_args.add_argument('amount', type=int, required=True)

end_round_args = reqparse.RequestParser()
end_round_args.add_argument('player_id', type=int, required=True)
end_round_args.add_argument('session_id', type=str, required=True)
end_round_args.add_argument('credentials', type=dict, required=False)
end_round_args.add_argument('game_id', type=str, required=False)
end_round_args.add_argument('round_id', type=int, required=True)

end_session_args = reqparse.RequestParser()
end_session_args.add_argument('player_id', type=int, required=True)
end_session_args.add_argument('session_id', type=str, required=True)
end_session_args.add_argument('credentials', type=dict, required=False)

wegas_transaction_fields = wallet_ns.model('Wegas_transaction', {
    'real': fields.Integer(attribute='amount_real'),
    'bonus':fields.Integer(attribute='amount_bonus')
})


wegas_balance_fields = wallet_ns.model('Wegas_balance', {
    'real': fields.Integer(attribute='real_balance'),
    'bonus':fields.Integer(attribute='bonus_balance'),
    'bonus_round': fields.Integer})


wegas_response_fields = wallet_ns.model('Wegas_Response', {
    'success': fields.Integer,
    'player_id': fields.Integer,
    'transaction': fields.Nested(wegas_transaction_fields, skip_none=True),
    'balance': fields.Nested(wegas_balance_fields, skip_none=True),
    'currency':fields.String,
    'nickname': fields.String,
    'country': fields.String,
    'city': fields.String,
    'ext_transaction_id': fields.String,
    'message':fields.String

})

@wallet_ns.route('/validate')
class ValidateSession(Resource):
    @wallet_ns.marshal_with(wegas_response_fields, skip_none=True)
    @wallet_ns.expect(validation_args)
    @wallet_ns.doc('Endpoint for Wegas to validate session')
    def post(self):
        args = validation_args.parse_args()
        # Check whether session exists on our side and all relevant params match
        session = Session.query.filter(Session.session_id == args['session_id']).one_or_none()
        if session is None:
            abort(404, message='Session with this id not found')
        if args['player_id'] and args['player_id'] is not None:
            if args['player_id'] != session.player_id:
                abort(403, message="The player id provided does not match session's player_id")
        else:
            abort(404, message='player_id not provided')
        if args['game_id'] and args['game_id'] is not None:
            if args['game_id'] != session.game_id:
                abort(404, message="Provided game id does not match session's game id")
        if (session.end_date is not None) or not session.is_active:
            abort(404, message="This session is already closed")
        if session.game_id != args['game_id']:
            abort(404, message="Session conflict. This session was opened for a different game.")
        # session is okay, set as validated in db
        session.validated = True
        db.session.commit()
        # put together response
        balance = get_current_balance(args['player_id'])
        currency = balance.pop('currency')
        player = get_player(args['player_id'])
        return {
            'success': 1,
            'balance': balance,
            'currency': currency,
            'nickname': player.nickname,
            'country': player.country,
            'city': player.city,
            'player_id': player.player_id
        }


@wallet_ns.route('/balance')
class GetBalance(Resource):
    @wallet_ns.marshal_with(wegas_response_fields, skip_none=True)
    @wallet_ns.expect(balance_args)
    @wallet_ns.doc('Endpoint for Wegas to get player wallet balance')
    def post(self):
        args = balance_args.parse_args()
        session = check_session(args)
        balance = get_current_balance(args['player_id'])
        balance['bonus_round'] = 0
        currency = balance.pop('currency')
        return {
            'success': 1,
            'balance': balance,
            'player_id': session.player_id,
            'currency': currency
        }


@wallet_ns.route('/bet')
class MakeBet(Resource):
    @wallet_ns.marshal_with(wegas_response_fields, skip_none=True)
    @wallet_ns.expect(transaction_args)
    @wallet_ns.doc('Endpoint for Wegas to make player bet')
    def post(self):
        args = transaction_args.parse_args()
        session = check_session(args)
        balance = get_current_balance(args['player_id'])
        # check whether player has sufficient balance
        if args['amount'] > (balance['real_balance'] + balance['bonus_balance']):
            return {'success':0, 'message': 'Insufficient balance'}
        # check whether amount is positive
        if args['amount'] <= 0:
            return {'success':0, 'message': 'Bet amount must be positive'}
        # Create new round on our side
        now = datetime.now()
        new_round = Round(ext_round_id=args.get('round_id'), session_id=session.session_id, start_date=now, stake=args.get('amount'))
        db.session.add(new_round)
        db.session.commit()
        # prepare data to save new transaction
        tr_id = get_string_id()
        wallet = get_player_wallet(args['player_id'])
        transaction_type_id = get_transaction_type_id('bet')
        # apportioning bet between real and bonus balance. Balance is first subtracted from bonus, then from real.
        if balance['bonus_balance'] >= args['amount']:
            bet_transaction = Transaction(transaction_id=tr_id, transaction_type=transaction_type_id, wallet_id=wallet.wallet_id,
                                          amount_real=0, amount_bonus=-args['amount'], occured_at=now,
                                          ext_transaction_id=args.get('transaction_id'), round_id=new_round.round_id,
                                          session_id=session.session_id)
        else:
            bonus_amount = balance['bonus_balance']
            real_amount = args['amount'] - bonus_amount
            bet_transaction = Transaction(transaction_id=tr_id, transaction_type=transaction_type_id, wallet_id=wallet.wallet_id,
                                          amount_real=-real_amount, amount_bonus=-bonus_amount, occured_at=now,
                                          ext_transaction_id=args.get('transaction_id'), round_id=new_round.round_id,
                                          session_id=session.session_id)
        db.session.add(bet_transaction)
        db.session.commit()
        balance = get_current_balance(args['player_id'])
        return {
            'success': 1,
            'transaction': bet_transaction,
            'balance': balance,
            'ext_transaction_id': bet_transaction.ext_transaction_id,
        }


@wallet_ns.route('/win')
class Win(Resource):
    @wallet_ns.marshal_with(wegas_response_fields, skip_none=True)
    @wallet_ns.expect(transaction_args)
    @wallet_ns.doc('Endpoint for Wegas to inform us about player win')
    def post(self):
        args = transaction_args.parse_args()
        session = check_session(args)
        id = get_string_id()
        now = datetime.now()
        wallet = get_player_wallet(args['player_id'])
        transaction_type_id = get_transaction_type_id('win')
        our_round = get_internal_round(args.get('round_id'), session.session_id)
        # Assume win is all real balance
        win_transaction = Transaction(transaction_id=id, transaction_type=transaction_type_id, wallet_id=wallet.wallet_id,
                                      amount_real=args.get('amount'), amount_bonus=0, occured_at=now,
                                      ext_transaction_id=args.get('transaction_id'), round_id=our_round.round_id,
                                      session_id=session.session_id)
        db.session.add(win_transaction)
        db.session.commit()
        our_round.end_date = now
        our_round.win = args.get('amount')
        db.session.commit()
        balance = get_current_balance(args['player_id'])
        return {
            'success': 1,
            'player_id': session.player_id,
            'transaction': win_transaction,
            'balance': balance,
            'ext_transaction_id': win_transaction.ext_transaction_id
        }


@wallet_ns.route('/endround')
class EndRound(Resource):
    @wallet_ns.marshal_with(wegas_response_fields, skip_none=True)
    @wallet_ns.expect(end_round_args)
    @wallet_ns.doc('Endpoint for ending round (in which there was no win)')
    def post(self):
        args = end_round_args.parse_args()
        session = check_session(args)
        our_round = get_internal_round(args.get('round_id'), session.session_id)
        now = datetime.now()
        our_round.end_date = now
        db.session.commit()
        balance = get_current_balance(args['player_id'])
        return {
            'success': 1,
            'player_id': session.player_id,
            'balance': balance,
            'currency':balance['currency']
        }


@wallet_ns.route('/endsession')
class EndSession(Resource):
    @wallet_ns.marshal_with(wegas_response_fields, skip_none=True)
    @wallet_ns.expect(end_session_args)
    @wallet_ns.doc('Endpoint for Wegas to inform us about end of session (player navigating away)')
    def post(self):
        args = end_session_args.parse_args()
        ending_session = check_session(args)
        now = datetime.now()
        ending_session.end_date = now
        ending_session.is_active = False
        db.session.commit()
        return {
            'success': 1
        }


def check_session(args):
    """
Given an args dictionary, which contains the args sent in the payload of a Wegas request, perform basic checks
about the session- whether it exists, whether the player_id and game matches, and whether it's marked as validated
and not closed in the db.
    :param args: dict()
    :rtype: SQLAlchemy Query object representing a Session
    """
    session = Session.query.filter(Session.session_id == args['session_id']).one_or_none()
    if session is None:
        abort(404, message='Session with this id not found')
    if not session.validated:
        abort(404, message='Session not validated')
    if session.player_id != args['player_id']:
        abort(403, message="The player id provided does not match session's player_id")
    if (session.end_date is not None) or not session.is_active:
        abort(404, message="This session is already closed")
    if args.get('game_id') is not None:
        if args['game_id'] != session.game_id:
            abort(404, message="Provided game id does not match session's game id")
    return session


def get_current_balance(player_id) -> dict:
    """
Given the player's id, return their current balance, broken down into real and bonus
    :param player_id: integer, primary key of player in Player table
    :rtype: dict {'real_balance':, 'bonus_balance':, 'total_balance':}
    """

    player = Player.query.get(player_id)
    if not player:
        abort(404, message="Player not found")
    wallet = Wallet.query.filter(Wallet.player_id == player_id).one()
    q_real = db.session.query(func.sum(Transaction.amount_real)).filter(Transaction.wallet_id == wallet.wallet_id).group_by(Transaction.wallet_id).one_or_none()
    if q_real:
        q_real = q_real[0]
    else:
        q_real = 0
    q_bonus = db.session.query(func.sum(Transaction.amount_bonus)).filter(Transaction.wallet_id == wallet.wallet_id).group_by(Transaction.wallet_id).one_or_none()
    if q_bonus:
        q_bonus = q_bonus[0]
    else:
        q_bonus = 0
    return {"real_balance": q_real, "bonus_balance": q_bonus, "bonus_round": 0, "currency": wallet.currency}


def get_string_id(length: int = 30) -> string:
    """
Generate a random string with uppercase letters, lowercase letters and numbers. To be used for string PKs in database.
    :rtype: string
    """
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=length))


def get_player_wallet(player_id):
    """
Given a player's player_id, return their Wallet from the database. Returns None if no wallet found.
    :rtype: SQLAlchemy Query object representing a record in the Wallet table
    """
    return Wallet.query.filter(Wallet.player_id == player_id).one_or_none()


def get_player(player_id):
    """
Given a player's player id, return their nickname from the database. Will abort if player not found.
    :rtype: SQLAlchemy Query object representing a record in the Player table
    """
    player = Player.query.get(player_id)
    if player is None:
        abort(404, message="Player could not be found")
    return player

def get_transaction_type_id(transaction_type):
    """
Given a string denoting a transaction type, such as 'deposit' or 'bet', return the corresponding c_transaction_id
of that tupe in the DB.
    :param transaction_type: string
    :rtype: int
    """
    transaction_type_record = C_Transaction.query.filter(C_Transaction.transaction_type == transaction_type).one()
    return transaction_type_record.c_transaction_id

def get_internal_round(ext_round_id, session_id):
    """
Given an external round id (round_id from Wegas) and a session id, return the corresponding Round from our table.
    :param ext_round_id: int
    :param: session_id: string
    :rtype SQLAlchemy Query object representing a record in the Round table
    """
    return Round.query.filter(Round.ext_round_id == ext_round_id, Round.session_id == session_id).one_or_none()
