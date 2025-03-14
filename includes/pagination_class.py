import requests

"""
Decorator for pagination
"""
class PaginationClass:
    def __init__(self):
        self.page = 1
        self.per_page = 10
        self.offset = 0

    def set_paging_params(self, request):
        self.page = int(request.view_args.get('page', self.page) or self.page)
        self.per_page = int(request.view_args.get('per_page', self.per_page) or self.per_page)

        if self.page < 1 or self.per_page < 1 or self.per_page > 100:
            return jsonify({"error": "Invalid pagination values. Page must be ≥ 1 and per_page between 1-100."}), 400

        self.offset = (self.page - 1) * self.per_page

        print(f"per_page: {self.per_page}")