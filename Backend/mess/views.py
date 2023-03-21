from .models import Student, Meal, Menu, Announcement
from .serializer import StudentSerializer, MenuSerializer, NoticeSerializer, MealSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from django.db.models import Avg, Sum, Variance
from django.db.models.fields.files import ImageFieldFile, FileField
import H5Mess.settings as settings
import requests, random, csv, numpy as np, base64, sys, os
from django.http import HttpResponse


def get_meal_type():
    hours = datetime.now().hour
    print(hours)
    if hours in range(0, 11):
        return 'B'
    elif hours in range(11, 16):
        return 'L'
    elif hours in range(16, 19):
        return 'S'
    elif hours in range(19, 24):
        return 'D'



REGISTER = None
REGISTER_WAITING= None

LOGIN = None
LOGIN_WAITING = None

WEIGHT = [None]*settings.WEIGHT_MACHINES
WEIGHT_WAITING = [None]*settings.WEIGHT_MACHINES

@api_view(['GET'])
def ping(request):
    return Response({"I am live."})

def verify_student(rollNumber):
    print("PATH", os.path.join(sys.path[0] + "/mess/H5Students.csv"))
    hostel = np.loadtxt(os.path.join(sys.path[0] + "/mess/H5Students.csv"), delimiter=",", dtype=str)
    if str(rollNumber) in hostel:
        return True
    else:
        return False

@api_view(['GET'])
def reset_all(request):
    global REGISTER
    global REGISTER_WAITING
    global LOGIN
    global LOGIN_WAITING
    global WEIGHT
    global WEIGHT_WAITING
    REGISTER, REGISTER_WAITING, LOGIN, LOGIN_WAITING = None, None, None, None
    WEIGHT, WEIGHT_WAITING = [None]*settings.WEIGHT_MACHINES, [None]*settings.WEIGHT_MACHINES 
    return Response({"all reset"})


@api_view(['POST'])
def fill_data(request, call):
    if call == "uniform":
        for key, value in request.data.items():
            for each in Student.objects.all():
                for day in range(len(value)):
                    weight = value[len(value)-day-1]/len(Student.objects.all())
                    if not Meal.objects.filter(student=each, date=datetime.today()-timedelta(days=day), type=key).exists():
                        meal = Meal(student=each, date=datetime.today(
                        )-timedelta(days=day), type=key, weight=weight)
                        meal.save()
    elif call == "random":
        days = int(request.data.get("days"))
        for each in Student.objects.all():
            for day in range(days):
                for key in ['B', 'L', 'S', 'D']:
                    weight = random.randint(10, 75)
                    if not Meal.objects.filter(student=each, date=datetime.today()-timedelta(days=day), type=key).exists():
                        meal = Meal(student=each, date=datetime.today(
                        )-timedelta(days=day), type=key, weight=weight)
                        meal.save()
    return Response(status=status.HTTP_201_CREATED)


