from django.db import models

class Food(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    vendor = models.CharField(max_length=50)
    isBreakfast = models.BooleanField(verbose_name='Breakfast')
    isLunch = models.BooleanField(verbose_name='Lunch')
    isDinner = models.BooleanField(verbose_name='Dinner')
    isSehri = models.BooleanField(verbose_name='Sehri')
    isAftari = models.BooleanField(verbose_name='Aftari')
    isActive = models.BooleanField(verbose_name='Active')
    
    def __str__(self):
        return self.name +' - '+ str(self.price)

class FoodOrder(models.Model):
    SERVED = 'served'
    CANCELLED = 'cancelled'
    REJECTED = 'rejected'
    PENDING = 'pending' # after approval
    PLACED = 'placed' # before approval
    
    STATUS_CHOICES = ((SERVED, 'Served'),
                      (CANCELLED, 'Cancelled'),
                      (REJECTED, 'Rejected'),
                      (PENDING, 'Pending'),
                      (PLACED, 'Placed'))
    
    food = models.ForeignKey(Food, null=True, blank=True, on_delete=models.SET_NULL)
    employee = models.ForeignKey('home.Employee', related_name='foods', null=True, blank=True, on_delete=models.SET_NULL)
    project = models.ForeignKey('home.Project', null=True, blank=True, on_delete=models.SET_NULL)
    datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=15)
    approvedBy = models.ForeignKey('home.Employee', related_name='approved_foods', null=True, blank=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.employee.name +' - '+ self.food.name +' - '+ str(self.datetime)