### Steps for LLD:
1. Think about what Models you need.
2. What kind of DB relations we need.
3. What kind of DB calls you need. - Repository (is a class that contains DB calls)
4. What features do we want and write its code - Service (is a class that contains business logic)
5. What APIs do we need. - Views

GET /search_movie?theatreId=<some-id>

GET /serach_theatre?movieId=<some-id>&languageId=<some-id>


## Composition over Inheritance
Instead of creating lange inheritance hierarchies, build objects by combining smaller objects.

Inheritance tightly couples subclasses to parent implementation
But Composotion allows objects to be swapped independently.


```python
class Bird:
  def eat(self):
    print("Eating")

class FlyingBird(Bird):
  def fly(self):
    print("Flying")

class Penguin(FlyingBird):
  pass
```
```python
penguin = Penguin()
penguin.fly() #flying
```

```python
class FlyBehavior:
  # more fields
  def fly(self):
    print("Flying")

class NoFlyBehavior:
  # more fields
  def fly(self):
    print("Cannot fly")

class Bird:
  def __init__(self, fly_behavior):
    self.fly_behavior = fly_behavior

  def fly(self):
    self.fly_behavior.fly()

eagle = Bird(FlyBehavior())
penguin = Bird(NoFlyBehavior())

eagle.fly()
penguin.fly()
```


Instead of using:
```python
class BasePaymentGateway:
    ...

class RazorpayGateway(BasePaymentGateway):
    ...

class StripeGateway(BasePaymentGateway):
    ...
```

We can use:
```python
class PaymentService:

    def __init__(self, gateway):
        self.gateway = gateway

    def pay(self, amount):
        self.gateway.charge(amount)
```

## Managing dependencies and coupling

<b>What is a dependency?</b>
If class A uses class B, then A depends on B.

Example:
```python
class OrderService:

    def place_order(self):
        payment = StripePayment()
        payment.pay()
```

Problem: `OrderService` is tightly coupled with `StripePayment` and thus. we cannot change the payment gateway without change the code of `place_order`

<b>We need Loose Coupling:</b>

```python
class OrderService:

    def __init__(self, payment):
        self.payment = payment

    def place_order(self):
        self.payment.pay()
```

<b>Dependency Injection</b>
Instead of creating dependencies, like:
```payment = StripePayment()```

We will do:
```service = OrderService(StripePayment())```

## Designing for change and extension

Bad:
```python
if payment_type == "stripe":
    ...

elif payment_type == "paypal":
    ...

elif payment_type == "razorpay":
    ...
```

Every new payment gateway modifies this code.

Violates Open/Closed Principle.

Better:
```python
class PaymentGateway:

    def pay(self):
        pass

class StripeGateway(PaymentGateway):
    ...

class RazorpayGateway(PaymentGateway):
    ...

class PaypalGateway(PaymentGateway):
    ...
```

## Recognizing and fixing bad designs

1. God Class: One class that does everything.

```
UserService

- create user
- login
- send email
- upload image
- analytics
- payment
- notifications
```

Thousands of lines of code. Its better to split into separate classes that specialise in 1 kind of job.

Ex: Split into:
```
UserService
EmailService
ImageService
PaymentService
AnalyticsService
```

2. Long Methods:
Such methods usually contain too many responsibilities.
```python
def process_order()
  # 400 lines
```

Better: Break into smaller methods
```
validate()

calculate()

save()

notify()
```

3. Massive if-else chains
4. Duplicate Code
5. Tight Coupling
6. Primitive Obssession:
Don't use strings everywhere.

Bad:
```python
status = "PAID"
status = "CANCELLED"
status = "FAILED"
```

Better:
```python
from enum import Enum

class OrderStatus(Enum):
    PAID = "paid"
    FAILED = "failed"
```