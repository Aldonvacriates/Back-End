from marshmallow import fields

from app.extensions import ma
from app.models import Loan


class LoanSchema(ma.SQLAlchemyAutoSchema):
    book_ids = fields.Method(
        serialize="dump_book_ids",
        deserialize="load_book_ids",
        required=False,
    )

    class Meta:
        model = Loan
        include_fk = True

    def dump_book_ids(self, obj):
        return [book.id for book in obj.books]

    def load_book_ids(self, value):
        return value


loan_schema = LoanSchema()
loans_schema = LoanSchema(many=True)
