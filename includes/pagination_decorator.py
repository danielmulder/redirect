
class PaginationDecorator:
    def __init__(self):
        self.page = 1       # Default page or is replaced with requested page by client
        self.per_page = 10  # Default number of pages per tab or is replaced with requested page by client
        self.offset = 1

    def set_paging_params(self):
        # Get param for current page for pagination start
        self.page = request.args.get('page', default=self.page, type=int)
        # Get param for number of pages per page
        self.per_page = request.args.get('per_page', default=10, type=int)

        # Page validation (most be positive)
        if self.page < 1 or self.per_page < 1 or self.per_page > 100:
            return jsonify({"error": "Invalid pagination values. Page must be ≥ 1 and per_page between 1-100."}), 400
        else:
            self.offset = (self.page - 1) * self.per_page

    def pagination_total(self):
        # Get total records for pagination
        #total_count = Session.execute(
        #    select(func.count()).where(? == ?)
        #).scalar()
        pass
