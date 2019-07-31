from datetime import datetime, timedelta
from math import ceil

from rest_framework import status, permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse

from quiz.models import Question, Collection, MyCollections, MyQuestions
from .serializers import QuestionSerializer, CollectionSerializer, MyCollectionsSerializer, MyQuestionsSerializer


@api_view(['GET', 'POST'])
@permission_classes((permissions.IsAuthenticated, ))
def collectionListView(request):
    # permission_classes = [permissions.AllowAny]
    if request.method == 'GET':
        queryset = Collection.objects.all()
        serializer = CollectionSerializer(queryset, many=True)

        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        serializer = CollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((permissions.IsAuthenticated, ))
def collectionDetailView(request, collection_id):
    try:
        collection = Collection.objects.get(id=collection_id)
    except Collection.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 


@api_view(['PUT'])
@permission_classes((permissions.IsAuthenticated, ))
def putRatingToCollection(request, collection_id):
    try:
        collection = Collection.objects.get(id=collection_id)
    except Collection.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    collection_data = CollectionSerializer(collection).data
    data = {}
    data['ratings_count'] = collection_data['ratings_count'] + 1
    data['rating'] = (collection_data['rating'] * collection_data['ratings_count'] + request.data['rating']) / data['ratings_count']
    data['name'] = collection_data['name']

    serializer = CollectionSerializer(collection, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)

    else:
        print(serializer.errors)    
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes((permissions.IsAuthenticated, ))
def questionListView(request, collection_id):
    if request.method == 'GET':
        queryset = Question.objects.filter(collection=collection_id)
        serializer = QuestionSerializer(queryset, many=True)

        return JsonResponse(serializer.data, safe=False)

    if request.method == 'POST':
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((permissions.IsAuthenticated, ))
def questionDetailView(request, collection_id, question_id):
    try:
        question = Question.objects.get(collection=collection_id, id=question_id)
    except Question.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = QuestionSerializer(question)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = QuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)    


@api_view(['GET',])
@permission_classes((permissions.IsAuthenticated, ))
def get_user(request):
    # print(request.user)
    try:
        pass
        # print(request.META['HTTP_AUTHORIZATION'])
    except:
        return Response({'user': 'Logged Out'})
    return Response({
        'username': request.user.username,
        'email': request.user.email,
    })


@api_view(['GET', 'POST'])
@permission_classes((permissions.IsAuthenticated, ))
def myCollectionsListView(request):
    if request.method == 'GET':
        queryset = MyCollections.objects.filter(user=request.user)
        serializer = MyCollectionsSerializer(queryset, many=True)
        return_data = []
        for my_collection in serializer.data:
            data = my_collection
            collection = Collection.objects.get(id=my_collection['collection'])
            collection = CollectionSerializer(collection)
            data['name'] = collection.data['name']

            to_learn = 0
            questions = MyQuestions.objects.filter(my_collection=my_collection['id'])
            today = datetime.now()
            questions = MyQuestionsSerializer(questions, many=True).data
            for question in questions:
                rep_date = datetime.strptime(question['next_rep_date'], '%Y-%m-%d')
                if rep_date <= today:
                    to_learn += 1
            
            data['to_learn'] = to_learn
            return_data.append(data)

        return Response(return_data)

    elif request.method == 'POST':
        user = request.user
        collection = int(request.data['collection'])
        my_collection_data = {
            'collection': collection,
            'user': user.id
        }
        serializer = MyCollectionsSerializer(data=my_collection_data)
        if serializer.is_valid():                
            serializer.save()
            questions = Question.objects.filter(collection=int(request.data['collection']))
            question_serializer = QuestionSerializer(questions, many=True)
            questions = question_serializer.data
            today = datetime.now()
            for question in questions:
                my_question_data = {
                    'original_collection': collection,
                    'my_collection': serializer.data['id'],
                    'original_question': question['id'],
                    'rep_count': 0,
                    'next_rep_date': today.strftime('%Y-%m-%d')
                }
                my_question_serializer = MyQuestionsSerializer(data=my_question_data)
                if my_question_serializer.is_valid():
                    my_question_serializer.save()
                else:
                    print(my_question_serializer.errors)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
