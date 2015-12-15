from rest_framework.views import APIView
from rest_framework.response import Response
from booking.models import TableAllocation

class Occupancy(APIView):
    
    def get(self, request):
        result = TableAllocation.objects.all().values()
        return Response(result)
