from django.contrib.auth.models import User

from rest_framework import serializers

from profile_app.models import Profile

class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with profile type selection."""
    type = serializers.ChoiceField(choices=[('customer', 'customer'), ('business', 'business')], write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True}
        }

    def save(self, **kwargs):
        """Create a new user with associated profile.

        Validates password match and creates both User and Profile instances.
        """
        password = self.validated_data['password']
        repeated_password = self.validated_data['repeated_password']

        if password != repeated_password:
            raise serializers.ValidationError({"error": "Passwords do not match."})
        
        user = User(
            username=self.validated_data['username'],
            email=self.validated_data['email'])
        
        user.set_password(password)
        user.save()

        Profile.objects.create(
            user=user,
            type=self.validated_data['type']
        )

        return user
        
class LoginSerializer(serializers.Serializer):
    """Serializer for user login authentication."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate user credentials.

        Checks if username exists and password is correct.
        """
        username = data.get('username')
        password = data.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "Invalid username or password."})

        if not user.check_password(password):
            raise serializers.ValidationError({"error": "Invalid username or password."})

        data['user'] = user
        return data

    def get(self):
        """Return the authenticated user."""
        return self.validated_data['user']