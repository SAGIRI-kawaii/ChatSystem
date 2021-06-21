# import yaml
from os import environ
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, insert, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import Column, Integer, String, DateTime, Boolean, BLOB, BIGINT

# yaml.warnings({'YAMLLoadWarning': False})
environ['NLS_LANG'] = 'AMERICAN_AMERICA.AL32UTF8'


DB_LINK = "sqlite+aiosqlite:///data.db"


class AsyncEngine:
    def __init__(self, db_link):
        self.engine = create_async_engine(
            db_link,
            echo=False
        )

    async def execute(self, sql, **kwargs):
        async with AsyncSession(self.engine) as session:
            try:
                result = await session.execute(sql, **kwargs)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise e

    async def fetchall(self, sql):
        return (await self.execute(sql)).fetchall()

    async def fetchone(self, sql):
        # self.warning(sql)
        result = await self.execute(sql)
        one = result.fetchone()
        if one:
            return one
        else:
            return None

    async def fetchone_dt(self, sql, n=999999):
        # self.warning(sql)
        result = await self.execute(sql)
        columns = result.keys()
        length = len(columns)
        for _ in range(n):
            one = result.fetchone()
            if one:
                yield {columns[i]: one[i] for i in range(length)}

    @staticmethod
    def warning(x):
        print('\033[033m{}\033[0m'.format(x))

    @staticmethod
    def error(x):
        print('\033[031m{}\033[0m'.format(x))


class AsyncORM(AsyncEngine):
    """对象关系映射（Object Relational Mapping）"""

    def __init__(self, conn):
        super().__init__(conn)
        self.session = AsyncSession(bind=self.engine)
        self.Base = declarative_base(self.engine)
        self.async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
        # self.create_all()

    # def __del__(self):
    #     self.session.close()

    async def create_all(self):
        """创建所有表"""
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)

    async def drop_all(self):
        """创建所有表"""
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.drop_all)

    async def add(self, table, dt):
        """插入"""
        async with self.async_session() as session:
            async with session.begin():
                session.add(table(**dt), _warn=False)
            await session.commit()

    async def update(self, table, condition, dt):
        await self.execute(update(table).where(*condition).values(**dt))

    async def insert_or_update(self, table, condition, dt):
        if (await self.execute(select(table).where(*condition))).all():
            return await self.execute(update(table).where(*condition).values(**dt))
        else:
            return await self.execute(insert(table).values(**dt))

    async def insert_or_ignore(self, table, condition, dt):
        if not (await self.execute(select(table).where(*condition))).all():
            return await self.execute(insert(table).values(**dt))

    async def insert(self, table, dt):
        return await self.execute(insert(table).values(**dt))

    async def delete(self, table, condition):
        return await self.execute(delete(table).where(*condition))


orm = AsyncORM(DB_LINK)

Base = orm.Base


class GroupChatRecord(Base):
    """ 群聊天记录表 """
    __tablename__ = "group_chat_record"

    id = Column(Integer, primary_key=True)
    time = Column(DateTime, nullable=False)
    group_id = Column(BIGINT, nullable=False)
    sender = Column(BIGINT, nullable=False)
    message_chain = Column(String(length=4000), nullable=False)


class FriendChatRecord(Base):
    """ 好友聊天记录表 """
    __tablename__ = "friend_chat_record"

    id = Column(Integer, primary_key=True)
    time = Column(DateTime, nullable=False)
    sender = Column(BIGINT, nullable=False)
    receiver = Column(BIGINT, nullable=False)
    message_chain = Column(String(length=4000), nullable=False)


class Group(Base):
    """ 群组信息 """
    __tablename__ = "group"

    group_id = Column(Integer, primary_key=True)
    name = Column(String(length=50), nullable=True)
    description = Column(String(length=200), default="本群还没有描述呢～快来编辑吧～")
    avatar = Column(String(length=32), nullable=True)


class User(Base):
    """ 用户信息 """
    __tablename__ = "user"

    user_id = Column(BIGINT, primary_key=True)
    username = Column(String(length=50), nullable=False)
    nickname = Column(String(length=50), nullable=True)
    password = Column(String(length=32), nullable=False)
    sign = Column(String(length=200), default="这个人很懒，没有留下任何东西")
    avatar = Column(String(length=32), nullable=True)


class FriendRelationship(Base):
    """ 好友关系 """
    __tablename__ = "friend_relationship"

    account = Column(BIGINT, primary_key=True)
    friend = Column(BIGINT, primary_key=True)


class GroupRelationship(Base):
    """
    群组关系
    permission: 权限等级
        1: 普通成员
        2: 管理员
        3: 群主
    """
    __tablename__ = "group_relationship"

    group_id = Column(BIGINT, primary_key=True)
    member_id = Column(BIGINT, primary_key=True)
    permission = Column(Integer, default=1)


class Application(Base):
    """
    申请信息（好友/群）
    application_type: 申请类型
        1: 好友申请
        2: 加群申请
        3: 退群通知
    """
    __tablename__ = "application"

    time = Column(DateTime, nullable=False)
    applicant = Column(BIGINT, primary_key=True)
    receiver = Column(BIGINT, primary_key=True)
    message = Column(String(length=100), default="什么也没有说")
    application_type = Column(Integer, primary_key=True)
    passed = Column(Boolean, default=False)
