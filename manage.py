from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from shop import app
from shop.database import Base


migrate = Migrate(app, Base)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
