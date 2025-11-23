from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from .models import DailyCollection, Person
from .serializers import DailyCollectionSerializer
from accounts.models import Employee


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_collection_api(request):
    """API endpoint for adding collection (Admin only)"""
    if not request.user.is_admin:
        return Response(
            {'error': 'Access denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    employee_id = request.data.get('employee')
    date_str = request.data.get('date')
    amount = request.data.get('amount_collected')
    
    try:
        employee = Employee.objects.get(emp_id=employee_id)
        from datetime import datetime
        coll_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        from decimal import Decimal
        amount_decimal = Decimal(str(amount))
        
        if amount_decimal < 0:
            return Response(
                {'error': 'Amount cannot be negative'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        collection, created = DailyCollection.objects.get_or_create(
            employee=employee,
            date=coll_date,
            defaults={'amount_collected': amount_decimal}
        )
        
        if not created:
            collection.amount_collected = amount_decimal
            collection.save()
        
        serializer = DailyCollectionSerializer(collection)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def collection_list_api(request):
    """API endpoint for listing collections"""
    collections = DailyCollection.objects.all()
    
    # Filter by employee
    if not request.user.is_admin:
        collections = collections.filter(employee=request.user)
    else:
        employee_id = request.GET.get('employee')
        if employee_id:
            collections = collections.filter(employee__emp_id=employee_id)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        collections = collections.filter(date__gte=date_from)
    if date_to:
        collections = collections.filter(date__lte=date_to)
    
    serializer = DailyCollectionSerializer(collections.order_by('-date'), many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calculate_daily_incentive_api(request):
    """API endpoint for calculating daily incentive"""
    date_str = request.GET.get('date')
    employee_id = request.GET.get('employee')
    
    if not date_str:
        return Response(
            {'error': 'Date parameter required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    from datetime import datetime
    coll_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    collections = DailyCollection.objects.filter(date=coll_date)
    
    if employee_id:
        collections = collections.filter(employee__emp_id=employee_id)
    
    total_incentive = collections.aggregate(Sum('incentive_earned'))['incentive_earned__sum'] or 0
    
    return Response({
        'date': date_str,
        'total_incentive': float(total_incentive),
        'collections_count': collections.count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_person_by_mobile_api(request):
    """API endpoint for getting person details by mobile number (for auto-fill)"""
    mobile = request.GET.get('mobile', '').strip()
    
    if not mobile:
        return Response(
            {'error': 'Mobile number required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        person = Person.objects.get(mobile=mobile)
        return Response({
            'found': True,
            'name': person.name,
            'mobile': person.mobile,
            'location': person.location or '',
            'area': person.area or '',
            'mail_id': person.mail_id or '',
            'training_date': person.training_date.strftime('%Y-%m-%d') if person.training_date else '',
        })
    except Person.DoesNotExist:
        return Response({
            'found': False
        })

