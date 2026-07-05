# SOLID principles

## 1. S - Single Responsibility Principle (SRP)
A class should have only one reason to change.
A class should do one job

Bad:
```python
class OrderView(APIView):
    def post(self, request):
        # validate request
        # calculate prices
        # create order
        # send email
        # create invoice
        # notify warehouse
        # analytics
```

This view is responsible for:

* validation
* business logic
* persistence
* notifications
* analytics

Too many responsibilities.

Better:
```
View
    ↓
OrderService [which contains business logic]
    ↓
Repositories / Models [which do the DB calls]
    ↓
EmailService
InvoiceService
WarehouseService
AnalyticsService
```

## 2. O - Open/Closed Principle (OCP)
Open for extension but closed for modification.
Instead of changing existing code repeatedly, extend it.

Bad:
```python
class DiscountService:

    def calculate(self, user):

        if user.type == "gold":
            return 20

        elif user.type == "silver":
            return 10

        elif user.type == "platinum":
            return 30
```

Good:
```python
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):

    @abstractmethod
    def discount(self):
        pass

class GoldDiscount(DiscountStrategy):

    def discount(self):
        return 20

class SilverDiscount(DiscountStrategy):

    def discount(self):
        return 10
```

Adding Platinum requires a new class, not changing existing logic.

## 3. L - Liskov Substituition Principle (LSP)
Subclasses should be replaceable with their parent class.

Suppose:
```python
class Notification:

    def send(self):
        ... -> {"status": "sent"}

class EmailNotification(Notification):

    def send(self):
        ... -> {"done": True}

class SMSNotification(Notification):

    def send(self):
        ... -> bool
```

Anywhere expecting Notification should work.

Violation:
```python
class FakeNotification(Notification):

    def send(self):
        raise Exception("Can't send")
```


## 4. I - Interface Segregation Principle (ISP)
Don't force clients to depend on the methods that they don't use.

Suppose:
```python
class Animal:

    def fly(self):
        ...

    def swim(self):
        ...

    def walk(self):
        ...
```

Fishes don't fly.
Birds don't swim inside the water.
Fishes don't walk.
This is bad abstraction.

Instead do this:
```python
class Flyable

class Swimmable

class Walkable
```

Another example:<br>
<b>Bad</b>

```python
class UserService:

    def login()

    def logout()

    def reset_password()

    def upload_avatar()

    def delete_account()

    def generate_report()

    def send_newsletter()
```

Instead:
```python
AuthenticationService

ProfileService

ReportingService

NewsletterService
```

## 5. D - Dependency Inversion Principle (DIP)
Depend on abstractions, not concrete implementations.

Suppose:
```python
class OrderService:

    def create(self):
        EmailService().send()
```

Problem: OrderService is tightly coupled with EmailService.

Better:
```python
class NotificationService(ABC):

    @abstractmethod
    def send(self):
        pass

class EmailService(NotificationService):

    def send(self):
        ...  

class OrderService:

    def __init__(self, notifier):
        self.notifier = notifier

    def create(self):
        self.notifier.send()

service = OrderService(EmailService())
```


# A Real Django Architecture Following SOLID
```
project/

orders/

    models.py

    views.py

    serializers.py

    services/
        order_service.py
        pricing_service.py
        payment_service.py

    repositories/
        order_repository.py

    notifications/
        email_service.py
        sms_service.py

    permissions.py

    selectors/
        order_selector.py

    tasks.py
```