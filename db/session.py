import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

import config

engine = create_engine(config.psql_url)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

