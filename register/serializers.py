from rest_framework import serializers
from .models import User
from .models import FriendRequest

class UserRegistrationSerializer(serializers.ModelSerializer):
    
    confirm_password = serializers.CharField(write_only= True)
    
    class Meta:
        model = User
        fields = ['first_name','last_name','email','password','confirm_password']
        extra_kwargs = {
            'password':{'write_only':True}
        }
    
        
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Passwords do not match')
        return data
    
    
    def create(self, validated_data):
        user = User.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['email'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only = True)


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name')
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        search_term = request.query_params.get('search', None) if request else None

        if search_term and User.objects.filter(email=search_term).exists():
            return {'id': representation['id'], 'email': representation['email']}
        else:
            return {'id': representation['id'], 'first_name': representation['first_name']}
        

#Main part of friend request

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at']

class CreateFriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['receiver']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['sender'] = request.user
        if FriendRequest.objects.filter(sender=request.user, receiver=validated_data['receiver'], status='pending').exists():
            raise serializers.ValidationError("Friend request already sent.")
        return super().create(validated_data)

class UpdateFriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['status']


class FriendsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']
