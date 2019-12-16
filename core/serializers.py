from rest_framework import serializers
from core.models import (
    Customer,
    Profession,
    DataSheet,
    Document
)


class DataSheetSerializer(serializers.ModelSerializer):

    class Meta:

        model = DataSheet
        fields = (
            'id',
            'description',
            'historical_data'
        )


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:

        model = Document
        fields = (
            'id',
            'dtype',
            'doc_number',
            'customer'
        )


class ProfessionSerializer(serializers.ModelSerializer):

    class Meta:

        model = Profession
        fields = (
            'id',
            'description'
        )


class CustomerSerializer(serializers.ModelSerializer):

    num_professions = serializers.SerializerMethodField()
    # data_sheet = serializers.StringRelatedField()
    data_sheet = DataSheetSerializer()
    profession = ProfessionSerializer(many=True)

    class Meta:

        model = Customer
        fields = (
            'id',
            'name',
            'address',
            'profession',
            'data_sheet',
            'active',
            'status_message',  # property decorator defined in model
            'num_professions'  # serializer method defined in model
        )

    def get_num_professions(self, obj):
        return obj.num_professions()

    def create(self, validated_data):

        professions = validated_data['profession']
        del validated_data['profession']

        data_sheet = validated_data['data_sheet']
        del validated_data['data_sheet']

        customer = Customer.objects.create(**validated_data)
        d_sheet = DataSheet.objects.create(**data_sheet)
        customer.data_sheet = d_sheet

        for profession in professions:

            prof = Profession.objects.create(**profession)
            customer.profession.add(prof)

        customer.save()
        return customer
