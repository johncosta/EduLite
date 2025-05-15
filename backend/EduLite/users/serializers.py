from django.contrib.auth.models import User, Group
from rest_framework import serializers

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Group model.
    Exposes the 'url' (hyperlink to the group detail) and 'name' of the group.
    """
    class Meta:
        model = Group
        fields = ['url', 'name']
        # 'url' is automatically configured by HyperlinkedModelSerializer
        # It requires the view to be registered with a router and to have a 'view_name'
        # or for the request to be available in the serializer context.
        # For example, if your viewset for Group is registered as 'group-detail',
        # DRF can automatically generate this link.

class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the User model.
    Exposes 'url', 'username', 'email', and the 'groups' the user belongs to.
    Relationships to groups are represented by hyperlinks.
    """
    # By default, HyperlinkedModelSerializer represents ManyToMany relationships
    # (like 'groups' on User) using HyperlinkedRelatedField.
    # This means 'groups' will be a list of URLs pointing to the respective group resources.
    # If you wanted to customize how 'groups' are represented, you could explicitly define it:
    # groups = GroupSerializer(many=True, read_only=True) # For full nested representation
    # groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name') # For list of group names

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']
        # 'url' here links to the detail view for a specific user.
        # 'groups' will be a list of hyperlinks to the groups the user is part of.