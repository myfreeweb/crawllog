import os
from sqlalchemy import Column, ForeignKey, Integer, Text, Boolean, create_engine
from sqlalchemy.orm import sessionmaker, backref, relationship
from sqlalchemy.ext.declarative import declarative_base

def my_sessionmaker():
    engine = create_engine(os.environ.get('CRAWLLOG_DATABASE_URI', 'sqlite:////tmp/test.db'))
    Session = sessionmaker(bind=engine)
    return Session

Model = declarative_base()
Session = my_sessionmaker()

class Server(Model):
    __tablename__ = 'server'
    id = Column(Integer, primary_key=True)
    name = Column(Text)


class ServerLog(Model):
    __tablename__ = 'server_log'
    id = Column(Integer, primary_key=True)
    uri = Column(Text)
    uri_template = Column(Text)
    crawl_month_fix = Column(Boolean)
    position = Column(Integer)
    server_id = Column(Integer, ForeignKey('server.id'))
    server = relationship('Server', backref=backref('logs', lazy='dynamic'))


class User(Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    uri = Column(Text)
    micropub_uri = Column(Text)
    access_token = Column(Text)


class UserOnServer(Model):
    __tablename__ = 'user_on_server'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    auto_pub_threshold = Column(Integer)
    server_id = Column(Integer, ForeignKey('server.id'))
    server = relationship('Server', backref=backref('server_users', lazy='dynamic'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', backref=backref('user_servers', lazy='dynamic'))


def upsert_preserving_position(s, log):
    (id, server, uri, uri_template, crawl_month_fix, position) = log
    if s.query(ServerLog).get(id):
        s.merge(ServerLog(id=id, server=server, uri=uri, uri_template=uri_template, crawl_month_fix=crawl_month_fix))
    else:
        s.merge(ServerLog(id=id, server=server, uri=uri, uri_template=uri_template, crawl_month_fix=crawl_month_fix, position=position))


# check new data at: https://github.com/crawl/scoring/blob/master/sources.yml
def setup_db():
    s = Session()
    cao    = Server(id=0, name='crawl.akrasiac.org')
    # cszo   = Server(id=1, name='crawl.s-z.org') # RIP
    # cdo    = Server(id=2, name='crawl.develz.org') # Doesn't even return Content-Length
    clan   = Server(id=3, name='underhound.eu')
    cbro   = Server(id=4, name='crawl.berotato.org')
    cwz    = Server(id=5, name='webzook.net/soup')
    # lld    = Server(id=6, name='lazy-life.ddo.jp') # Doesn't support HEAD
    cxc    = Server(id=7, name='crawl.xtahua.com')
    # cpo    = Server(id=8, name='crawl.project357.org') # Content-Length
    # cjr    = Server(id=9, name='crawl.jorgrun.rocks') # RIP
    [s.merge(server) for server in [cao]]
    [upsert_preserving_position(s, data) for data in [
         # DO NOT CHANGE ID!
        (0,       cao,     'http://crawl.akrasiac.org/logfile-git',               'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  360910030),
        (1,       cao,     'http://crawl.akrasiac.org/logfile10',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  28041164),
        (2,       cao,     'http://crawl.akrasiac.org/logfile11',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  13081547),
        (3,       cao,     'http://crawl.akrasiac.org/logfile12',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  24040176),
        (4,       cao,     'http://crawl.akrasiac.org/logfile13',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  26115012),
        (5,       cao,     'http://crawl.akrasiac.org/logfile14',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  30000618),
        (6,       cao,     'http://crawl.akrasiac.org/logfile15',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  62805919),
        (7,       cao,     'http://crawl.akrasiac.org/logfile16',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  66794598),
        (8,       cao,     'http://crawl.akrasiac.org/logfile17',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  62839820),
        (9,       cao,     'http://crawl.akrasiac.org/logfile18',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  61363158),
        (10,      cao,     'http://crawl.akrasiac.org/logfile19',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  0),
        (11,      cao,     'http://crawl.akrasiac.org/logfile20',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  0),
        (12,      cao,     'http://crawl.akrasiac.org/logfile21',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  0),
        (13,      cao,     'http://crawl.akrasiac.org/logfile22',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  0),
        (3000,    clan,    'https://underhound.eu/crawl/meta/git/logfile',        'https://underhound.eu/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  112265829),
        (3001,    clan,    'https://underhound.eu/crawl/meta/0.10/logfile',       'https://underhound.eu/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  106071),
        (3002,    clan,    'https://underhound.eu/crawl/meta/0.11/logfile',       'https://underhound.eu/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  79132),
        (3003,    clan,    'https://underhound.eu/crawl/meta/0.12/logfile',       'https://underhound.eu/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  1632644),
        (3004,    clan,    'https://underhound.eu/crawl/meta/0.13/logfile',       'https://underhound.eu/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  8708102),
        (3005,    clan,    'https://underhound.eu/crawl/meta/0.14/logfile',       'https://underhound.eu/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  7359165),
        (3006,    clan,    'https://underhound.eu/crawl/meta/0.15/logfile',       'https://underhound.eu/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  7427725),
        (3007,    clan,    'https://underhound.eu/crawl/meta/0.16/logfile',       'https://underhound.eu/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  6529896),
        (3008,    clan,    'https://underhound.eu/crawl/meta/0.17/logfile',       'https://underhound.eu/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  23536470),
        (3009,    clan,    'https://underhound.eu/crawl/meta/0.18/logfile',       'https://underhound.eu/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  24030317),
        (3010,    clan,    'https://underhound.eu/crawl/meta/0.19/logfile',       'https://underhound.eu/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  0),
        (3011,    clan,    'https://underhound.eu/crawl/meta/0.20/logfile',       'https://underhound.eu/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  0),
        (3012,    clan,    'https://underhound.eu/crawl/meta/0.21/logfile',       'https://underhound.eu/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  0),
        (3013,    clan,    'https://underhound.eu/crawl/meta/0.22/logfile',       'https://underhound.eu/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  0),
        (4000,    cbro,    'http://crawl.berotato.org/crawl/meta/git/logfile',    'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  144691367),
        (4001,    cbro,    'http://crawl.berotato.org/crawl/meta/0.13/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  424187),
        (4002,    cbro,    'http://crawl.berotato.org/crawl/meta/0.14/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  3267516),
        (4003,    cbro,    'http://crawl.berotato.org/crawl/meta/0.15/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  4974258),
        (4004,    cbro,    'http://crawl.berotato.org/crawl/meta/0.16/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  17165648),
        (4005,    cbro,    'http://crawl.berotato.org/crawl/meta/0.17/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  20152628),
        (4006,    cbro,    'http://crawl.berotato.org/crawl/meta/0.18/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  44107731),
        (4006,    cbro,    'http://crawl.berotato.org/crawl/meta/0.19/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  0),
        (4007,    cbro,    'http://crawl.berotato.org/crawl/meta/0.20/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  0),
        (4008,    cbro,    'http://crawl.berotato.org/crawl/meta/0.21/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  0),
        (4009,    cbro,    'http://crawl.berotato.org/crawl/meta/0.22/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  0),
        (5000,    cwz,     'http://webzook.net/soup/trunk/logfile',               'http://webzook.net/soup/morgue/trunk/{name}/morgue-{name}-{end}.txt',             True,  288275423),
       #(5001,    cwz,     'http://webzook.net/soup/0.13/logfile',                'http://webzook.net/soup/morgue/0.13/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(5002,    cwz,     'http://webzook.net/soup/0.14/logfile',                'http://webzook.net/soup/morgue/0.14/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(5003,    cwz,     'http://webzook.net/soup/0.15/logfile',                'http://webzook.net/soup/morgue/0.15/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(5004,    cwz,     'http://webzook.net/soup/0.16/logfile',                'http://webzook.net/soup/morgue/0.16/{name}/morgue-{name}-{end}.txt',              True,  0),
        (5005,    cwz,     'http://webzook.net/soup/0.17/logfile',                'http://webzook.net/soup/morgue/0.17/{name}/morgue-{name}-{end}.txt',              True,  5613183),
        (5006,    cwz,     'http://webzook.net/soup/0.18/logfile',                'http://webzook.net/soup/morgue/0.18/{name}/morgue-{name}-{end}.txt',              True,  0),
        (5007,    cwz,     'http://webzook.net/soup/0.19/logfile',                'http://webzook.net/soup/morgue/0.19/{name}/morgue-{name}-{end}.txt',              True,  0),
        (5008,    cwz,     'http://webzook.net/soup/0.20/logfile',                'http://webzook.net/soup/morgue/0.20/{name}/morgue-{name}-{end}.txt',              True,  0),
        (5009,    cwz,     'http://webzook.net/soup/0.21/logfile',                'http://webzook.net/soup/morgue/0.21/{name}/morgue-{name}-{end}.txt',              True,  0),
        (5010,    cwz,     'http://webzook.net/soup/0.22/logfile',                'http://webzook.net/soup/morgue/0.22/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(6000,    lld,     'http://lazy-life.ddo.jp:8080/meta/trunk/logfile',     'http://lazy-life.ddo.jp:8080/morgue/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(6001,    lld,     'http://lazy-life.ddo.jp:8080/meta/0.14/logfile',      'http://lazy-life.ddo.jp:8080/morgue/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(6002,    lld,     'http://lazy-life.ddo.jp:8080/meta/0.15/logfile',      'http://lazy-life.ddo.jp:8080/morgue/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(6003,    lld,     'http://lazy-life.ddo.jp:8080/meta/0.16/logfile',      'http://lazy-life.ddo.jp:8080/morgue/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(6004,    lld,     'http://lazy-life.ddo.jp:8080/meta/0.17/logfile',      'http://lazy-life.ddo.jp:8080/morgue/{name}/morgue-{name}-{end}.txt',              True,  0),
        (7000,    cxc,     'http://crawl.xtahua.com/crawl/meta/git/logfile',      'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  81420955),
        (7001,    cxc,     'http://crawl.xtahua.com/crawl/meta/0.14/logfile',     'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  295987),
        (7002,    cxc,     'http://crawl.xtahua.com/crawl/meta/0.15/logfile',     'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  1346634),
        (7003,    cxc,     'http://crawl.xtahua.com/crawl/meta/0.16/logfile',     'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  9592324),
        (7004,    cxc,     'http://crawl.xtahua.com/crawl/meta/0.17/logfile',     'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  13313271),
        (7005,    cxc,     'http://crawl.xtahua.com/crawl/meta/0.18/logfile',     'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  0),
        (7006,    cxc,     'http://crawl.xtahua.com/crawl/meta/0.19/logfile',     'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  0),
        (7007,    cxc,     'http://crawl.xtahua.com/crawl/meta/0.20/logfile',     'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  0),
        (7008,    cxc,     'http://crawl.xtahua.com/crawl/meta/0.21/logfile',     'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  0),
        (7009,    cxc,     'http://crawl.xtahua.com/crawl/meta/0.22/logfile',     'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  0),
       #(8000,    cpo,     'https://crawl.project357.org/dcss-logfiles-trunk',    'http://crawl.project357.org/morgue/{name}/morgue-{name}-{end}.txt',               True,  0),
       #(8001,    cpo,     'https://crawl.project357.org/dcss-logfiles-0.15',     'http://crawl.project357.org/morgue/{name}/morgue-{name}-{end}.txt',               True,  0),
       #(8002,    cpo,     'https://crawl.project357.org/dcss-logfiles-0.16',     'http://crawl.project357.org/morgue/{name}/morgue-{name}-{end}.txt',               True,  0),
       #(8003,    cpo,     'https://crawl.project357.org/dcss-logfiles-0.17',     'http://crawl.project357.org/morgue/{name}/morgue-{name}-{end}.txt',               True,  0),
       #(10000, )
    ]]
    s.commit()
