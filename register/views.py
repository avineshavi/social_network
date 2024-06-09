from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response 
from rest_framework.views import APIView 
from rest_framework.permissions import IsAuthenticated 
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from .models import FriendRequest
from rest_framework import(
    generics, permissions, status
)
from .serializers import(
    UserRegistrationSerializer, UserLoginSerializer, UserListSerializer, UserSearchSerializer,
    FriendRequestSerializer, CreateFriendRequestSerializer, UpdateFriendRequestSerializer, FriendsListSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    

class UserLoginView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception = True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, username=email, password=password)
        
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token':token.key},status=status.HTTP_200_OK)
        
        else:
            return Response({'details':'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
 


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        request.auth.delete()
        return Response({"detail":"Logout successful"},status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class UserSearchPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'total_count': self.page.paginator.count,
            'records_count_per_page': len(data),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class UserSearchView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSearchSerializer
    pagination_class = UserSearchPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search', None)

        if search_term:
            if User.objects.filter(email=search_term).exists():
                return queryset.filter(email=search_term)
            return queryset.filter(first_name__icontains=search_term)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(self.customize_response(serializer.data))
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(self.customize_response(serializer.data))

    def customize_response(self, data):
        search_term = self.request.query_params.get('search', None)
        if search_term and User.objects.filter(email=search_term).exists():
            for item in data:
                item.pop('first_name', None)
        else:
            for item in data:
                item.pop('email', None)
        return data


class SendFriendRequestView(generics.CreateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = CreateFriendRequestSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, receiver_id, *args, **kwargs):
        receiver_id = receiver_id
        if not receiver_id:
            return Response({"detail": "Receiver ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        one_minute_ago = timezone.now() - timezone.timedelta(minutes=1)
        recent_requests_count = FriendRequest.objects.filter(
            sender=request.user,
            created_at__gte=one_minute_ago
        ).count()
        
        if recent_requests_count >= 3:
            return Response({"detail": "You can only send 3 friend requests per minute."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        friend_request_exist = FriendRequest.objects.filter(
            Q(sender=request.user, receiver_id=receiver_id, status='pending') |
            Q(sender=receiver_id, receiver=request.user, status='pending')
        ).exists()
        if friend_request_exist:
            return Response({"detail": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {'receiver': receiver_id}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=request.user)
        receiver = User.objects.get(id=receiver_id)
        response_data = {
            'message': f"Friend request has been sent to {receiver.first_name}.",
            'receiver_name': receiver.first_name,
            'receiver_id': receiver.id
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class AcceptFriendRequestView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = UpdateFriendRequestSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.receiver != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        instance.status = FriendRequest.ACCEPTED
        instance.save()
        sender = instance.sender
        response_data = {
            'message': f"Friend request accepted from {sender.first_name}.",
            'sender_name': sender.first_name
        }
        return Response(response_data, status=status.HTTP_200_OK)


class RejectFriendRequestView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = UpdateFriendRequestSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.receiver != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        instance.status = FriendRequest.REJECTED
        instance.save()
        sender = instance.sender
        response_data = {
            'message': f"Friend request rejected from {sender.first_name}.",
            'sender_name': sender.first_name
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ListFriendRequestsPendingView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    authentication_classes = [TokenAuthentication]
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(receiver=self.request.user, status='pending')


class ListOfFriendView(generics.ListAPIView):
    serializer_class = FriendsListSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        friends = FriendRequest.objects.filter(
            Q(sender=user, status='accepted') | Q(receiver=user, status='accepted')
        )
        friend_ids = friends.values_list('sender', 'receiver')
        user_ids = {user_id for pair in friend_ids for user_id in pair if user_id != user.id}
        return User.objects.filter(id__in=user_ids)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)