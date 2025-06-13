from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response


class ChatRoomPagination(PageNumberPagination):
    """
    Standard pagination for chat room listings.
    Used for browsing chat rooms with page numbers.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "results": data,
                "page_size": self.page_size,
            }
        )


class MessageCursorPagination(CursorPagination):
    """
    Cursor-based pagination for chat messages.
    Better for real-time chat as it handles new messages better
    and is more efficient with large datasets.
    """

    page_size = 50
    ordering = "-created_at"  # Newest messages first
    cursor_query_param = "cursor"

    def get_paginated_response(self, data):
        # Convert the reversed iterator to a list to make it serializable
        reversed_data = list(reversed(data))
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": reversed_data,  # Now it's a list, not an iterator
            }
        )
