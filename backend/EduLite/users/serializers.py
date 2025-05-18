from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


## -- User/Group Hyperlinked Serializers -- ##


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Group model.
    Exposes the 'url' (hyperlink to the group detail) and 'name' of the group.
    """
    class Meta:
        model = Group
        fields = ['url', 'name']
        # 'url' is automatically configured by HyperlinkedModelSerializer


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the User model.
    Exposes 'url', 'username', 'email', and the 'groups' the user belongs to.
    Relationships to groups are represented by hyperlinks.
    """
    # If you wanted to customize how 'groups' are represented, you could explicitly define it:
    # groups = GroupSerializer(many=True, read_only=True) # For full nested representation
    # groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name') # For list of group names

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']
        # 'url' here links to the detail view for a specific user.
        # 'groups' will be a list of hyperlinks to the groups the user is part of.


## -- Secure Password Hashing Serializers -- ##


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles username, email, password input, password confirmation, and secure password hashing.
    """
    email = serializers.EmailField(required=True)
    
    password = serializers.CharField(
        write_only=True, # ensures the password is never returned in the response
        required=True, 
        validators=[validate_password] # validates that the password is strong enough
        )
    password2 = serializers.CharField(
        write_only=True, 
        required=True, 
        label="Confirm password"
        )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            # If we want users to optionally enter their names on registration:
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate_email(self, value: str) -> str:
        """
        Perform custom email validations:
        1. Check for blocked domains.
        2. Check for email uniqueness.
        """
        if '@' not in value:
            # This is an extra safeguard. EmailField should catch most format issues.
            raise serializers.ValidationError("Invalid email format: '@' symbol missing.")
        email_name, domain_part = value.split('@', 1)
        # We can move this to settings.py if we need to
        blocked_domains = ['example.com', 'test.com'] 
        
        if domain_part.lower() in [d.lower() for d in blocked_domains]:
            raise serializers.ValidationError(
                "Registration from this email domain is not allowed."
            )

        # Uniqueness Check
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email address already exists."
            )
        
        return value # If all checks pass, return the validated email value

    def validate_username(self, value):
        """
        Check that the username is unique.
        """
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate(self, attrs):
        """
        Check that the two password entries match.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Password fields didn't match."})
        # You can add more custom validation here if needed
        return attrs

    def create(self, validated_data):
        """
        Create and return a new user instance, given the validated data.
        Handles password hashing.
        """
        # Remove password2 from validated_data as it's not part of the User model
        validated_data.pop('password2')
        
        # Extract password to use with create_user
        password = validated_data.pop('password')
        
        # create_user handles normalization of username/email and password hashing
        user = User.objects.create_user(
            **validated_data, # username, email, first_name, last_name
            password=password,
            is_active=True, # TODO: Setup email verification, or other means of account activation
        )
        return user