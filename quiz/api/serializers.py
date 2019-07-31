from rest_framework import serializers
from quiz.models import Question, Collection, MyCollections, MyQuestions


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = '__all__'


class MyQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyQuestions
        fields = '__all__'


class MyCollectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyCollections
        fields = '__all__'
