from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Visitor
from .serializers import VisitorSerializer

@api_view(['POST'])
def add_visitor(request):
    ip = request.data.get('ip')
    location = request.data.get('location')
    user_agent = request.data.get('userAgent')

    try:
        visitor, created = Visitor.objects.get_or_create(ip=ip)
        if not created:
            visitor.view_count += 1
            visitor.save()
        else:
            visitor.location = location
            visitor.user_agent = user_agent
            visitor.save()

        serializer = VisitorSerializer(visitor)
        return Response({'message': 'Visitor tracked successfully', 'visitor': serializer.data}, status=200)

    except Exception as e:
        print("Error in adding visitor:", e)
        return Response({'message': 'Internal Server Error'}, status=500)


@api_view(['GET'])
def get_visitor_stats(request):
    try:
        visitors = Visitor.objects.all()
        total_visitors = visitors.count()
        total_visits = sum([v.view_count for v in visitors])
        top_visitor = visitors.order_by('-view_count').first()

        serializer = VisitorSerializer(visitors, many=True)
        top_serializer = VisitorSerializer(top_visitor)

        return Response({
            'visitors': serializer.data,
            'totalVisitors': total_visitors,
            'totalVisits': total_visits,
            'topVisitor': top_serializer.data
        }, status=200)

    except Exception as e:
        print("Error in fetching visitor stats:", e)
        return Response({'message': 'Internal Server Error'}, status=500)
