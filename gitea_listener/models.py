import typing
from datetime import datetime

from pydantic import BaseModel


__all__ = ['ShortUser', 'User', 'Repository', 'Commit', 'PushEvent',
           'Response']


class ShortUser(BaseModel):
    name: str
    email: str
    username: str


class User(BaseModel):
    id: int
    login: str
    full_name: str
    email: str
    avatar_url: str
    username: str


class Repository(BaseModel):
    id: int
    owner: User
    name: str
    full_name: str
    description: typing.Optional[str]
    private: bool
    fork: bool
    html_url: str
    ssh_url: str
    clone_url: str
    website: typing.Optional[str]
    stars_count: int
    forks_count: int
    watchers_count: int
    open_issues_count: int
    default_branch: str
    created_at: datetime
    updated_at: datetime


class Commit(BaseModel):
    id: str
    message: str
    url: str
    author: ShortUser
    committer: ShortUser
    timestamp: datetime


class PushEvent(BaseModel):
    secret: typing.Optional[str]
    ref: str = ''
    before: str = ''
    after: str = ''
    compare_url: str = ''
    commits: typing.List[Commit]
    repository: Repository
    pusher: User
    sender: User


class Response(BaseModel):
    ok: bool
