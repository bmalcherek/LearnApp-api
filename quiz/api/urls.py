from django.urls import path

from . import views


urlpatterns = [
    path('collections/', views.collectionListView),
    path('collections/<int:collection_id>/', views.collectionDetailView),
    path('collections/<int:collection_id>/rate/', views.putRatingToCollection),
    path('questions/<int:collection_id>/', views.questionListView),
    path('questions/<int:collection_id>/<int:question_id>', views.questionDetailView),
    path('user/', views.get_user),
    path('my-collections/', views.myCollectionsListView),
    path('my-collections/<int:collection_id>/', views.myCollectionsDetailView),
    path('my-questions/<int:my_collection_id>/', views.MyQuestionsView),
    path('my-questions/<int:my_collection_id>/get-questions-to-learn/', views.getQuestionsToLearn),
    path('my-questions/<int:my_collection_id>/<int:question_id>/', views.myQuestionsDetailedView),
]
