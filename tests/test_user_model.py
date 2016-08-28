import time
import unittest

from app import create_app, db
from app.models import AnonymousUser, Permission, Role, User


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='password')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='password')
        with self.assertRaises(AttributeError):
            u.password()

    def test_password_verification(self):
        u = User(password='password')
        self.assertTrue(u.verify_password('password'))
        self.assertFalse(u.verify_password('notpassword'))

    def test_password_salts_are_random(self):
        u = User(password='password')
        u2 = User(password='password')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(password='password')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm_account(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password='password')
        u2 = User(password='notpassword')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm_account(token))

    def test_expired_confirmation_token(self):
        u = User(password='password')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm_account(token))

    def test_valid_reset_token(self):
        u = User(password='password')
        db.session.add(u)
        db.session.commit()
        token = u.generate_password_reset_token()
        self.assertTrue(u.reset_password(token, 'notpassword'))
        self.assertTrue(u.verify_password('notpassword'))

    def test_invalid_reset_token(self):
        u1 = User(password='password')
        u2 = User(password='notpassword')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_password_reset_token()
        self.assertFalse(u2.reset_password(token, 'notnotpassword'))
        self.assertTrue(u2.verify_password('notpassword'))

    def test_valid_email_change_token(self):
        u = User(email='user@example.com', password='password')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('otheruser@example.org')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'otheruser@example.org')

    def test_invalid_email_change_token(self):
        u1 = User(email='user@example.com', password='password')
        u2 = User(email='otheruser@example.org', password='notpassword')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token('otherotheruser@example.net')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'otheruser@example.org')

    def test_duplicate_email_change_token(self):
        u1 = User(email='user@example.com', password='password')
        u2 = User(email='otheruser@example.org', password='notpassword')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('user@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'otheruser@example.org')

    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email='user@example.com', password='password')
        self.assertTrue(u.can(Permission.GENERAL))
        self.assertFalse(u.can(Permission.ADMINISTER))

    def test_make_administrator(self):
        Role.insert_roles()
        u = User(email='user@example.com', password='password')
        self.assertFalse(u.can(Permission.ADMINISTER))
        u.role = Role.query.filter_by(
            permissions=Permission.ADMINISTER).first()
        self.assertTrue(u.can(Permission.ADMINISTER))

    def test_administrator(self):
        Role.insert_roles()
        r = Role.query.filter_by(permissions=Permission.ADMINISTER).first()
        u = User(email='user@example.com', password='password', role=r)
        self.assertTrue(u.can(Permission.ADMINISTER))
        self.assertTrue(u.can(Permission.GENERAL))
        self.assertTrue(u.is_admin())

    def test_anonymous(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.GENERAL))