@permission_classes((permissions.IsAuthenticated, ))
def myCollectionsDetailView(request, collection_id):
    try:
        collection = MyCollections.objects.get(id=collection_id)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET':
        serializer = MyCollectionsSerializer(collection)
        data = serializer.data
        original_collection = Collection.objects.get(id=data['collection'])
        og_coll_serializer = CollectionSerializer(original_collection)
        data['name'] = og_coll_serializer.data['name']
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        collection.delete()        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def MyQuestionsView(request, my_collection_id):
    try:
        questions = MyQuestions.objects.filter(my_collection_id=my_collection_id)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    serializer = MyQuestionsSerializer(questions, many=True)
    if len(serializer.data) == 0:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    my_collection = MyCollections.objects.get(id=serializer.data[0]['my_collection'])
    my_collection_serializer = MyCollectionsSerializer(my_collection)
    owner_id = my_collection_serializer.data['user']

    if request.user.id != owner_id:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    return_data = list()
    for question in serializer.data:
        og_question = Question.objects.get(id=question['original_question'])
        og_question = QuestionSerializer(og_question).data
        og_question_values = { key: og_question[key] for key in ['question', 'is_image', 'image_url', 'answer'] }
        data = {**question, **og_question_values}
        return_data.append(data)

    return Response(return_data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@permission_classes((permissions.IsAuthenticated, ))
def myQuestionsDetailedView(request, my_collection_id, question_id):
    # print(my_collection_id, question_id)
    try:
        question = MyQuestions.objects.get(id=question_id)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
    
    elif request.method == 'PUT':
        old_question = MyQuestionsSerializer(question)
        # print(old_question.data)
        data = request.data
        new_e_factor = old_question.data['e_factor'] + (0.1 - (5 - data['q']) * (0.08 + (5 - data['q']) * 0.02))
        if new_e_factor < 1.3:
            new_e_factor = 1.3
        data['e_factor'] = new_e_factor
        data['rep_count'] = old_question.data['rep_count']

        if data['q'] >= 4:
            data['rep_count'] += 1
            today = datetime.now()
            data['last_rep_date'] = today.strftime('%Y-%m-%d')
            if data['rep_count'] == 1:
                data['next_rep_date'] = (today + timedelta(days=1)).strftime('%Y-%m-%d')
                data['last_interval'] = 1
            elif data['rep_count'] == 2:
                data['next_rep_date'] = (today + timedelta(days=6)).strftime('%Y-%m-%d')
                data['last_interval'] = 6
            else:
                new_interval = ceil(old_question.data['last_interval'] * new_e_factor)
                data['next_rep_date'] = (today + timedelta(days=new_interval)).strftime('%Y-%m-%d')
                data['last_interval'] = new_interval
        else:
            data['rep_count'] = 0
            data['last_interval'] = 0

        print(data)

        serializer = MyQuestionsSerializer(question, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def getQuestionsToLearn(request, my_collection_id):
    try:
        questions = MyQuestions.objects.filter(my_collection_id=my_collection_id)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    serializer = MyQuestionsSerializer(questions, many=True)
    data = serializer.data
    my_collection = MyCollections.objects.get(id=my_collection_id)
    my_collection = MyCollectionsSerializer(my_collection).data

    if request.user.id != my_collection['user']:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    today = datetime.now()
    response_data = list()
    for question in data:
        rep_date = datetime.strptime(question['next_rep_date'], '%Y-%m-%d')
        if rep_date <= today:
            og_question = Question.objects.get(id=question['original_question'])
            og_question = QuestionSerializer(og_question).data
            og_question_values = { key: og_question[key] for key in ['question', 'is_image', 'image_url', 'answer'] }
            question_data = {**question, **og_question_values}
            response_data.append(question_data)

    return Response(response_data, status=status.HTTP_200_OK)
