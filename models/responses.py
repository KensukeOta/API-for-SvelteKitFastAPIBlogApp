from .post_model import PostPublic
from .user_model import UserPublic


class UserPublicWithPosts(UserPublic):
    posts: list[PostPublic]


class PostPublicWithUser(PostPublic):
    user: UserPublic | None = None