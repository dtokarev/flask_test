from project import ma, Search


class SearchSchema(ma.ModelSchema):
    class Meta:
        model = Search

search_schema = SearchSchema()
searches_schema = SearchSchema(many=True)
