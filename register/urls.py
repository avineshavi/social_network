from django.urls import path
from .views import UserRegistrationView
from .views import UserLoginView
from .views import UserLogoutView
from .views import UserListView
from .views import UserSearchView

from .views import SendFriendRequestView
from .views import ListFriendRequestsPendingView
from .views import AcceptFriendRequestView
from .views import RejectFriendRequestView
from .views import ListOfFriendView
urlpatterns = [
    path('api/signup/', UserRegistrationView.as_view(),name='api_user_register'),
    path('api/login/', UserLoginView.as_view(),name='user_login'),
    path('api/users-list/', UserListView.as_view(), name='user_list'),
    path('api/search/', UserSearchView.as_view(), name='user_search'),
    
    
    path('api/friend-requests/send/<int:receiver_id>/', SendFriendRequestView.as_view(), name='send_friend_request'),
    path('api/friend-requests/accept/<int:pk>/', AcceptFriendRequestView.as_view(), name='accept_friend_request'),
    path('api/friend-requests/reject/<int:pk>/', RejectFriendRequestView.as_view(), name='reject_friend_request'),
    path('api/friend-requests-pending/', ListFriendRequestsPendingView.as_view(), name='list_friend_request'),
    path('api/friend-list/', ListOfFriendView.as_view(), name='list_friends'),
    

    path('logout/', UserLogoutView.as_view(),name='user_logout'),
]
