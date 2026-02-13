"""
Sample Data Setup for 2moreFitness
Run this after migrations: python manage.py shell < setup_sample_data.py
"""

from django.contrib.auth.models import User
from apps.core.models import UserProfile, MembershipPlan
from apps.trainers.models import Trainer
from apps.classes.models import GymClass
from apps.members.models import Member, Membership
from datetime import datetime, timedelta, time

print("Creating sample data for 2moreFitness...")

# Create Membership Plans
print("Creating membership plans...")
plans_data = [
    {
        'name': 'Monthly Basic',
        'description': 'Perfect for getting started with your fitness journey',
        'duration': 'monthly',
        'price': 2500.00,
        'features': '''Full gym access
Group classes included
Locker room facilities
Free WiFi'''
    },
    {
        'name': 'Quarterly Premium',
        'description': 'Our most popular choice for committed members',
        'duration': 'quarterly',
        'price': 6500.00,
        'features': '''Everything in Monthly Basic
Free fitness assessment
Nutrition guidance
Priority class booking
10% discount on merchandise'''
    },
    {
        'name': 'Annual Elite',
        'description': 'Best value package for serious fitness enthusiasts',
        'duration': 'annual',
        'price': 20000.00,
        'features': '''Everything in Quarterly Premium
4 personal training sessions per month
Free gym merchandise
Guest pass privileges
Priority equipment access
Complimentary sports massage (monthly)'''
    }
]

for plan_data in plans_data:
    MembershipPlan.objects.get_or_create(
        name=plan_data['name'],
        defaults=plan_data
    )

print(f"Created {len(plans_data)} membership plans")

# Create sample trainers
print("Creating trainers...")
trainers_data = [
    {
        'username': 'trainer_mike',
        'email': 'mike@2morefitness.ph',
        'first_name': 'Mike',
        'last_name': 'Johnson',
        'specialization': 'Strength Training & Bodybuilding',
        'bio': 'Certified strength coach with 10 years of experience in competitive bodybuilding and powerlifting.',
        'certifications': 'NSCA-CSCS\nACE Personal Trainer\nUSA Powerlifting Coach',
        'years_of_experience': 10,
        'hourly_rate': 1500.00
    },
    {
        'username': 'trainer_sarah',
        'email': 'sarah@2morefitness.ph',
        'first_name': 'Sarah',
        'last_name': 'Martinez',
        'specialization': 'Yoga & Flexibility Training',
        'bio': 'Experienced yoga instructor specializing in vinyasa flow and therapeutic yoga practices.',
        'certifications': 'RYT 500 Yoga Alliance\nYoga Therapy Certification\nPrenatal Yoga Certified',
        'years_of_experience': 8,
        'hourly_rate': 1200.00
    },
    {
        'username': 'trainer_carlos',
        'email': 'carlos@2morefitness.ph',
        'first_name': 'Carlos',
        'last_name': 'Reyes',
        'specialization': 'HIIT & Functional Fitness',
        'bio': 'High-intensity interval training expert and former competitive athlete.',
        'certifications': 'CrossFit Level 2\nACE Functional Training Specialist\nFirst Aid & CPR',
        'years_of_experience': 6,
        'hourly_rate': 1300.00
    }
]

for trainer_data in trainers_data:
    user, created = User.objects.get_or_create(
        username=trainer_data['username'],
        defaults={
            'email': trainer_data['email'],
            'first_name': trainer_data['first_name'],
            'last_name': trainer_data['last_name']
        }
    )
    if created:
        user.set_password('trainer123')
        user.save()
        
        profile = user.profile
        profile.role = 'trainer'
        profile.save()
        
        Trainer.objects.create(
            user=user,
            specialization=trainer_data['specialization'],
            bio=trainer_data['bio'],
            certifications=trainer_data['certifications'],
            years_of_experience=trainer_data['years_of_experience'],
            hourly_rate=trainer_data['hourly_rate']
        )

print(f"Created {len(trainers_data)} trainers")

# Create sample classes
print("Creating gym classes...")
trainers = list(Trainer.objects.all())

classes_data = [
    {'name': 'Morning Strength', 'trainer': trainers[0], 'difficulty': 'intermediate', 
     'duration': 60, 'day_of_week': 'monday', 'time': time(6, 0),
     'description': 'Build strength with compound movements and progressive overload'},
    {'name': 'Power Yoga', 'trainer': trainers[1], 'difficulty': 'beginner', 
     'duration': 45, 'day_of_week': 'monday', 'time': time(18, 0),
     'description': 'Dynamic yoga flow to build strength and flexibility'},
    {'name': 'HIIT Bootcamp', 'trainer': trainers[2], 'difficulty': 'advanced', 
     'duration': 45, 'day_of_week': 'tuesday', 'time': time(17, 0),
     'description': 'High-intensity circuit training for maximum calorie burn'},
    {'name': 'Beginner Strength', 'trainer': trainers[0], 'difficulty': 'beginner', 
     'duration': 60, 'day_of_week': 'wednesday', 'time': time(10, 0),
     'description': 'Learn proper form and technique for fundamental exercises'},
    {'name': 'Vinyasa Flow', 'trainer': trainers[1], 'difficulty': 'intermediate', 
     'duration': 60, 'day_of_week': 'wednesday', 'time': time(19, 0),
     'description': 'Flowing sequences synchronized with breath'},
    {'name': 'CrossFit WOD', 'trainer': trainers[2], 'difficulty': 'advanced', 
     'duration': 60, 'day_of_week': 'thursday', 'time': time(6, 30),
     'description': 'Workout of the day featuring Olympic lifts and metabolic conditioning'},
]

for class_data in classes_data:
    GymClass.objects.get_or_create(
        name=class_data['name'],
        day_of_week=class_data['day_of_week'],
        time=class_data['time'],
        defaults=class_data
    )

print(f"Created {len(classes_data)} gym classes")

# Create a demo member
print("Creating demo member...")
demo_user, created = User.objects.get_or_create(
    username='demo_member',
    defaults={
        'email': 'demo@2morefitness.ph',
        'first_name': 'Demo',
        'last_name': 'Member'
    }
)

if created:
    demo_user.set_password('demo123')
    demo_user.save()
    
    profile = demo_user.profile
    profile.role = 'member'
    profile.phone = '09171234567'
    profile.address = '123 Fitness St., Quezon City'
    profile.save()
    
    member = Member.objects.create(
        user=demo_user,
        gender='M',
        height=175.0,
        weight=70.0,
        fitness_goals='Build muscle and improve overall fitness'
    )
    
    # Create active membership for demo member
    plan = MembershipPlan.objects.filter(duration='quarterly').first()
    if plan:
        Membership.objects.create(
            member=member,
            plan=plan,
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=90)).date(),
            status='active',
            payment_status='paid',
            payment_amount=plan.price,
            payment_date=datetime.now().date(),
            payment_reference='SAMPLE001'
        )

print("✓ Sample data created successfully!")
print("\nDefault credentials:")
print("Admin: Create using 'python manage.py createsuperuser'")
print("Demo Member: username=demo_member, password=demo123")
print("Trainer Mike: username=trainer_mike, password=trainer123")
print("Trainer Sarah: username=trainer_sarah, password=trainer123")
print("Trainer Carlos: username=trainer_carlos, password=trainer123")
