from flask_sqlalchemy import SQLAlchemy as Base


class SQLAlchemy(Base):
    def __init__(self, *args, **kwargs):
        super(SQLAlchemy, self).__init__(*args, **kwargs)

    def apply_driver_hacks(self, app, info, options):
        if "isolation_level" not in options:
            options["isolation_level"] = "READ COMMITTED"

        return super(SQLAlchemy, self).apply_driver_hacks(app, info, options)