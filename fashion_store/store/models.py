from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
	userCustomer = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	nameCustomer = models.CharField(max_length=200, null=True)
	emailCustomer = models.EmailField(max_length=200, unique=True)

	def __str__(self):
		return "{} - {} ({})".format(self.emailCustomer, self.nameCustomer, self.userCustomer)

class Category(models.Model):
	nameCategory = models.CharField(max_length=50, unique=True)

	def __str__(self):
		return "{}".format(self.nameCategory)

class Product(models.Model):
	nameProduct = models.CharField(max_length=50)
	priceProduct = models.FloatField()
	digitalProduct = models.BooleanField(default=False)
	imageProduct = models.ImageField(upload_to='products/', default='products/640x360.png')
	categoryProduct = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
	descriptionProduct = models.TextField(max_length=1000, default="Description")

	def __str__(self):
		return "{} - Rp.{}".format(self.nameProduct, self.priceProduct)

	@property
	def imageURL(self):
		try:
			url = self.imageProduct.url
		except:
			url = ''
		return url

class Order(models.Model):
	customerOrder = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	dateOrder = models.DateTimeField(auto_now_add=True)
	completeOrder = models.BooleanField(default=False)
	transactionOrder = models.CharField(max_length=100, null=True)
	totalOrder = models.FloatField(default=0, null=True)
	totalProductOrder = models.IntegerField(null=True, default=0)

	def __str__(self):
		return "{}: {}".format(self.transactionOrder, self.totalOrder)

	@property
	def getCartTotal(self):
		orderItems = self.orderitem_set.all()
		totalCart = sum([item.getOrderTotal for item in orderItems])
		return totalCart
	
	@property
	def getCartItems(self):
		orderItems = self.orderitem_set.all()
		totalCartItems = sum([item.quantityOrdered for item in orderItems])
		return totalCartItems

	@property
	def getShipping(self):
		allowedShipping = False
		orderItems = self.orderitem_set.all()
		for i in orderItems:
			if i.productOrdered.digitalProduct == False:
				allowedShipping = True
		return allowedShipping

class OrderItem(models.Model):
	productOrdered = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	itemOrdered = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantityOrdered = models.IntegerField(default=0, null=True, blank=True)
	dateOrdered = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "{} - {}".format(self.id, self.itemOrdered)
	
	@property
	def getOrderTotal(self):
		totalOrdered = self.productOrdered.priceProduct * self.quantityOrdered
		return totalOrdered

class Payment(models.Model):
	transactionId = models.CharField(max_length=100, null=True)
	pricePayment = models.FloatField(default=0, null=True)
	statusPayment = models.CharField(max_length=50, null=True)
	methodPayment = models.CharField(max_length=100, null=False)
	datePayment = models.DateTimeField(auto_now_add=True)
	completePayment = models.BooleanField(default=False)

	def __str__(self):
		return "{}. {} - {} Rp.{}".format(self.id, self.transactionId, self.statusPayment, self.pricePayment)

class ShippingAddress(models.Model):
	customerOrder = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	itemOrdered = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	paymentOrder = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
	nameShipping = models.CharField(max_length=70, null=False)
	addressShipping = models.CharField(max_length=200, null=False)
	cityShipping = models.CharField(max_length=100, null=False)
	stateShipping = models.CharField(max_length=100, null=False)
	zipcodeShipping = models.CharField(max_length=20, null=False)
	countryShipping = models.CharField(max_length=50, null=False, default="Indonesia")
	phoneShipping = models.CharField(max_length=20, null=False)
	emailShipping = models.EmailField(max_length=150, null=False)
	dateShipping = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "{}. {}".format(self.id, self.itemOrdered)

class Testimonials(models.Model):
	nameTestimonials = models.CharField(max_length=100, null=True)
	imageTestimonials = models.ImageField(upload_to='testimonials/', default='testimonials/testimonials.png')
	messageTestimonials = models.TextField(max_length=200, null=True)

	def __str__(self):
		return "{}".format(self.nameTestimonials)

	@property
	def imageTesti(self):
		try:
			url = self.imageTestimonials.url
		except:
			url = ''
		return url

class OrderSummary(ShippingAddress):
	class Meta:
		proxy = True
		verbose_name = 'Order Summary'
		verbose_name_plural = 'Order Summary'