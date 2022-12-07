from udemy.apps.course.models import Course
from udemy.apps.course.serializer import CourseSerializer


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = []
        self.cart = cart

    def to_representation(self):
        course_annotations = Course.get_annotations('avg_rating', 'num_subscribers')
        courses_ids = self.cart
        courses = Course.objects.filter(id__in=courses_ids).annotate(**course_annotations)

        serializer = CourseSerializer(
            courses,
            many=True,
            fields=('id', 'title', 'url', 'is_paid', 'price', 'instructors', 'num_subscribers', 'avg_rating', 'created')
        )

        return serializer.data

    def add(self, course):
        course_id = course.id
        if course_id not in self.cart:
            self.cart.append(course_id)
            self.save()

    def remove(self, course):
        course_id = course.id
        if course_id in self.cart:
            self.cart.remove(course_id)
            self.save()

    def save(self):
        self.session.modified = True
