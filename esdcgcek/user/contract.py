from dataclasses import asdict, dataclass
import json

@dataclass
class User:
    id: str
    first_name: str
    last_name: str
    email: str
    role: str
    type: str
    password: str
    def to_dict(self):
        return asdict(self)
    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)

@dataclass
class UserResponse:
    user: list[User]
    total_user: int

if __name__ == "__main__":
    user = User(
        id="123",
        first_name="Ganga",
        last_name="V",
        email="ganga@gmail.com",
        role="admin",
        type="user",
        password="gangav"
    )
    print(user)
