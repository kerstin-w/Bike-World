class AddItemAddedToRequestMiddleware:
    """
    Middleware to add item_added to request object for every incoming request
    """

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        """
        Add item_added to request object based on session data
        """
        item_added = request.session.pop("item_added", False)
        request.item_added = item_added

        response = self.get_response(request)

        return response
