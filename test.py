import pytest

import db


def test_check_user_exists():
   assert db.check_user_exists(1041994617) == False
   assert db.check_user_exists(1041994618) == True

