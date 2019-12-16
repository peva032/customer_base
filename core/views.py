from django.shortcuts import render
from core.models import (
    Customer,
    Profession,
    DataSheet,
    Document
)
from core.serializers import (
    CustomerSerializer,
    ProfessionSerializer,
    DataSheetSerializer,
    DocumentSerializer
)
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import (
        AllowAny,
        IsAdminUser,
        IsAuthenticated,
        IsAuthenticatedOrReadOnly,
        DjangoModelPermissions,
        DjangoModelPermissionsOrAnonReadOnly
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class CustomerViewSet(viewsets.ModelViewSet):

    authentication_classes = [TokenAuthentication, ]

    serializer_class = CustomerSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('name',)
    # search filters with foreign keys
    search_fields = ('name', 'address', 'data_sheet__description')
    ordering_fields = ('id', 'name') #if parsing ordering param
    ordering = ('-id')
    # lookup_field = 'name' # set the name to be default look up field

    def get_queryset(self):
        
        address = self.request.query_params.get('address', None)

        # get method always returns true for boolean
        if self.request.query_params.get('active') == 'False':
            status = False
        else:
            status = True

        if address:
            customers = Customer.objects.filter(
                address__icontains=address, active=status
            )
        else:
            # if no id or status is supplied then return all active
            customers = Customer.objects.filter(active=status)

        return customers

    # Overriding the list method for the customers endpoint

    # def list(self, request, *args, **kwargs):
    #     customers = self.get_queryset()
    #     serializer = CustomerSerializer(customers, many=True)
    #     return Response(serializer.data)

    # Overriding the request method for the customers endpoint
    def retrieve(self, request, *args, **kwargs):

        obj = self.get_object()
        serializer = CustomerSerializer(obj)
        return Response(serializer.data)

    # def create(self, request, *args, **kwargs):

    #     data = request.data
    #     customer = Customer.objects.create(
    #         name=data['name'],
    #         address=data['address'],
    #         data_sheet_id=data['data_sheet']
    #     )
    #     profession = Profession.objects.get(id=data['profession'])

    #     customer.profession.add(profession)
    #     customer.save()

    #     serializer = CustomerSerializer(customer)
    #     return Response(serializer.data)

    def update(self, request, *args, **kargs):

        customer = self.get_object()
        data = request.data
        customer.name = data['name']
        customer.address = data['address']
        customer.data_sheet_id = data['data_sheet']

        profession = Profession.objects.get(id=data['profession'])

        # first remove all professions before adding updated
        for p in customer.profession.all():
            customer.profession.remove(p)

        customer.profession.add(profession)
        customer.save()

        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):

        # if user doesn't provide a field then it will default to existing
        customer = self.get_object()
        customer.name = request.data.get('name', customer.name)
        customer.address = request.data.get('address', customer.address)
        customer.data_sheet_id = request.data.get(
            'data_sheet', customer.data_sheet_id
        )

        customer.save()
        serializer = CustomerSerializer(customer)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        
        customer = self.get_object()
        customer.delete()

        return Response('Customer Removed')

    @action(detail=True)
    def deactivate(self, request, *args, **kwargs):

        customer = self.get_object()
        customer.active = False
        customer.save()
        serializer = CustomerSerializer(customer)

        return Response(serializer.data)

    @action(detail=False)
    def deactivate_all(self, request, **kwargs):

        customers = self.get_queryset()
        customers.update(active=False)

        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def change_status(self, request, **kwargs):

        customers = self.get_queryset()
        status = True if request.data['active'] == 'True' else False
        customers.update(active=status)

        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)


class ProfessionViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAdminUser, ]
    authentication_classes = [TokenAuthentication, ]

    # standard django query, which can support filters
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer


class DataSheetViewSet(viewsets.ModelViewSet):

    permission_classes = [AllowAny, ]

    # standard django query, which can support filters
    queryset = DataSheet.objects.all()
    serializer_class = DataSheetSerializer


class DocumentViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticatedOrReadOnly, ]
    authentication_classes = [TokenAuthentication, ]

    # standard django query, which can support filters
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
