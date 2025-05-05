from rest_framework import serializers
from .models import ProjectUpload, ContactMessage, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class ProjectUploadSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False,
        help_text="List of tag names (existing or new)"
    )

    class Meta:
        model = ProjectUpload
        fields = [
            'id', 'author', 'author_username', 'title', 'slug', 'desc',
            'live_link', 'github_link', 'image', 'is_published', 'tags',
            'tag_names', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'slug', 'author')

    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        project = super().create(validated_data)
        self._handle_tags(project, tag_names)
        return project

    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tag_names', None)
        project = super().update(instance, validated_data)
        if tag_names is not None:
            project.tags.clear()
            self._handle_tags(project, tag_names)
        return project

    def _handle_tags(self, project, tag_names):
        for name in tag_names:
            cleaned_name = name.strip()
            if cleaned_name:  
                tag, _created = Tag.objects.get_or_create(name=cleaned_name)
                project.tags.add(tag)


    def _handle_tags(self, project, tag_names):
        for name in tag_names:
            cleaned_name = name.strip()
            if cleaned_name:
                tag, _ = Tag.objects.get_or_create(name=cleaned_name)
                project.tags.add(tag)

class ProjectUploadSerializer(serializers.ModelSerializer):
    tag_names = serializers.SerializerMethodField()
    src = serializers.SerializerMethodField()

    class Meta:
        model = ProjectUpload
        fields = ['title', 'desc', 'live_link', 'github_link', 'tag_names', 'src']

    def get_tag_names(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())

    def get_src(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return ""


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone_number',
            'role', 'message', 'is_read', 'status', 'submitted_at'
        ]
        read_only_fields = ('id', 'is_read', 'status', 'submitted_at')

    def validate_role(self, value):
        """Ensure the role is one of the predefined options"""
        valid_roles = ['As a Client', 'As a Frontend Developer', 'As a Backend Developer', 'As a Full Stack Developer']
        if value not in valid_roles:
            raise serializers.ValidationError("Invalid role. Please select a valid option.")
        return value

    def validate_status(self, value):
        """Ensure the status is one of the predefined options"""
        valid_statuses = ['new', 'in_progress', 'resolved']
        if value not in valid_statuses:
            raise serializers.ValidationError("Invalid status. Please select a valid option.")
        return value
