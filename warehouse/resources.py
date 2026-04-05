from import_export import resources,fields
from Product.models import Product

class ProductResource(resources.ModelResource):
    wh_stock = fields.Field(attribute='wh_stock')
    class Meta:
        model = Product
        exclude = ('post', )
        fields = ('ProductName','Barcode','Tag','Minimum')
        export_order = ('ProductName','Barcode','Tag','Minimum')

