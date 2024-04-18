from sqlalchemy import *

Base = declarative_base()

class Users(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    username = Column(String)
    passsword = Column(String(256))
    name = Column(String)
    last_name = Column(String)
    user_type = Column(String)

    def __repr__(self):
        return "User ID: {self.id}, email: {self.email}, username: {self.username}, password: {self.passsword}, name: {self.name}, last name: {self.last_name}, user_type: {self.user_type}".format(self.user_type="Vendor" if self.user_type = 'V' else: "Buyer")

class Addresses(Base):
    __tablename__ = 'Addresses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    active = Column(Boolean)
    state = Column(String)
    province = Column(String)

    def __repr__(self):
        return "Address id: {self.id}, of the user: {self.user_id}, status: {self.active}, state: {self.state}, province: {self:province}".format(self.active="active" if self.active=True else: "Not active")