@api_view(['GET'])
def map_export(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    for students in Student.objects.all().values_list('rollNumber', 'RFID'):
        writer.writerow(students)

    response['Content-Disposition'] = 'attachment; filename="students_reg.csv'
    return response



@api_view(['GET'])
def verify_network(request):
    return Response({"name": "H5Mess"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def cancel_request(request):
    global REGISTER_WAITING
    REGISTER_WAITING = None
    return Response({}, status=status.HTTP_200_OK)


@api_view(['POST'])
def sso_login(request):
    access_code = request.data.get("access_code")
    print("ACCESS CODE", access_code)
    token_exchange_response = requests.post(url=settings.TOKEN_EXCHANGE_URL,
                                            headers={
                                                "Authorization": "Basic {}".format(base64.b64encode("{}:{}".format(settings.CLIENT_ID, settings.CLIENT_SECRET).encode('ascii')).decode('ascii')),
                                                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                                            },
                                            data="code={}&redirect_uri={}&grant_type=authorization_code".format(access_code, settings.REDIRECT_URI),)
    token_exchanage = token_exchange_response.json()
    print("TOKEN EXCHANGE RESPONSE", token_exchanage)
    access_token = token_exchanage.get("access_token")
    resources_response = requests.get(url=settings.RESOURCES_URL, headers={
        "Authorization": "Bearer {}".format(access_token),
    },)
    resources = resources_response.json()
    print(resources)
    roll_number = resources.get("roll_number")
    if (verify_student(roll_number)):
        name = "{} {}".format(resources.get("first_name"), resources.get("last_name"))
        student, _ = Student.objects.get_or_create(name=name, rollNumber=roll_number)
        result = StudentSerializer(student, context={"request": request})
        return Response(result.data)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def demo_login(request):
    if (request.data.get("username") == "FullAccessDemo" and request.data.get("Password") == "testing@HighFive"):
        student, _ = Student.objects.get_or_create(rollNumber="200000000", name="Demo User")
        student.save()
        result = StudentSerializer(student, context={"request": request})
        return Response(result.data)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def update(request):
    rollNumber = request.data.get("rollNumber")
    roomNumber = request.data.get("roomNumber")
    alias = request.data.get("alias")
    print(rollNumber, roomNumber, alias)
    student = Student.objects.get(rollNumber=rollNumber)
    student.roomNumber = roomNumber
    student.alias = alias
    if len(dict(request.FILES)) > 0 and "file" in dict(request.FILES).keys():
        print("CONTAINS IMAGE")
        student.photo = request.FILES["file"]
        student.permission = "A"
    student.save()
    return Response({
        "messge": "Updated successfully",
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def manual(request):
    global REGISTER_WAITING
    name = request.data.get("Name")
    rollNumber = request.data.get("Roll Number")
    roomNumber = request.data.get("Room Number")
    alias = request.data.get("Alias")
    print(rollNumber, roomNumber, alias)
    if (verify_student(rollNumber)):
        student, created = Student.objects.get_or_create(rollNumber=rollNumber, roomNumber = roomNumber, alias=alias, name=name)
        if len(dict(request.FILES)) > 0 and "Photo" in dict(request.FILES).keys():
            print("CONTAINS IMAGE")
            student.photo = request.FILES["Photo"]
            student.permission = "A"
            student.save()
            REGISTER_WAITING = request.data.get("Roll Number")
        return Response({
            "messge": "Updated successfully",
        }, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET'])
def get_student(request):
    roll_number = request.headers.get("rollNumber")
    if Student.objects.filter(rollNumber=roll_number).exists():
        student = Student.objects.get(rollNumber=roll_number)
        meal_data = {}
        if Meal.objects.filter(student=student, date=datetime.today(), type=get_meal_type()).exists():
            meal_obj = Meal.objects.get(
                student=student, date=datetime.today(), type=get_meal_type())
            meal = MealSerializer(meal_obj)
            meal_data = meal.data
        result = StudentSerializer(student, context={"request": request})
        return Response({"student": result.data, "meal": meal_data}, status=status.HTTP_200_OK)
    else:
        return Response({"message": "No student with the matching roll number"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PATCH'])
def register(request, rfid_pin):
    global REGISTER
    global REGISTER_WAITING
    if request.method == 'GET':
        if rfid_pin == "pin":
            REGISTER = request.GET["code"]
            return Response(status=status.HTTP_202_ACCEPTED)
        elif rfid_pin == "card":
            if (REGISTER_WAITING != None) and (Student.objects.get(rollNumber=REGISTER_WAITING).RFID == None):
                student = Student.objects.get(rollNumber=REGISTER_WAITING)
                student.RFID = request.GET["rfid"]
                student.save()
                REGISTER_WAITING = None
                return Response(status=status.HTTP_423_LOCKED)
            else:
                return Response(status=status.HTTP_304_NOT_MODIFIED)
        elif rfid_pin == "confirm":
            if REGISTER_WAITING != None:
                return Response(REGISTER_WAITING, status=status.HTTP_302_FOUND)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def login(request, rfid_pin):
    global LOGIN
    global LOGIN_WAITING
    if request.method == 'GET':
        if rfid_pin == "pin":
            LOGIN = request.GET["code"]
            return Response(status=status.HTTP_202_ACCEPTED)

        elif rfid_pin == "recognise":
            try:
                RFID = request.GET["rfid"]
            except:
                RFID = None
            if (RFID != None):
                try:
                    student = Student.objects.get(RFID=RFID)
                    if (student.permission == 'NA'):
                        return Response(student.alias, status=status.HTTP_403_FORBIDDEN)
                    elif (Meal.objects.filter(student=student, type=get_meal_type(), date=datetime.now().date()).exists()):
                        return Response(student.alias, status=status.HTTP_208_ALREADY_REPORTED)
                    else:
                        meal = Meal(student=student, type=get_meal_type(),
                                    weight=None, date=datetime.now().date())
                        meal.save()
                        return Response(student.alias, status=status.HTTP_201_CREATED)
                except Student.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            elif (LOGIN_WAITING != None):
                name = LOGIN_WAITING
                LOGIN_WAITING = None
                return Response(name, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def weight(request, rfid_pin):
    global WEIGHT
    global WEIGHT_WAITING
    if request.method == 'GET':
        if rfid_pin == "pin":
            code = request.GET["code"]
            i = int((int(code)-1000)/int(9000/settings.WEIGHT_MACHINES))
            print(i)
            print(code)
            WEIGHT[i] = code
            return Response(status=status.HTTP_202_ACCEPTED)
        elif rfid_pin == "recognise":
            index = int(request.GET["index"])
            try:
                RFID = request.GET["rfid"]
            except:
                RFID = None
            if RFID != None:
                try:
                    student = Student.objects.get(RFID=RFID)
                    try:
                        meal = Meal.objects.get(student__RFID=RFID, type=get_meal_type(), date=datetime.now().date())
                        if (meal.weight == None):
                            WEIGHT_WAITING[index] = student.rollNumber
                            return Response(student.alias, status=status.HTTP_202_ACCEPTED)
                        else:
                            return Response(student.alias, status=status.HTTP_405_METHOD_NOT_ALLOWED)
                    except Meal.DoesNotExist:
                        return Response(student.alias, status=status.HTTP_206_PARTIAL_CONTENT)
                except Student.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            elif WEIGHT_WAITING[index] != None:
                return Response(Student.objects.get(rollNumber=WEIGHT_WAITING[index]).alias, status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

        elif rfid_pin == "update":
            index = int(request.GET["index"])
            try:
                weight = request.GET["weight"]
            except:
                weight = None
            print(weight)
            if weight is None:
                WEIGHT_WAITING[index] = None
                return Response(status=status.HTTP_205_RESET_CONTENT)
            elif WEIGHT_WAITING[index] != None:
                rollNumber = WEIGHT_WAITING[index]
                student = Student.objects.get(rollNumber=rollNumber)
                meal = Meal.objects.get(student=student, type=get_meal_type(), date=datetime.today())
                WEIGHT_WAITING[index] = None
                if (get_meal_type() in ['B', 'S']):
                    meal.weight = str(int(weight))
                elif (get_meal_type() in ['L', 'D']):
                    meal.weight = str(int(weight))
                meal.save()
                return Response(student.alias, status=status.HTTP_423_LOCKED)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def app(request, call):
    global REGISTER_WAITING
    global LOGIN_WAITING
    global WEIGHT_WAITING
    if request.method == 'GET':
        if call == "meal":
            rollNumber = request.headers.get("rollNumber")
            student = Student.objects.get(rollNumber=rollNumber)
            if Meal.objects.filter(student=student, type=get_meal_type(), date=datetime.today()).exists():
                meal = Meal.objects.get(
                    student=student, type=get_meal_type(), date=datetime.today())
                result = MealSerializer(meal)
                return Response({
                    "message": result.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Not Found"}, status=status.HTTP_204_NO_CONTENT)

        elif call == "status":
            id = int(request.headers.get("id"))
            if Meal.objects.filter(id=id).exists():
                meal = Meal.objects.get(id=id)
                result = MealSerializer(meal)
                return Response({
                    "message": result.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "message": "No meal with this id"
                }, status=status.HTTP_204_NO_CONTENT)

        elif call == "menu":
            menu = Menu.objects.all()
            serializer = MenuSerializer(menu, many=True)
            return Response(serializer.data)

        elif call == "notices":
            notices = Announcement.objects.filter(display=True)
            serializer = NoticeSerializer(notices, many=True)
            return Response(serializer.data)

        elif len(call) == 9:
            try:
                student = Student.objects.get(rollNumber=call)
            except Student.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = StudentSerializer(student)
            return Response(serializer.data)

    elif request.method == "POST":
        if call == "validate":
            print(request.data)
            if request.data.get("machine") == "register":
                if REGISTER == request.data.get("code"):
                    REGISTER_WAITING = request.data.get("rollNumber")
                    return Response(status=status.HTTP_202_ACCEPTED)
                else:
                    return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
            elif (request.data.get("machine") == "login"):
                if LOGIN == request.data.get("code"):
                    try:
                        student = Student.objects.get(rollNumber=request.data.get("rollNumber"))
                        if (student.permission == 'NA'):
                            return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
                        elif (Meal.objects.filter(student=student, type=get_meal_type(), date=datetime.now().date()).exists()):
                            return Response({"message": "Meal Already Taken"}, status=status.HTTP_208_ALREADY_REPORTED)
                        else:
                            meal = Meal(student=student, type=get_meal_type(), weight=None, date=datetime.now().date())
                            meal.save()
                            result = MealSerializer(meal)
                            LOGIN_WAITING = student.alias
                            return Response({"message": result.data}, status=status.HTTP_201_CREATED)
                    except Student.DoesNotExist:
                        return Response(status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
            elif (request.data.get("machine") == "weight"):
                code = request.data.get("code")
                index = int((int(code)-1000)/int(9000/settings.WEIGHT_MACHINES))
                print(index)
                rollNumber = request.data.get("rollNumber")
                if WEIGHT[index] == code:    
                    try:
                        student = Student.objects.get(rollNumber=rollNumber)
                        try:
                            meal = Meal.objects.get(
                                student=student, type=get_meal_type(), date=datetime.now().date())
                            if (meal.weight is None):
                                WEIGHT_WAITING[index] = rollNumber
                                return Response(status=status.HTTP_202_ACCEPTED)
                            else:
                                return Response(student.name, status=status.HTTP_405_METHOD_NOT_ALLOWED)
                        except Meal.DoesNotExist:
                            return Response(student.name, status=status.HTTP_206_PARTIAL_CONTENT)
                    except Student.DoesNotExist:
                        return Response(status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


        if call == "newStudent":
            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def arena(request, call):
    today = datetime.today()
    if request.method == 'GET':
        upto = request.data.get("upto")
        interval = request.data.get("interval")
        upto = upto if upto != None else today
        interval = interval if interval != None else "0"
        end = datetime(
            int(upto.split("/")[0]), int(upto.split("/")[1]), int(upto.split("/")[2]))
        start = end - timedelta(days=int(interval))
        mealtype = request.data.get("type")
        student = request.data.get("rollNumber")
        operation = request.data.get("operation")
        N = request.data.get("N")
        if call == "dateTotal":
            return Response(total_day_waste(start, end, mealtype))
        elif call == "dateAvg":
            return Response(average_day_waste(start, end, mealtype))
        # elif call == "dateVar":
        #     return Response(variance_date_waste(start, end, mealtype))
        elif call == "movingAvg":
            return Response(moving_avg_waste(start, end, mealtype))
        elif call == "myStats":  # datewise wastage
            return Response(student_days_total(student, start, end, mealtype, operation))
        elif call == "percentile":  # percentile among low wastage
            return Response(percentile(student, mealtype))
        elif call == "topN":  # leaderboard
            return Response(top_N_scorers(N, start, end, mealtype))


# OVERALL STATISTICS API CALLS

def total_day_waste(start, end, type=None):
    if type == None:
        return Meal.objects.filter(date__range=[start, end]).aggregate(Sum("weight"))
    else:
        return Meal.objects.filter(date__range=[start, end], type=type).aggregate(Sum("weight"))


def average_day_waste(start, end, type=None):
    if type == None:
        return Meal.objects.filter(date__range=[start, end]).aggregate(Avg("weight"))
    else:
        return Meal.objects.filter(date__range=[start, end], type=type).aggregate(Avg("weight"))


def variance_date_waste(start, end, type=None):
    if type == None:
        return Meal.objects.filter(date__range=[start, end]).aggregate(Variance("weight"))
    else:
        return Meal.objects.filter(date__range=[start, end], type=type).aggregate(Variance("weight"))


def moving_avg_waste(start, end, type=None):
    if type == None:
        return Meal.objects.filter(date__range=[start, end]).aggregate(Avg("weight"))
    else:
        return Meal.objects.filter(date__range=[start, end], type=type).aggregate(Avg("weight"))



@api_view(["GET"])
def day_summary(request):
    start = datetime.fromisoformat(request.headers.get("start"))
    end = datetime.fromisoformat(request.headers.get("end"))
    type = request.headers.get("type")
    print(start, end, type)
    average = average_day_waste(start, end)
    variance = 0.0
    total = total_day_waste(start, end)
    data = []
    date = start
    while(date <= end):
        day = Meal.objects.filter(date=date)
        sum = 0
        for meal in day:
            if(meal.weight is None):
                pass
            else:
                sum += float(meal.weight)
        data.append([date, sum])
        date += timedelta(days=1)
    return Response({
        "total": total["weight__sum"],
        "average": average["weight__avg"],
        "data": data
    },)

@api_view(["GET"])
def day_summary_average(request):
    start = datetime.fromisoformat(request.headers.get("start"))
    end = datetime.fromisoformat(request.headers.get("end"))
    type = request.headers.get("type")
    print(start, end, type)
    average = average_day_waste(start, end)
    variance = 0.0
    total = total_day_waste(start, end)
    data = []
    date = start
    while(date <= end):
        day = Meal.objects.filter(date=date)
        sum = 0
        num = 0
        for meal in day:
            num += 1
            if(meal.weight is None):
                pass
            else:
                sum += float(meal.weight)
        avg = 0
        if(num!=0):
            avg = sum/num
        data.append([date, avg])
        date += timedelta(days=1)
    return Response({
        "total": total["weight__sum"],
        "average": average["weight__avg"],
        "data": data
    },)

# INDIVIDUAL STATISTICS API CALLS


@api_view(['GET'])
def day_details(request):
    rollNumber = request.headers.get("rollNumber")
    print('roll_number', rollNumber)
    student = Student.objects.get(rollNumber=rollNumber)
    data = [x["date"] for x in Meal.objects.filter(
        student=student).values('date').distinct()]
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def day_data(request):
    rollNumber = request.headers.get("rollNumber")
    date = request.headers.get("date")
    student = Student.objects.get(rollNumber=rollNumber)
    meals = Meal.objects.filter(student=student, date=date)
    result = MealSerializer(meals, many=True)
    return Response({"data": result.data}, status=status.HTTP_200_OK)

# returns total food wasted for last x days upto given date "upto"


def student_days_total(RL, start, end, type=None, operation="Sum"):
    if RL == None:
        return status.HTTP_400_BAD_REQUEST
    if type == None:
        meals = Meal.objects.filter(
            student__rollNumber=RL, date__range=[start, end])
        if operation == "Sum":
            return meals.aggregate(Sum("weight"))
        elif operation == "Avg":
            return meals.aggregate(Avg("weight"))
    else:
        meals = Meal.objects.filter(
            student__rollNumber=RL, type=type, date__range=[start, end])
        if operation == "Sum":
            return meals.aggregate(Sum("weight"))
        elif operation == "Avg":
            return meals.aggregate(Avg("weight"))


def percentile(id, type=None):
    students = Meal.objects.all().values('student_id').annotate(
        Avg("weight")).order_by("weight__avg")
    totalstudents = students.count()
    myavg = students.filter(student_id=id).values_list("weight__avg")
    studentswithmorewaste = students.filter(weight__avg__gte=myavg).count()

    percentile = (studentswithmorewaste)*100.0/totalstudents

    return percentile


def top_N_scorers(N, start, end, type=None):
    if type == None:
        leaders = Meal.objects.filter(date__range=[start, end]).values(
            'student__rollNumber', "student__name").annotate(Avg("weight")).order_by("weight__avg")
    else:
        leaders = Meal.objects.filter(date__range=[start, end], type=type).values(
            'student__rollNumber').annotate(Avg("weight")).order_by("weight__avg")

    N = len(leaders) if N == None else min(len(leaders), int(N))

    for each in range(N):
        del leaders[each]["student__rollNumber"]

    return leaders[:N]


@api_view(['POST'])
def create_test_users(request):
    for i in range(1, 11):
        name = "Person " + str(i)
        alias = "Person" + str(i)
        rollNumber = "20002000" + str(i)
        roomNumber = str(i)
        RFID = "1000000"+str(i)
        photo = ImageFieldFile(
            instance=None, field=FileField(), name='/photos/test.jpg')
        student, _ = Student.objects.update_or_create(
            name=name, alias=alias, roomNumber=roomNumber, rollNumber=rollNumber, photo=photo, permission="A", RFID=RFID)
        student.save()
    return Response({})


@api_view(['POST'])
def create_test_meals(request):
    for i in range(1, 11):
        rollNumber = "20002000" + str(i)
        student = Student.objects.get(rollNumber=rollNumber)
        for i in range(1, 7):
            breakfast = Meal.objects.create(
                student=student, type="B", date=datetime.today()-timedelta(days=(i)), weight=random.randint(10, 75))
            breakfast.save()
            lunch = Meal.objects.create(
                student=student, type="L", date=datetime.today()-timedelta(days=(i)), weight=random.randint(40, 120))
            lunch.save()
            snack = Meal.objects.create(
                student=student, type="S", date=datetime.today()-timedelta(days=(i)), weight=random.randint(5, 100))
            snack.save()
            dinner = Meal.objects.create(
                student=student, type="D", date=datetime.today()-timedelta(days=(i)), weight=random.randint(10, 150))
            dinner.save()
    return Response({})
