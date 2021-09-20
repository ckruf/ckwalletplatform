from application import db


class Session(db.Model):
    __tablename__ = 'Session'

    session_id = db.Column(db.String(50), primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('Player.player_id'), nullable=False)
    game_id = db.Column(db.String(50), db.ForeignKey('Game.game_id'), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    validated = db.Column(db.Boolean, nullable=False)

    transaction = db.relationship('Transaction', backref='session', lazy=True)
    round = db.relationship('Round', backref='session', lazy=True)


class Transaction(db.Model):
    __tablename__ = 'Transaction'

    transaction_id = db.Column(db.String(50), primary_key=True)
    transaction_type = db.Column(db.Integer, db.ForeignKey('C_Transaction.c_transaction_id'), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('Wallet.wallet_id'), nullable=False)
    amount_real = db.Column(db.Integer, index=False, unique=False, nullable=False)
    amount_bonus = db.Column(db.Integer, index=False, unique=False, nullable=False)
    occured_at = db.Column(db.DateTime, nullable=False)
    ext_transaction_id = db.Column(db.String(50), nullable=True)
    round_id = db.Column(db.Integer, db.ForeignKey('Round.round_id', ondelete='SET NULL'), nullable=True)  # nullable true for deposits
    session_id = db.Column(db.String(50), db.ForeignKey('Session.session_id'), nullable=True)  # nullable true: deposits


class C_Transaction(db.Model):
    __tablename__ = 'C_Transaction'

    c_transaction_id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(10), nullable=False, unique=True)

    transaction = db.relationship('Transaction', backref='type', lazy=True)


class Player(db.Model):
    __tablename__ = 'Player'

    player_id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(50), nullable=True)

    session = db.relationship('Session', backref='session', lazy=True)
    wallet = db.relationship('Wallet', backref='player', lazy=True, uselist=False)


class Game(db.Model):
    __tablename__ = 'Game'

    game_id = db.Column(db.String(50), primary_key=True)

    session = db.relationship('Session', backref='game', lazy=True)


class Wallet(db.Model):
    __tablename__ = 'Wallet'

    wallet_id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(3), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('Player.player_id'), nullable=False)

    transaction = db.relationship('Transaction', backref='wallet', lazy=True)


class Round(db.Model):
    __tablename__ = 'Round'

    round_id = db.Column(db.Integer, primary_key=True)
    ext_round_id = db.Column(db.Integer, nullable=False)
    session_id = db.Column(db.String(50), db.ForeignKey('Session.session_id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    stake = db.Column(db.Integer, nullable=False)
    win = db.Column(db.Integer, nullable=True)

    transaction = db.relationship('Transaction', backref='round', lazy=True)