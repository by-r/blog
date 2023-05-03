from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length = 8, write_only = True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

# subclass from SimpleJWT lib - used to serialize/deserialize the tokens that are used to auth API
# overrides get_token method from base of TokenObtainPairSerializer class :: get_token - generate JWT that is returned to client when auth req
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user) # invoke get_token method and return JWT that it generates :: JWT modified with username/email fields
        token['username'] = user.username
        token['email'] = user.email
        return token
